from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import PasswordChange, ProfileUpdate
from app.utils.jwt import get_current_user
from app.utils.security import hash_password, verify_password


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "nickname": current_user.nickname or "",
            "avatar": current_user.avatar or "",
            "role": current_user.role,
        },
    }


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar is not None:
        current_user.avatar = payload.avatar

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "code": 0,
        "message": "更新成功",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "nickname": current_user.nickname or "",
            "avatar": current_user.avatar or "",
            "role": current_user.role,
        },
    }


@router.put("/password")
def change_password(payload: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"code": 0, "message": "密码修改成功", "data": None}
