from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister
from app.utils.jwt import create_access_token
from app.utils.security import hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        avatar="",
        role="user",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"code": 0, "message": "注册成功", "data": None}


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")

    if payload.role and user.role != payload.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号不属于所选登录入口")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码错误")

    token = create_access_token(subject=str(user.id), extra_data={"username": user.username})
    response_data = {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname or "",
            "avatar": user.avatar or "",
            "role": user.role,
        },
    }
    return {"code": 0, "message": "登录成功", "data": response_data}
