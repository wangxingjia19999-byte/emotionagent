from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    LoginResponseData,
    RefreshTokenRequest,
    UserLogin,
    UserRegister,
)
from app.utils.audit import audit_log
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


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


def _is_locked(user: User) -> bool:
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        return True
    return False


# ═══════════════ 注册 ═══════════════


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
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


# ═══════════════ 登录 ═══════════════


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")

    # 检查锁定状态
    if _is_locked(user):
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"账户已被暂时锁定，请 {remaining} 分钟后重试",
        )

    if payload.role and user.role != payload.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号不属于所选登录入口")

    if not verify_password(payload.password, user.password_hash):
        # 记录登录失败
        user.failed_attempts = (user.failed_attempts or 0) + 1
        if user.failed_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            user.locked_until = user.locked_until.replace(minute=user.locked_until.minute + 15)
            db.add(user)
            db.commit()
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="密码错误次数过多，账户已锁定 15 分钟")
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码错误，还剩 {5 - user.failed_attempts} 次尝试机会",
        )

    # 登录成功，重置失败计数
    user.failed_attempts = 0
    user.locked_until = None
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id), extra_data={"username": user.username})
    refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "code": 0,
        "message": "登录成功",
        "data": LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user=_serialize_user(user),
        ).model_dump(),
    }


# ═══════════════ 刷新 Token ═══════════════


@router.post("/refresh")
@limiter.limit("20/minute")
def refresh_access_token(request: Request, payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload_data = decode_token(payload.refresh_token)
    if payload_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请提供 refresh token")

    subject = payload_data.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效")

    user = db.query(User).filter(User.id == int(subject)).first()
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")

    new_access = create_access_token(subject=str(user.id), extra_data={"username": user.username})
    new_refresh = create_refresh_token(subject=str(user.id))

    return {
        "code": 0,
        "message": "Token 已刷新",
        "data": {
            "access_token": new_access,
            "refresh_token": new_refresh,
        },
    }
