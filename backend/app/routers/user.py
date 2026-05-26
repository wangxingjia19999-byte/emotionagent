from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import PasswordChange, ProfileUpdate
from app.utils.jwt import get_current_user
from app.utils.security import hash_password, verify_password


router = APIRouter(prefix="/user", tags=["user"])
AVATAR_DIR = Path(__file__).resolve().parent.parent / "static" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname or "",
        "avatar": user.avatar or "",
        "occupation": user.occupation or "",
        "age": user.age,
        "gender": user.gender or "",
        "role": user.role,
    }


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "code": 0,
        "message": "获取成功",
        "data": _serialize_user(current_user),
    }


@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    data = _serialize_user(user)
    if user.id != current_user.id:
        data["email"] = ""

    return {
        "code": 0,
        "message": "获取成功",
        "data": {**data, "is_self": user.id == current_user.id},
    }


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar is not None:
        current_user.avatar = payload.avatar
    if payload.email is not None and payload.email != current_user.email:
        existed_user = db.query(User).filter(User.email == payload.email, User.id != current_user.id).first()
        if existed_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被其他用户使用")
        current_user.email = payload.email
    if payload.occupation is not None:
        current_user.occupation = payload.occupation
    if payload.age is not None:
        current_user.age = payload.age
    if payload.gender is not None:
        current_user.gender = payload.gender

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "code": 0,
        "message": "更新成功",
        "data": _serialize_user(current_user),
    }


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只允许上传图片文件")

    original_suffix = Path(file.filename or "avatar.png").suffix or ".png"
    file_name = f"{uuid4().hex}{original_suffix}"
    file_path = AVATAR_DIR / file_name

    content = await file.read()
    file_path.write_bytes(content)

    avatar_url = f"http://127.0.0.1:8000/static/avatars/{file_name}"
    current_user.avatar = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "code": 0,
        "message": "头像上传成功",
        "data": {
            "avatar": avatar_url,
        },
    }


@router.put("/password")
def change_password(payload: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="两次输入的新密码不一致")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"code": 0, "message": "密码修改成功", "data": None}
