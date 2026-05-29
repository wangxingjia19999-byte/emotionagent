"""
管理员独立认证系统
管理员账号存储在 admins 表中，与 users 表完全隔离
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth/admin", tags=["管理员认证"])
limiter = Limiter(key_func=get_remote_address)


def _serialize_admin(admin: Admin) -> dict:
    return {
        "id": admin.id,
        "username": admin.username,
        "nickname": admin.nickname or "",
        "role": admin.role,
    }


def _is_locked(admin: Admin) -> bool:
    if admin.locked_until and admin.locked_until > datetime.now(timezone.utc):
        return True
    return False


@router.post("/login")
@limiter.limit("10/minute")
def admin_login(request: Request, body: dict, db: Session = Depends(get_db)):
    """
    管理员登录
    返回清晰错误信息：账号不存在 / 密码错误 / 账号被锁定
    """
    account = (body.get("account") or body.get("username") or "").strip()
    password = body.get("password") or ""

    if not account:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请输入管理员账号")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请输入密码")

    # 查找管理员
    admin = db.query(Admin).filter(Admin.username == account).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员账号不存在")

    if admin.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该管理员账号已被禁用")

    if _is_locked(admin):
        remaining = int((admin.locked_until - datetime.now(timezone.utc)).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"密码错误次数过多，账户已锁定，请 {remaining} 分钟后再试",
        )

    if not verify_password(password, admin.password_hash):
        admin.failed_attempts = (admin.failed_attempts or 0) + 1
        remaining = 5 - admin.failed_attempts
        if admin.failed_attempts >= 5:
            admin.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.add(admin)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="密码错误次数过多，账户已锁定 15 分钟",
            )
        db.add(admin)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"密码错误，还剩 {remaining} 次尝试机会",
        )

    # 登录成功
    admin.failed_attempts = 0
    admin.locked_until = None
    db.add(admin)
    db.commit()
    db.refresh(admin)

    access_token = create_access_token(
        subject=str(admin.id),
        extra_data={"username": admin.username, "is_admin": True, "admin_role": admin.role},
    )
    refresh_token = create_refresh_token(subject=str(admin.id))

    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "admin": _serialize_admin(admin),
        },
    }


@router.post("/refresh")
@limiter.limit("20/minute")
def admin_refresh_token(request: Request, body: dict, db: Session = Depends(get_db)):
    """管理员刷新 token"""
    token = body.get("refresh_token", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请提供 refresh_token")

    payload_data = decode_token(token)
    if payload_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请提供有效的 refresh token")

    is_admin = payload_data.get("is_admin")
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="非管理员 token")

    subject = payload_data.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效")

    admin = db.query(Admin).filter(Admin.id == int(subject)).first()
    if not admin or admin.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="管理员不存在或已禁用")

    new_access = create_access_token(
        subject=str(admin.id),
        extra_data={"username": admin.username, "is_admin": True, "admin_role": admin.role},
    )
    new_refresh = create_refresh_token(subject=str(admin.id))

    return {
        "code": 0,
        "message": "Token 已刷新",
        "data": {
            "access_token": new_access,
            "refresh_token": new_refresh,
        },
    }
