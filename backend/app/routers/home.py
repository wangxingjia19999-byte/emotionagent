from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.home import HomeOverviewData
from app.utils.jwt import get_current_user


router = APIRouter(tags=["首页"])

AI_SESSION_TABLES = ["ai_chat_sessions", "ai_sessions", "chat_sessions", "conversations", "dialogue_sessions"]
POST_TABLES = ["community_posts", "posts", "forum_posts"]
FAVORITE_TABLES = ["favorites", "favorite_posts", "post_favorites", "collections", "user_favorites"]
FRIEND_TABLES = ["friend_relations", "friendships", "friends", "user_friends", "friend_links"]
PRIVATE_MESSAGE_TABLES = ["private_messages", "messages", "chat_messages", "friend_messages", "direct_messages"]

USER_COLUMNS = ["user_id", "owner_id", "created_by", "uid", "author_id", "publisher_id", "sender_id"]
RECIPIENT_COLUMNS = ["recipient_id", "to_user_id", "receiver_id", "user_id", "target_user_id"]
TITLE_COLUMNS = ["title", "name", "subject", "session_title", "conversation_title"]
UPDATED_COLUMNS = ["updated_at", "last_updated_at", "last_message_at", "updated_time", "modified_at", "created_at", "create_time"]
CATEGORY_COLUMNS = ["category", "category_name", "type", "topic"]
LIKE_COLUMNS = ["like_count", "likes_count", "thumb_count", "praise_count"]
COMMENT_COLUMNS = ["comment_count", "comments_count", "reply_count"]
READ_COLUMNS = ["is_read", "read", "has_read", "read_flag", "message_read"]
STATUS_COLUMNS = ["status", "state"]


def _get_inspector(db: Session):
    return inspect(db.get_bind())


def _find_table(inspector, candidates: list[str]) -> str | None:
    existing_tables = set(inspector.get_table_names())
    for table_name in candidates:
        if table_name in existing_tables:
            return table_name
    return None


def _find_column(inspector, table_name: str, candidates: list[str]) -> str | None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    for column_name in candidates:
        if column_name in columns:
            return column_name
    return None


def _scalar_count(db: Session, sql: str, params: dict[str, Any] | None = None) -> int:
    try:
        result = db.execute(text(sql), params or {})
        value = result.scalar_one_or_none()
        return int(value or 0)
    except Exception:
        return 0


def _count_user_rows(
    db: Session,
    inspector,
    table_candidates: list[str],
    user_id: int,
    *,
    extra_filter: str | None = None,
    extra_params: dict[str, Any] | None = None,
) -> int:
    table_name = _find_table(inspector, table_candidates)
    if not table_name:
        return 0

    user_column = _find_column(inspector, table_name, USER_COLUMNS)
    if not user_column:
        return 0

    sql = f"SELECT COUNT(*) FROM `{table_name}` WHERE `{user_column}` = :user_id"
    params: dict[str, Any] = {"user_id": user_id}

    if extra_filter:
        sql += f" AND ({extra_filter})"
    if extra_params:
        params.update(extra_params)

    return _scalar_count(db, sql, params)


def _count_friends(db: Session, inspector, user_id: int) -> int:
    table_name = _find_table(inspector, FRIEND_TABLES)
    if not table_name:
        return 0

    user_column = _find_column(inspector, table_name, USER_COLUMNS)
    if not user_column:
        return 0

    status_column = _find_column(inspector, table_name, STATUS_COLUMNS)
    if status_column:
        accepted_values = ["accepted", "approved", "confirmed", "friend", "active", "normal"]
        status_placeholders = ", ".join(f":status_{index}" for index in range(len(accepted_values)))
        sql = (
            f"SELECT COUNT(*) FROM `{table_name}` WHERE `{user_column}` = :user_id "
            f"AND LOWER(COALESCE(`{status_column}`, '')) IN ({status_placeholders})"
        )
        params = {"user_id": user_id, **{f"status_{index}": value for index, value in enumerate(accepted_values)}}
        return _scalar_count(db, sql, params)

    return _count_user_rows(db, inspector, FRIEND_TABLES, user_id)


def _count_unread_messages(db: Session, inspector, user_id: int) -> int:
    table_name = _find_table(inspector, PRIVATE_MESSAGE_TABLES)
    if not table_name:
        return 0

    recipient_column = _find_column(inspector, table_name, RECIPIENT_COLUMNS)
    if not recipient_column:
        return 0

    read_column = _find_column(inspector, table_name, READ_COLUMNS)
    if read_column:
        sql = (
            f"SELECT COUNT(*) FROM `{table_name}` "
            f"WHERE `{recipient_column}` = :user_id AND COALESCE(`{read_column}`, 0) = 0"
        )
        return _scalar_count(db, sql, {"user_id": user_id})

    status_column = _find_column(inspector, table_name, STATUS_COLUMNS)
    if status_column:
        sql = (
            f"SELECT COUNT(*) FROM `{table_name}` "
            f"WHERE `{recipient_column}` = :user_id AND LOWER(COALESCE(`{status_column}`, '')) = 'unread'"
        )
        return _scalar_count(db, sql, {"user_id": user_id})

    return 0


