from __future__ import annotations

from collections.abc import Iterable
import json
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Comment, Favorite, Post, PostHug, PostLike
from app.models.user import User
from app.schemas.post import (
    CommentActionResponse,
    CommentCreate,
    CommentItemResponse,
    CommentPageResponse,
    PostCreate,
    PostActionResponse,
    PostDetailResponse,
    PostItemResponse,
    PostPageResponse,
    PostUpdate,
)
from app.utils.audit import audit_log
from app.utils.jwt import get_current_user


router = APIRouter(prefix="/posts", tags=["帖子"])
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "posts"
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def _ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_image_url(image_url: str | None) -> str | None:
    if image_url is None:
        return None
    image_url = image_url.strip()
    return image_url or None


def _normalize_image_urls(image_urls: str | list[str] | None, fallback_image_url: str | None = None) -> list[str]:
    if isinstance(image_urls, str):
        try:
            parsed_value = json.loads(image_urls)
        except json.JSONDecodeError:
            parsed_value = []
    else:
        parsed_value = image_urls or []

    if not isinstance(parsed_value, list):
        parsed_value = []

    cleaned_urls = []
    for item in parsed_value:
        if isinstance(item, str):
            item = item.strip()
            if item:
                cleaned_urls.append(item)

    if not cleaned_urls and fallback_image_url:
        normalized_fallback = _normalize_image_url(fallback_image_url)
        if normalized_fallback:
            cleaned_urls.append(normalized_fallback)

    return cleaned_urls[:9]


def _serialize_user(user: User | None) -> dict:
    if not user:
        return {
            "id": 0,
            "username": "",
            "nickname": "",
            "avatar": "",
            "role": "",
        }

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname or "",
        "avatar": user.avatar or "",
        "role": user.role or "",
    }


def _get_post_or_404(db: Session, post_id: int) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在或已删除")
    return post


def _get_comment_or_404(db: Session, comment_id: int) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment or comment.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在或已删除")
    return comment


def _load_users_map(db: Session, user_ids: Iterable[int]) -> dict[int, User]:
    ids = list({int(user_id) for user_id in user_ids if user_id is not None})
    if not ids:
        return {}
    users = db.query(User).filter(User.id.in_(ids)).all()
    return {user.id: user for user in users}


def _serialize_post(post: Post, author: User | None, *, liked: bool = False, hugged: bool = False, favorited: bool = False) -> dict:
    image_urls = _normalize_image_urls(getattr(post, "image_urls", None), getattr(post, "image_url", None))
    is_anonymous = bool(getattr(post, "is_anonymous", False))
    payload = {
        "id": post.id,
        "user_id": post.user_id if not is_anonymous else 0,
        "title": post.title,
        "content": post.content,
        "category": post.category or "其他",
        "mood_tag": getattr(post, "mood_tag", None) or None,
        "is_anonymous": is_anonymous,
        "image_url": image_urls[0] if image_urls else _normalize_image_url(post.image_url),
        "image_urls": image_urls,
        "view_count": int(post.view_count or 0),
        "like_count": int(post.like_count or 0),
        "hug_count": int(post.hug_count or 0),
        "comment_count": int(post.comment_count or 0),
        "favorite_count": int(post.favorite_count or 0),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": _serialize_user(author) if not is_anonymous else {
            "id": 0, "username": "", "nickname": "匿名用户", "avatar": "", "role": "",
        },
    }
    if liked or hugged or favorited:
        payload["liked"] = liked
        payload["hugged"] = hugged
        payload["favorited"] = favorited
    return payload


def _serialize_comment(comment: Comment, author: User | None) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "author": _serialize_user(author),
    }


def _paginate_items(items: list, total: int, page: int, page_size: int):
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def _post_page_query(
    db: Session,
    *,
    keyword: str | None = None,
    category: str | None = None,
    mood_tag: str | None = None,
    sort: Literal["latest", "hot"] = "latest",
    user_id: int | None = None,
    favorite_only: bool = False,
):
    query = db.query(Post).filter(Post.is_deleted.is_(False))

    if user_id is not None and not favorite_only:
        query = query.filter(Post.user_id == user_id)

    if favorite_only:
        query = query.join(Favorite, Favorite.post_id == Post.id).filter(Favorite.user_id == user_id)

    if keyword:
        keyword = keyword.strip()
        if keyword:
            like_keyword = f"%{keyword}%"
            query = query.filter(or_(Post.title.like(like_keyword), Post.content.like(like_keyword)))

    if category:
        category = category.strip()
        if category:
            query = query.filter(Post.category == category)

    if mood_tag:
        mood_tag = mood_tag.strip()
        if mood_tag:
            query = query.filter(Post.mood_tag == mood_tag)

    if sort == "hot":
        hot_score = Post.like_count + Post.comment_count + Post.view_count
        query = query.order_by(desc(hot_score), desc(Post.created_at))
    elif favorite_only:
        query = query.order_by(desc(Favorite.created_at), desc(Post.created_at))
    else:
        query = query.order_by(desc(Post.created_at))

    return query


