from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.friend import FriendRequest, Friendship, PrivateMessage
from app.models.user import User
from app.schemas.friend import (
    FriendItem,
    FriendList,
    FriendRequestItem,
    FriendRequestList,
    FriendRequestSend,
    UserSearchItem,
)
from app.utils.audit import audit_log
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/friends", tags=["好友"])


def _serialize_user_brief(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname or "",
        "avatar": user.avatar or "",
        "occupation": user.occupation or None,
    }


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


# ==================== 用户搜索 ====================


@router.get("/search")
def search_users(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """搜索用户（按用户名或昵称）"""
    keyword = f"%{q.strip()}%"
    users = (
        db.query(User)
        .filter(
            User.id != current_user.id,
            User.status == "active",
            or_(User.username.like(keyword), User.nickname.like(keyword)),
        )
        .limit(20)
        .all()
    )

    results = []
    for u in users:
        is_friend = _are_friends(db, current_user.id, u.id)
        pending = (
            db.query(FriendRequest)
            .filter(
                FriendRequest.from_user_id == current_user.id,
                FriendRequest.to_user_id == u.id,
                FriendRequest.status == "pending",
            )
            .first()
            is not None
        )
        results.append(
            UserSearchItem(
                id=u.id,
                username=u.username,
                nickname=u.nickname or "",
                avatar=u.avatar or "",
                occupation=u.occupation,
                is_friend=is_friend,
                has_pending_request=pending,
            ).model_dump()
        )

    return {"code": 0, "message": "success", "data": results}


# ==================== 好友申请 ====================


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    payload: FriendRequestSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送好友申请"""
    if payload.to_user_id == current_user.id:
        return {"code": 1, "message": "不能添加自己为好友"}

    target = db.query(User).filter(User.id == payload.to_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    if _are_friends(db, current_user.id, payload.to_user_id):
        return {"code": 1, "message": "已经是好友了"}

    existing = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.from_user_id == current_user.id,
            FriendRequest.to_user_id == payload.to_user_id,
            FriendRequest.status == "pending",
        )
        .first()
    )
    if existing:
        return {"code": 1, "message": "已发送过申请，请等待对方处理"}

    # 如果对方也给我发了申请，自动成为好友
    reverse = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.from_user_id == payload.to_user_id,
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .first()
    )
    if reverse:
        reverse.status = "accepted"
        db.add(reverse)
        f1 = Friendship(user_id=current_user.id, friend_id=payload.to_user_id)
        f2 = Friendship(user_id=payload.to_user_id, friend_id=current_user.id)
        db.add(f1)
        db.add(f2)
        db.commit()
        return {"code": 0, "message": "对方已向你发过申请，已自动成为好友"}

    req = FriendRequest(
        from_user_id=current_user.id,
        to_user_id=payload.to_user_id,
        message=payload.message,
    )
    db.add(req)
    db.commit()
    return {"code": 0, "message": "好友申请已发送"}


@router.get("/requests")
def list_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看收到的好友申请"""
    requests = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .order_by(FriendRequest.created_at.desc())
        .all()
    )

    items = []
    for r in requests:
        items.append(
            FriendRequestItem(
                id=r.id,
                from_user_id=r.from_user_id,
                to_user_id=r.to_user_id,
                message=r.message,
                status=r.status,
                from_user=_serialize_user_brief(r.from_user) if r.from_user else {},
                created_at=r.created_at,
            ).model_dump()
        )

    return {"code": 0, "message": "success", "data": FriendRequestList(items=items, total=len(items)).model_dump()}


@router.post("/accept")
def accept_friend_request(
    request_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同意好友申请"""
    req = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="申请不存在或已处理")

    req.status = "accepted"
    db.add(req)

    f1 = Friendship(user_id=current_user.id, friend_id=req.from_user_id)
    f2 = Friendship(user_id=req.from_user_id, friend_id=current_user.id)
    db.add(f1)
    db.add(f2)
    db.commit()

    return {"code": 0, "message": "已同意好友申请"}


@router.post("/reject")
def reject_friend_request(
    request_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """拒绝好友申请"""
    req = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="申请不存在或已处理")

    req.status = "rejected"
    db.add(req)
    db.commit()
    return {"code": 0, "message": "已拒绝好友申请"}


# ==================== 好友列表 ====================


@router.get("")
def list_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取好友列表（含未读消息数和最后消息）"""
    friendships = (
        db.query(Friendship)
        .filter(Friendship.user_id == current_user.id)
        .order_by(Friendship.created_at.desc())
        .all()
    )

    items = []
    for fs in friendships:
        friend = db.query(User).filter(User.id == fs.friend_id).first()
        if not friend:
            continue

        unread = (
            db.query(PrivateMessage)
            .filter(
                PrivateMessage.sender_id == fs.friend_id,
                PrivateMessage.receiver_id == current_user.id,
                PrivateMessage.is_read == False,
            )
            .count()
        )

        last_msg = (
            db.query(PrivateMessage)
            .filter(
                or_(
                    (PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == fs.friend_id),
                    (PrivateMessage.sender_id == fs.friend_id) & (PrivateMessage.receiver_id == current_user.id),
                )
            )
            .order_by(PrivateMessage.created_at.desc())
            .first()
        )

        items.append(
            FriendItem(
                id=fs.id,
                friend_id=friend.id,
                username=friend.username,
                nickname=friend.nickname or "",
                avatar=friend.avatar or "",
                occupation=friend.occupation,
                unread_count=unread,
                last_message=last_msg.content[:50] if last_msg else None,
                last_message_time=last_msg.created_at if last_msg else None,
                created_at=fs.created_at,
            ).model_dump()
        )

    return {"code": 0, "message": "success", "data": FriendList(items=items, total=len(items)).model_dump()}


@router.delete("/{friend_id}")
def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除好友"""
    db.query(Friendship).filter(
        or_(
            (Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id),
            (Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id),
        )
    ).delete()
    db.commit()

    audit_log(current_user.id, "remove_friend", "friendship", friend_id)
    return {"code": 0, "message": "已删除好友"}