def _format_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _get_recent_ai_session(db: Session, inspector, user_id: int) -> dict[str, Any] | None:
    table_name = _find_table(inspector, AI_SESSION_TABLES)
    if not table_name:
        return None

    user_column = _find_column(inspector, table_name, USER_COLUMNS)
    if not user_column:
        return None

    id_column = _find_column(inspector, table_name, ["id", "session_id", "conversation_id"])
    if not id_column:
        return None

    title_column = _find_column(inspector, table_name, TITLE_COLUMNS)
    updated_column = _find_column(inspector, table_name, UPDATED_COLUMNS)
    order_column = updated_column or id_column
    title_select = f"`{title_column}` AS title" if title_column else "'' AS title"
    updated_select = f"`{updated_column}` AS updated_at" if updated_column else "NULL AS updated_at"

    sql = (
        f"SELECT `{id_column}` AS id, {title_select}, {updated_select} "
        f"FROM `{table_name}` WHERE `{user_column}` = :user_id "
        f"ORDER BY `{order_column}` DESC, `{id_column}` DESC LIMIT 1"
    )

    row = db.execute(text(sql), {"user_id": user_id}).mappings().first()
    if not row:
        return None

    return {
        "id": int(row["id"] or 0),
        "title": str(row["title"] or "最近一次情绪陪伴"),
        "updated_at": _format_datetime(row.get("updated_at")),
    }


def _get_recent_posts(db: Session, inspector) -> list[dict[str, Any]]:
    table_name = _find_table(inspector, POST_TABLES)
    if not table_name:
        return []

    id_column = _find_column(inspector, table_name, ["id", "post_id", "article_id"])
    if not id_column:
        return []

    title_column = _find_column(inspector, table_name, TITLE_COLUMNS)
    category_column = _find_column(inspector, table_name, CATEGORY_COLUMNS)
    like_column = _find_column(inspector, table_name, LIKE_COLUMNS)
    comment_column = _find_column(inspector, table_name, COMMENT_COLUMNS)
    updated_column = _find_column(inspector, table_name, UPDATED_COLUMNS)
    order_column = updated_column or id_column

    select_fields = [f"`{id_column}` AS id"]
    select_fields.append(f"`{title_column}` AS title" if title_column else "'' AS title")
    select_fields.append(f"`{category_column}` AS category" if category_column else "'' AS category")
    select_fields.append(f"`{like_column}` AS like_count" if like_column else "0 AS like_count")
    select_fields.append(f"`{comment_column}` AS comment_count" if comment_column else "0 AS comment_count")

    sql = (
        f"SELECT {', '.join(select_fields)} FROM `{table_name}` "
        f"ORDER BY `{order_column}` DESC, `{id_column}` DESC LIMIT 5"
    )

    rows = db.execute(text(sql)).mappings().all()
    recent_posts: list[dict[str, Any]] = []
    for row in rows:
        recent_posts.append(
            {
                "id": int(row["id"] or 0),
                "title": str(row["title"] or "未命名帖子"),
                "category": str(row["category"] or ""),
                "like_count": int(row["like_count"] or 0),
                "comment_count": int(row["comment_count"] or 0),
            }
        )

    return recent_posts


@router.get("/overview")
def get_home_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inspector = _get_inspector(db)

    statistics = {
        "ai_chat_count": _count_user_rows(db, inspector, AI_SESSION_TABLES, current_user.id),
        "friend_count": _count_friends(db, inspector, current_user.id),
        "post_count": _count_user_rows(db, inspector, POST_TABLES, current_user.id),
        "favorite_count": _count_user_rows(db, inspector, FAVORITE_TABLES, current_user.id),
        "unread_private_message_count": _count_unread_messages(db, inspector, current_user.id),
    }

    overview = HomeOverviewData.model_validate(
        {
            "user": {
                "id": current_user.id,
                "nickname": current_user.nickname or "",
                "avatar": current_user.avatar or "",
                "username": current_user.username,
                "email": current_user.email or "",
                "occupation": current_user.occupation or "",
                "age": current_user.age,
                "gender": current_user.gender or "",
                "role": current_user.role or "",
            },
            "statistics": statistics,
            "recent_ai_session": _get_recent_ai_session(db, inspector, current_user.id),
            "recent_posts": _get_recent_posts(db, inspector),
        }
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": overview.model_dump(),
    }