def _prepare_post_images(payload_image_urls: list[str] | None, payload_image_url: str | None) -> tuple[str | None, str | None]:
    cleaned_urls = _normalize_image_urls(payload_image_urls, payload_image_url)
    return (cleaned_urls[0] if cleaned_urls else None, json.dumps(cleaned_urls, ensure_ascii=False) if cleaned_urls else None)


@router.post("/images")
async def upload_post_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择图片文件")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 jpg、jpeg、png、gif、webp、bmp 格式")

    content_type = (file.content_type or "").lower()
    if content_type and not content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择图片文件")

    _ensure_upload_dir()
    stored_name = f"{current_user.id}_{uuid4().hex}{suffix}"
    stored_path = UPLOAD_DIR / stored_name

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片不能为空")

    stored_path.write_bytes(content)
    image_url = str(request.url_for("static", path=f"posts/{stored_name}"))
    return {
        "code": 0,
        "message": "上传成功",
        "data": {"image_url": image_url},
    }


@router.post("")
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        user_id=current_user.id,
        title=payload.title,
        content=payload.content,
        category=payload.category or "其他",
        mood_tag=payload.mood_tag,
        is_anonymous=payload.is_anonymous,
        image_url=_prepare_post_images(payload.image_urls, payload.image_url)[0],
        image_urls=_prepare_post_images(payload.image_urls, payload.image_url)[1],
    )
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    response = PostDetailResponse.model_validate(
        _serialize_post(post, current_user, liked=False, favorited=False)
    )
    return {
        "code": 0,
        "message": "发布成功",
        "data": response.model_dump(),
    }


