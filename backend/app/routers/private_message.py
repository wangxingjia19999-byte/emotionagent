from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.friend import Friendship, PrivateMessage
from app.models.user import User
from app.schemas.friend import MessageHistory, PrivateMessageItem, PrivateMessageSend, UnreadCount
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/private-messages", tags=["私聊"])


def _are_friends(db: Session, user_id: int, target_id: int) -> bool:
    return (
        db.query(Friendship)
        .filter(
            or_(
                (Friendship.user_id == user_id) & (Friendship.friend_id == target_id),
                (Friendship.user_id == target_id) & (Friendship.friend_id == user_id),
            )
        )
        .first()
        is not None
    )


@router.post("/send")
def send_message(
    payload: PrivateMessageSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送私聊消息"""
    if not _are_friends(db, current_user.id, payload.receiver_id):
        raise HTTPException(status_code=403, detail="只能给好友发送消息")

    msg = PrivateMessage(
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        content=payload.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return {
        "code": 0,
        "message": "发送成功",
        "data": {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat(),
        },
    }


@router.get("/history/{friend_id}")
def get_message_history(
    friend_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取与好友的聊天记录"""
    if not _are_friends(db, current_user.id, friend_id):
        raise HTTPException(status_code=403, detail="只能查看好友的消息")

    query = (
        db.query(PrivateMessage)
        .filter(
            or_(
                (PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == friend_id),
                (PrivateMessage.sender_id == friend_id) & (PrivateMessage.receiver_id == current_user.id),
            )
        )
        .order_by(PrivateMessage.created_at.desc())
    )

    total = query.count()
    messages = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        PrivateMessageItem(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            is_read=m.is_read,
            created_at=m.created_at,
        ).model_dump()
        for m in reversed(messages)  # 正序返回
    ]

    return {
        "code": 0,
        "message": "success",
        "data": MessageHistory(items=items, total=total, page=page, page_size=page_size).model_dump(),
    }


@router.get("/unread")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取未读消息数（按好友分组）"""
    unread_msgs = (
        db.query(PrivateMessage)
        .filter(
            PrivateMessage.receiver_id == current_user.id,
            PrivateMessage.is_read == False,
        )
        .all()
    )

    by_friend = {}
    for m in unread_msgs:
        key = str(m.sender_id)
        by_friend[key] = by_friend.get(key, 0) + 1

    return {
        "code": 0,
        "message": "success",
        "data": {"total": len(unread_msgs), "by_friend": by_friend},
    }


@router.post("/read/{friend_id}")
def mark_as_read(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记来自好友的消息为已读"""
    db.query(PrivateMessage).filter(
        PrivateMessage.sender_id == friend_id,
        PrivateMessage.receiver_id == current_user.id,
        PrivateMessage.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"code": 0, "message": "已标记为已读"}
