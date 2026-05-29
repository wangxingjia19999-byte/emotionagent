import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.schemas.user import (
    LoginResponseData,
    RefreshTokenRequest,
    SendVerifyCodeRequest,
    UserLogin,
    UserRegister,
)
from app.utils.audit import audit_log
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.mailer import send_verification_email
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


def _generate_account(db: Session) -> str:
    """生成系统账号：日期 + 3位序号，例如 20260528001"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = today
    last = (
        db.query(User)
        .filter(User.username.like(f"{prefix}%"))
        .order_by(User.username.desc())
        .first()
    )
    if last and last.username.startswith(prefix) and len(last.username) == len(prefix) + 3:
        seq = int(last.username[-3:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


# ═══════════════ 发送验证码 ═══════════════


@router.post("/send-verify-code")
@limiter.limit("3/minute")
def send_verify_code(request: Request, payload: SendVerifyCodeRequest, db: Session = Depends(get_db)):
    """向指定邮箱发送 6 位验证码（5 分钟有效）"""
    email = payload.email.strip().lower()

    # 60 秒内不允许重复发送
    recent = (
        db.query(VerificationCode)
        .filter(
            and_(
                VerificationCode.email == email,
                VerificationCode.purpose == "register",
                VerificationCode.created_at > datetime.now() - timedelta(seconds=60),
            )
        )
        .first()
    )
    if recent:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="验证码已发送，请 60 秒后再试",
        )

    code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now() + timedelta(minutes=5)

    vc = VerificationCode(email=email, code=code, purpose="register", expires_at=expires_at)
    db.add(vc)
    db.commit()

    ok = send_verification_email(email, code)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件发送失败，请稍后重试",
        )

    return {"code": 0, "message": f"验证码已发送至 {email}，5分钟内有效", "data": None}


# ═══════════════ 注册 ═══════════════


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
    """邮箱验证码注册，系统自动分配账号"""
    email = payload.email.strip().lower()

    # 校验验证码
    vc = (
        db.query(VerificationCode)
        .filter(
            and_(
                VerificationCode.email == email,
                VerificationCode.purpose == "register",
                VerificationCode.is_used == 0,
            )
        )
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    if not vc or vc.code != payload.verification_code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或不存在")
    if vc.expires_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码已过期，请重新获取")

    # 检查邮箱是否已注册
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已注册，请直接登录")

    # 标记验证码已使用
    vc.is_used = 1
    db.add(vc)

    # 生成系统账号
    account = _generate_account(db)

    user = User(
        username=account,
        email=email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname or "",
        avatar="",
        role="user",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit_log(
        user_id=user.id,
        action="register",
        target_type="user",
        target_id=user.id,
        detail={"account": account, "email": email},
        ip_address=request.client.host if request.client else None,
    )

    return {
        "code": 0,
        "message": "注册成功",
        "data": {
            "username": account,
            "email": email,
        },
    }


# ═══════════════ 登录 ═══════════════


def _find_user_by_account(db: Session, account: str):
    """通过邮箱或系统账号查找用户"""
    account = account.strip().lower() if "@" in account else account.strip()
    if "@" in account:
        return db.query(User).filter(User.email == account).first()
    return db.query(User).filter(User.username == account).first()


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = _find_user_by_account(db, payload.account)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号或密码错误")

    # 检查锁定状态
    if _is_locked(user):
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"账户已被暂时锁定，请 {remaining} 分钟后重试",
        )

    if payload.role and user.role != payload.role:
        # 管理员入口同时接受 admin 和 super_admin
        if not (payload.role == "admin" and user.role == "super_admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号不属于所选登录入口")

    if not verify_password(payload.password, user.password_hash):
        user.failed_attempts = (user.failed_attempts or 0) + 1
        if user.failed_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.add(user)
            db.commit()
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="密码错误次数过多，账户已锁定 15 分钟")
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码错误，还剩 {5 - user.failed_attempts} 次尝试机会",
        )

    # 登录成功
    user.failed_attempts = 0
    user.locked_until = None
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id), extra_data={"username": user.username})
    refresh_token = create_refresh_token(subject=str(user.id))

    audit_log(
        user_id=user.id,
        action="login",
        target_type="user",
        target_id=user.id,
        detail={"status": "success"},
        ip_address=request.client.host if request.client else None,
    )

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