@router.get("")
def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    mood_tag: str | None = Query(default=None),
    sort: Literal["latest", "hot"] = Query(default="latest"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _post_page_query(db, keyword=keyword, category=category, mood_tag=mood_tag, sort=sort)
    total = query.count()
    posts = query.offset((page - 1) * page_size).limit(page_size).all()
    author_map = _load_users_map(db, [post.user_id for post in posts])

    items = [
        PostItemResponse.model_validate(_serialize_post(post, author_map.get(post.user_id))).model_dump()
        for post in posts
    ]
    page_data = PostPageResponse.model_validate(_paginate_items(items, total, page, page_size))
    return {
        "code": 0,
        "message": "获取成功",
        "data": page_data.model_dump(),
    }


@router.get("/my")
def list_my_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _post_page_query(db, user_id=current_user.id)
    total = query.count()
    posts = query.offset((page - 1) * page_size).limit(page_size).all()
    author_map = {current_user.id: current_user}
    items = [
        PostItemResponse.model_validate(_serialize_post(post, author_map.get(post.user_id))).model_dump()
        for post in posts
    ]
    page_data = PostPageResponse.model_validate(_paginate_items(items, total, page, page_size))
    return {
        "code": 0,
        "message": "获取成功",
        "data": page_data.model_dump(),
    }


@router.get("/favorites")
def list_my_favorites(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _post_page_query(db, user_id=current_user.id, favorite_only=True)
    total = query.count()
    posts = query.offset((page - 1) * page_size).limit(page_size).all()
    author_map = _load_users_map(db, [post.user_id for post in posts])
    items = [
        PostItemResponse.model_validate(_serialize_post(post, author_map.get(post.user_id))).model_dump()
        for post in posts
    ]
    page_data = PostPageResponse.model_validate(_paginate_items(items, total, page, page_size))
    return {
        "code": 0,
        "message": "获取成功",
        "data": page_data.model_dump(),
    }


@router.get("/{post_id}/comments")
def list_comments(
    post_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_post_or_404(db, post_id)
    query = (
        db.query(Comment)
        .filter(Comment.post_id == post_id, Comment.is_deleted.is_(False))
        .order_by(Comment.created_at.asc())
    )
    total = query.count()
    comments = query.offset((page - 1) * page_size).limit(page_size).all()
    author_map = _load_users_map(db, [comment.user_id for comment in comments])

    items = [
        CommentItemResponse.model_validate(_serialize_comment(comment, author_map.get(comment.user_id))).model_dump()
        for comment in comments
    ]
    page_data = CommentPageResponse.model_validate(_paginate_items(items, total, page, page_size))
    return {
        "code": 0,
        "message": "获取成功",
        "data": page_data.model_dump(),
    }


@router.post("/{post_id}/comments")
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    comment = Comment(post_id=post.id, user_id=current_user.id, content=payload.content)
    post.comment_count = int(post.comment_count or 0) + 1

    db.add(comment)
    db.add(post)
    try:
        db.commit()
        db.refresh(comment)
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    response = CommentItemResponse.model_validate(
        _serialize_comment(comment, current_user)
    )
    return {
        "code": 0,
        "message": "评论成功",
        "data": response.model_dump(),
    }


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = _get_comment_or_404(db, comment_id)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的评论")

    post = db.query(Post).filter(Post.id == comment.post_id).first()
    comment.is_deleted = True
    if post and not post.is_deleted:
        post.comment_count = max(0, int(post.comment_count or 0) - 1)

    db.add(comment)
    if post:
        db.add(post)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    audit_log(current_user.id, "delete_comment", "comment", comment.id)

    response = CommentActionResponse.model_validate(
        {"comment_id": comment.id, "post_id": comment.post_id}
    )
    return {
        "code": 0,
        "message": "删除成功",
        "data": response.model_dump(),
    }


@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing_like = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
    )
    if existing_like:
        response = {
            "post_id": post.id,
            "liked": True,
            "favorited": False,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
        return {"code": 0, "message": "已经点赞过了", "data": response}

    like = PostLike(post_id=post.id, user_id=current_user.id)
    post.like_count = int(post.like_count or 0) + 1
    db.add(like)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except IntegrityError:
        db.rollback()
        response = {
            "post_id": post.id,
            "liked": True,
            "favorited": False,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
        return {"code": 0, "message": "已经点赞过了", "data": response}
    except Exception:
        db.rollback()
        raise

    response = PostActionResponse.model_validate(
        {
            "post_id": post.id,
            "liked": True,
            "favorited": False,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
    )
    return {"code": 0, "message": "点赞成功", "data": response.model_dump()}


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing_like = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
    )
    if not existing_like:
        response = PostActionResponse.model_validate(
            {
                "post_id": post.id,
                "liked": False,
                "favorited": False,
                "like_count": int(post.like_count or 0),
                "favorite_count": int(post.favorite_count or 0),
            }
        )
        return {"code": 0, "message": "尚未点赞", "data": response.model_dump()}

    db.delete(existing_like)
    post.like_count = max(0, int(post.like_count or 0) - 1)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    response = PostActionResponse.model_validate(
        {
            "post_id": post.id,
            "liked": False,
            "favorited": False,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
    )
    return {"code": 0, "message": "取消点赞成功", "data": response.model_dump()}


@router.post("/{post_id}/hug")
def hug_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing = (
        db.query(PostHug)
        .filter(PostHug.post_id == post.id, PostHug.user_id == current_user.id)
        .first()
    )
    if existing:
        return {"code": 0, "message": "已经抱抱过了", "data": {"post_id": post.id, "hug_count": int(post.hug_count or 0), "hugged": True}}

    hug = PostHug(post_id=post.id, user_id=current_user.id)
    post.hug_count = int(post.hug_count or 0) + 1
    db.add(hug)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except IntegrityError:
        db.rollback()
        return {"code": 0, "message": "已经抱抱过了", "data": {"post_id": post.id, "hug_count": int(post.hug_count or 0), "hugged": True}}

    return {"code": 0, "message": "抱抱成功", "data": {"post_id": post.id, "hug_count": int(post.hug_count or 0), "hugged": True}}


@router.delete("/{post_id}/hug")
def unhug_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing = (
        db.query(PostHug)
        .filter(PostHug.post_id == post.id, PostHug.user_id == current_user.id)
        .first()
    )
    if not existing:
        return {"code": 0, "message": "尚未抱抱", "data": {"post_id": post.id, "hug_count": int(post.hug_count or 0), "hugged": False}}

    db.delete(existing)
    post.hug_count = max(0, int(post.hug_count or 0) - 1)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise
    return {"code": 0, "message": "已取消抱抱", "data": {"post_id": post.id, "hug_count": int(post.hug_count or 0), "hugged": False}}


@router.post("/{post_id}/favorite")
def favorite_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing_favorite = (
        db.query(Favorite)
        .filter(Favorite.post_id == post.id, Favorite.user_id == current_user.id)
        .first()
    )
    if existing_favorite:
        response = PostActionResponse.model_validate(
            {
                "post_id": post.id,
                "liked": False,
                "favorited": True,
                "like_count": int(post.like_count or 0),
                "favorite_count": int(post.favorite_count or 0),
            }
        )
        return {"code": 0, "message": "已经收藏过了", "data": response.model_dump()}

    favorite = Favorite(post_id=post.id, user_id=current_user.id)
    post.favorite_count = int(post.favorite_count or 0) + 1
    db.add(favorite)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except IntegrityError:
        db.rollback()
        response = PostActionResponse.model_validate(
            {
                "post_id": post.id,
                "liked": False,
                "favorited": True,
                "like_count": int(post.like_count or 0),
                "favorite_count": int(post.favorite_count or 0),
            }
        )
        return {"code": 0, "message": "已经收藏过了", "data": response.model_dump()}
    except Exception:
        db.rollback()
        raise

    response = PostActionResponse.model_validate(
        {
            "post_id": post.id,
            "liked": False,
            "favorited": True,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
    )
    return {"code": 0, "message": "收藏成功", "data": response.model_dump()}


@router.delete("/{post_id}/favorite")
def unfavorite_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    existing_favorite = (
        db.query(Favorite)
        .filter(Favorite.post_id == post.id, Favorite.user_id == current_user.id)
        .first()
    )
    if not existing_favorite:
        response = PostActionResponse.model_validate(
            {
                "post_id": post.id,
                "liked": False,
                "favorited": False,
                "like_count": int(post.like_count or 0),
                "favorite_count": int(post.favorite_count or 0),
            }
        )
        return {"code": 0, "message": "尚未收藏", "data": response.model_dump()}

    db.delete(existing_favorite)
    post.favorite_count = max(0, int(post.favorite_count or 0) - 1)
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    response = PostActionResponse.model_validate(
        {
            "post_id": post.id,
            "liked": False,
            "favorited": False,
            "like_count": int(post.like_count or 0),
            "favorite_count": int(post.favorite_count or 0),
        }
    )
    return {"code": 0, "message": "取消收藏成功", "data": response.model_dump()}


@router.put("/{post_id}")
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己的帖子")

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.category is not None:
        post.category = payload.category
    if payload.mood_tag is not None:
        post.mood_tag = payload.mood_tag
    if payload.is_anonymous is not None:
        post.is_anonymous = payload.is_anonymous
    if payload.image_urls is not None or payload.image_url is not None:
        image_url, image_urls = _prepare_post_images(payload.image_urls, payload.image_url)
        post.image_url = image_url
        post.image_urls = image_urls

    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    response = PostDetailResponse.model_validate(
        _serialize_post(post, current_user, liked=False, favorited=False)
    )
    return {"code": 0, "message": "更新成功", "data": response.model_dump()}


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的帖子")

    post.is_deleted = True
    db.add(post)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    audit_log(current_user.id, "delete_post", "post", post.id, detail={"title": post.title})

    return {
        "code": 0,
        "message": "删除成功",
        "data": {"id": post.id},
    }


@router.get("/{post_id}")
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, post_id)
    post.view_count = int(post.view_count or 0) + 1
    db.add(post)
    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        raise

    author = db.query(User).filter(User.id == post.user_id).first()
    liked = (
        db.query(PostLike.id)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
        is not None
    )
    hugged = (
        db.query(PostHug.id)
        .filter(PostHug.post_id == post.id, PostHug.user_id == current_user.id)
        .first()
        is not None
    )
    favorited = (
        db.query(Favorite.id)
        .filter(Favorite.post_id == post.id, Favorite.user_id == current_user.id)
        .first()
        is not None
    )

    response = PostDetailResponse.model_validate(
        _serialize_post(post, author, liked=liked, hugged=hugged, favorited=favorited)
    )
    return {"code": 0, "message": "获取成功", "data": response.model_dump()}