"""
管理员后台 API
所有接口需要 admin 或 super_admin 角色
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.audit_log import AuditLog
from app.models.crisis_alert import CrisisAlert
from app.models.emotion_log import EmotionLog
from app.models.post import Post, Comment
from app.models.questionnaire import QuestionnaireRecord
from app.models.shop import (
    CartItem, Order, OrderItem, Product, ProductCategory, UserAddress,
)
from app.models.user import User
from app.models.user_profile import UserProfile
from app.utils.jwt import get_current_admin
from app.utils.security import hash_password

router = APIRouter(prefix="/admin", tags=["管理后台"])


# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

def _require_super_admin(admin: Admin) -> None:
    """要求 super_admin 角色"""
    if admin.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅超级管理员可执行此操作")


def _write_audit(admin: Admin, action: str, target_type: str, target_id: int,
                 detail: str | None = None, ip_address: str | None = None,
                 db: Session | None = None) -> None:
    """写入审计日志（静默，失败不影响主操作）"""
    if db is None:
        return
    try:
        log = AuditLog(
            user_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
    except Exception:
        pass  # 审计日志失败不应阻断主流程


# ═══════════════════════════════════════════════════════════════
# 仪表盘
# ═══════════════════════════════════════════════════════════════

@router.get("/dashboard")
def dashboard(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar()
    new_users_week = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar()

    total_products = db.query(func.count(Product.id)).scalar()
    on_sale = db.query(func.count(Product.id)).filter(Product.is_on_sale == 1).scalar()

    total_orders = db.query(func.count(Order.id)).scalar()
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == "pending_payment").scalar()
    today_orders = db.query(func.count(Order.id)).filter(Order.created_at >= today).scalar()
    revenue = db.query(func.sum(Order.total_amount)).filter(Order.status.in_(("paid", "shipped", "completed"))).scalar() or 0

    total_posts = db.query(func.count(Post.id)).filter(Post.is_deleted == 0).scalar()
    new_posts_week = db.query(func.count(Post.id)).filter(Post.is_deleted == 0, Post.created_at >= week_ago).scalar()

    total_questionnaires = db.query(func.count(QuestionnaireRecord.id)).scalar()
    questionnaires_week = db.query(func.count(QuestionnaireRecord.id)).filter(QuestionnaireRecord.created_at >= week_ago).scalar()

    total_emotion_logs = db.query(func.count(EmotionLog.id)).scalar()
    emotion_logs_week = db.query(func.count(EmotionLog.id)).filter(EmotionLog.created_at >= week_ago).scalar()

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "users": {"total": total_users, "active": active_users, "new_this_week": new_users_week},
            "shop": {"total_products": total_products, "on_sale": on_sale, "total_orders": total_orders, "pending_orders": pending_orders, "today_orders": today_orders, "revenue": float(revenue)},
            "community": {"total_posts": total_posts, "new_this_week": new_posts_week},
            "emotion": {"total_questionnaires": total_questionnaires, "questionnaires_this_week": questionnaires_week, "total_emotion_logs": total_emotion_logs, "emotion_logs_this_week": emotion_logs_week},
        },
    }


# ═══════════════════════════════════════════════════════════════
# 商品分类管理
# ═══════════════════════════════════════════════════════════════

@router.get("/categories")
def list_categories(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    categories = db.query(ProductCategory).order_by(ProductCategory.sort_order).all()
    return {"code": 0, "message": "获取成功", "data": [
        {"id": c.id, "name": c.name, "description": c.description, "icon": c.icon, "sort_order": c.sort_order}
        for c in categories
    ]}


@router.post("/categories")
def create_category(name: str, description: str = "", icon: str = "", sort_order: int = 0,
                    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    cat = ProductCategory(name=name, description=description, icon=icon, sort_order=sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"code": 0, "message": "分类已创建", "data": {"id": cat.id}}


@router.put("/categories/{cat_id}")
def update_category(cat_id: int, name: Optional[str] = None, description: Optional[str] = None,
                    icon: Optional[str] = None, sort_order: Optional[int] = None,
                    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    cat = db.query(ProductCategory).filter(ProductCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if name is not None:
        cat.name = name
    if description is not None:
        cat.description = description
    if icon is not None:
        cat.icon = icon
    if sort_order is not None:
        cat.sort_order = sort_order
    db.commit()
    return {"code": 0, "message": "分类已更新", "data": None}


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    cat = db.query(ProductCategory).filter(ProductCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(cat)
    db.commit()
    return {"code": 0, "message": "分类已删除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 商品管理
# ═══════════════════════════════════════════════════════════════

@router.get("/products")
def list_products(keyword: str = "", category_id: int = 0, page: int = 1, page_size: int = 20,
                  admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(Product)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    total = q.count()
    items = q.order_by(desc(Product.id)).offset((page - 1) * page_size).limit(page_size).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": p.id, "category_id": p.category_id, "name": p.name, "description": p.description,
            "price": float(p.price), "original_price": float(p.original_price),
            "image_url": p.image_url, "stock": p.stock, "sales_count": p.sales_count,
            "product_type": p.product_type, "is_on_sale": p.is_on_sale, "sort_order": p.sort_order,
            "created_at": str(p.created_at),
        } for p in items],
    }}


@router.post("/products")
def create_product(
    category_id: int, name: str, description: str, price: float, original_price: float = 0,
    image_url: str = "", stock: int = 0, product_type: str = "physical", is_on_sale: int = 1, sort_order: int = 0,
    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db),
):
    p = Product(category_id=category_id, name=name, description=description, price=price,
                original_price=original_price, image_url=image_url, stock=stock,
                product_type=product_type, is_on_sale=is_on_sale, sort_order=sort_order)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"code": 0, "message": "商品已创建", "data": {"id": p.id}}


@router.put("/products/{product_id}")
def update_product(product_id: int,
                   category_id: Optional[int] = None, name: Optional[str] = None,
                   description: Optional[str] = None, price: Optional[float] = None,
                   original_price: Optional[float] = None, image_url: Optional[str] = None,
                   stock: Optional[int] = None, product_type: Optional[str] = None,
                   is_on_sale: Optional[int] = None, sort_order: Optional[int] = None,
                   admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    for field in ["category_id", "name", "description", "price", "original_price", "image_url", "stock", "product_type", "is_on_sale", "sort_order"]:
        val = locals().get(field)
        if val is not None:
            setattr(p, field, val)
    db.commit()
    return {"code": 0, "message": "商品已更新", "data": None}


@router.delete("/products/{product_id}")
def delete_product(product_id: int, request: Request = None,
                   admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(p)
    db.commit()
    _write_audit(admin, "delete_product", "product", product_id,
                 detail=f"删除商品:{p.name}", ip_address=request.client.host if request else None, db=db)
    return {"code": 0, "message": "商品已删除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 订单管理
# ═══════════════════════════════════════════════════════════════

@router.get("/orders")
def list_orders(status_filter: str = "", page: int = 1, page_size: int = 20,
                admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(Order)
    if status_filter:
        q = q.filter(Order.status == status_filter)
    total = q.count()
    orders = q.order_by(desc(Order.id)).offset((page - 1) * page_size).limit(page_size).all()
    for o in orders:
        o.items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": o.id, "order_no": o.order_no, "user_id": o.user_id,
            "total_amount": float(o.total_amount), "status": o.status,
            "payment_method": o.payment_method, "paid_at": str(o.paid_at) if o.paid_at else None,
            "created_at": str(o.created_at),
            "items": [{"product_name": i.product_name, "price": float(i.price), "quantity": i.quantity} for i in (o.items or [])],
        } for o in orders],
    }}


@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status_val: str, request: Request = None,
                        admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="订单不存在")
    old_status = o.status
    o.status = status_val
    db.commit()
    _write_audit(admin, "update_order_status", "order", order_id,
                 detail=f"{old_status}→{status_val}",
                 ip_address=request.client.host if request else None, db=db)
    return {"code": 0, "message": "订单状态已更新", "data": None}


# ═══════════════════════════════════════════════════════════════
# 用户管理
# ═══════════════════════════════════════════════════════════════

@router.get("/users")
def list_users(keyword: str = "", role: str = "", page: int = 1, page_size: int = 20,
               admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(User)
    if keyword:
        q = q.filter(User.nickname.contains(keyword) | User.username.contains(keyword) | User.email.contains(keyword))
    if role:
        q = q.filter(User.role == role)
    total = q.count()
    users = q.order_by(desc(User.id)).offset((page - 1) * page_size).limit(page_size).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": u.id, "username": u.username, "email": u.email,
            "nickname": u.nickname, "role": u.role, "status": u.status,
            "gender": u.gender, "age": u.age, "occupation": u.occupation,
            "created_at": str(u.created_at),
        } for u in users],
    }}


@router.put("/users/{user_id}")
def update_user(user_id: int, request: Request = None,
                nickname: Optional[str] = None, role: Optional[str] = None,
                status_val: Optional[str] = Query(None, alias="status"),
                admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的管理员权限")
    changes = []
    if nickname is not None:
        user.nickname = nickname
        changes.append("nickname")
    if role is not None:
        user.role = role
        changes.append(f"role→{role}")
    if status_val is not None:
        user.status = status_val
        changes.append(f"status→{status_val}")
    db.commit()
    _write_audit(admin, "update_user", "user", user_id,
                 detail=",".join(changes),
                 ip_address=request.client.host if request else None, db=db)
    return {"code": 0, "message": "用户已更新", "data": None}


# ═══════════════════════════════════════════════════════════════
# 问卷管理（只读）
# ═══════════════════════════════════════════════════════════════

@router.get("/questionnaires")
def list_questionnaires(user_id: int = 0, scale_type: str = "", page: int = 1, page_size: int = 20,
                        admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(QuestionnaireRecord)
    if user_id:
        q = q.filter(QuestionnaireRecord.user_id == user_id)
    if scale_type:
        q = q.filter(QuestionnaireRecord.scale_type == scale_type)
    total = q.count()
    records = q.order_by(desc(QuestionnaireRecord.id)).offset((page - 1) * page_size).limit(page_size).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": r.id, "user_id": r.user_id, "scale_type": r.scale_type,
            "total_score": r.total_score, "result_level": r.result_level,
            "answers": r.answers, "created_at": str(r.created_at),
        } for r in records],
    }}


# ═══════════════════════════════════════════════════════════════
# 情绪日志管理（只读）
# ═══════════════════════════════════════════════════════════════

@router.get("/emotion-logs")
def list_emotion_logs(user_id: int = 0, page: int = 1, page_size: int = 20,
                      admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(EmotionLog)
    if user_id:
        q = q.filter(EmotionLog.user_id == user_id)
    total = q.count()
    logs = q.order_by(desc(EmotionLog.id)).offset((page - 1) * page_size).limit(page_size).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": r.id, "user_id": r.user_id, "emotion_label": r.emotion_label,
            "intensity": r.intensity, "raw_text": r.raw_text, "suggestion": r.suggestion,
            "created_at": str(r.created_at),
        } for r in logs],
    }}


# ═══════════════════════════════════════════════════════════════
# 帖子管理
# ═══════════════════════════════════════════════════════════════

@router.get("/posts")
def list_posts(keyword: str = "", page: int = 1, page_size: int = 20,
               admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(Post).filter(Post.is_deleted == 0)
    if keyword:
        q = q.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    total = q.count()
    posts = q.order_by(desc(Post.id)).offset((page - 1) * page_size).limit(page_size).all()
    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": p.id, "user_id": p.user_id, "title": p.title,
            "content": p.content[:200] if p.content else "",
            "category": p.category, "mood_tag": p.mood_tag,
            "view_count": p.view_count, "like_count": p.like_count,
            "comment_count": p.comment_count, "is_anonymous": p.is_anonymous,
            "is_deleted": p.is_deleted, "created_at": str(p.created_at),
        } for p in posts],
    }}


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, request: Request = None,
                admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="帖子不存在")
    p.is_deleted = 1
    db.commit()
    _write_audit(admin, "delete_post", "post", post_id,
                 detail=f"删除帖子:{p.title[:50] if p.title else ''},作者:{p.user_id}",
                 ip_address=request.client.host if request else None, db=db)
    return {"code": 0, "message": "帖子已删除", "data": None}


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, request: Request = None,
                   admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="评论不存在")
    c.is_deleted = 1
    db.commit()
    _write_audit(admin, "delete_comment", "comment", comment_id,
                 detail=f"删除评论(帖子ID:{c.post_id})",
                 ip_address=request.client.host if request else None, db=db)
    return {"code": 0, "message": "评论已删除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 管理员账号管理（仅 super_admin）
# ═══════════════════════════════════════════════════════════════

class CreateAdminBody(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    nickname: str = ""
    role: str = "admin"


class UpdateAdminBody(BaseModel):
    nickname: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


@router.get("/admins")
def list_admins(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """列出所有管理员（所有 admin 角色均可查看）"""
    admins = db.query(Admin).order_by(Admin.id).all()
    return {"code": 0, "message": "获取成功", "data": [{
        "id": a.id, "username": a.username, "nickname": a.nickname or "",
        "role": a.role, "status": a.status,
        "failed_attempts": a.failed_attempts,
        "created_at": str(a.created_at),
    } for a in admins]}


@router.post("/admins")
def create_admin(body: CreateAdminBody,
                 admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """创建管理员（仅 super_admin）"""
    _require_super_admin(admin)

    existing = db.query(Admin).filter(Admin.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="管理员账号已存在")

    new_admin = Admin(
        username=body.username,
        password_hash=hash_password(body.password),
        nickname=body.nickname or body.username,
        role=body.role,
        status="active",
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    _write_audit(admin, "create_admin", "admin", new_admin.id,
                 detail=f"创建管理员:{body.username},角色:{body.role}", db=db)

    return {"code": 0, "message": "管理员已创建", "data": {"id": new_admin.id}}


@router.put("/admins/{admin_id}")
def update_admin(admin_id: int, body: UpdateAdminBody,
                 admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """更新管理员信息（仅 super_admin）"""
    _require_super_admin(admin)

    target = db.query(Admin).filter(Admin.id == admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的权限")

    changed = []
    if body.nickname is not None:
        target.nickname = body.nickname
        changed.append("nickname")
    if body.role is not None:
        target.role = body.role
        changed.append(f"role→{body.role}")
    if body.status is not None:
        target.status = body.status
        changed.append(f"status→{body.status}")

    db.commit()
    _write_audit(admin, "update_admin", "admin", admin_id,
                 detail=",".join(changed), db=db)
    return {"code": 0, "message": "管理员已更新", "data": None}


@router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int,
                 admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """删除管理员（仅 super_admin，不能删除自己）"""
    _require_super_admin(admin)

    target = db.query(Admin).filter(Admin.id == admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    username = target.username
    db.delete(target)
    db.commit()
    _write_audit(admin, "delete_admin", "admin", admin_id,
                 detail=f"删除管理员:{username}", db=db)
    return {"code": 0, "message": "管理员已删除", "data": None}


@router.post("/admins/{admin_id}/reset-password")
def reset_admin_password(admin_id: int, body: dict,
                         admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """重置管理员密码（仅 super_admin）"""
    _require_super_admin(admin)

    target = db.query(Admin).filter(Admin.id == admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")

    new_password = body.get("new_password", "")
    if len(new_password) < 8:
        raise HTTPException(status_code=422, detail="密码长度不能少于8位")

    target.password_hash = hash_password(new_password)
    target.failed_attempts = 0
    target.locked_until = None
    db.commit()
    _write_audit(admin, "reset_admin_password", "admin", admin_id, db=db)
    return {"code": 0, "message": "密码已重置", "data": None}


# ═══════════════════════════════════════════════════════════════
# 危机预警管理
# ═══════════════════════════════════════════════════════════════

@router.get("/crisis-alerts")
def list_crisis_alerts(
    risk_level: str = "", page: int = 1, page_size: int = 20,
    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db),
):
    """查看危机预警记录"""
    q = db.query(CrisisAlert)
    if risk_level:
        q = q.filter(CrisisAlert.risk_level == risk_level)
    total = q.count()
    alerts = q.order_by(desc(CrisisAlert.id)).offset((page - 1) * page_size).limit(page_size).all()

    # 关联用户名
    user_ids = list({a.user_id for a in alerts})
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": a.id, "user_id": a.user_id,
            "username": users.get(a.user_id, {}).username if a.user_id in users else "未知",
            "risk_type": a.risk_type, "risk_level": a.risk_level,
            "raw_text": a.raw_text[:300] if a.raw_text else "",
            "guidance": a.guidance,
            "created_at": str(a.created_at),
        } for a in alerts],
    }}


@router.delete("/crisis-alerts/{alert_id}")
def delete_crisis_alert(alert_id: int,
                        admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """删除危机预警记录"""
    alert = db.query(CrisisAlert).filter(CrisisAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    db.delete(alert)
    db.commit()
    _write_audit(admin, "delete_crisis_alert", "crisis_alert", alert_id, db=db)
    return {"code": 0, "message": "预警记录已删除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 用户详情
# ═══════════════════════════════════════════════════════════════

@router.get("/users/{user_id}/detail")
def get_user_detail(user_id: int,
                    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """获取用户完整信息（画像 + 情绪 + 问卷 + 危机记录）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    recent_emotions = (
        db.query(EmotionLog)
        .filter(EmotionLog.user_id == user_id)
        .order_by(desc(EmotionLog.created_at))
        .limit(10)
        .all()
    )

    recent_questionnaires = (
        db.query(QuestionnaireRecord)
        .filter(QuestionnaireRecord.user_id == user_id)
        .order_by(desc(QuestionnaireRecord.created_at))
        .limit(5)
        .all()
    )

    crisis_alerts = (
        db.query(CrisisAlert)
        .filter(CrisisAlert.user_id == user_id)
        .order_by(desc(CrisisAlert.created_at))
        .limit(5)
        .all()
    )

    return {"code": 0, "message": "获取成功", "data": {
        "basic": {
            "id": user.id, "username": user.username, "email": user.email,
            "nickname": user.nickname, "avatar": user.avatar,
            "gender": user.gender, "age": user.age, "occupation": user.occupation,
            "role": user.role, "status": user.status,
            "created_at": str(user.created_at),
        },
        "profile": {
            "stressors": profile.stressors if profile else "",
            "occupation": profile.occupation if profile else "",
        } if profile else None,
        "recent_emotions": [{
            "id": e.id, "emotion_label": e.emotion_label, "intensity": e.intensity,
            "raw_text": e.raw_text, "suggestion": e.suggestion,
            "created_at": str(e.created_at),
        } for e in recent_emotions],
        "recent_questionnaires": [{
            "id": q.id, "scale_type": q.scale_type,
            "total_score": q.total_score, "result_level": q.result_level,
            "created_at": str(q.created_at),
        } for q in recent_questionnaires],
        "crisis_alerts": [{
            "id": c.id, "risk_type": c.risk_type, "risk_level": c.risk_level,
            "raw_text": c.raw_text[:200] if c.raw_text else "",
            "created_at": str(c.created_at),
        } for c in crisis_alerts],
    }}


# ═══════════════════════════════════════════════════════════════
# 审计日志
# ═══════════════════════════════════════════════════════════════

@router.get("/audit-logs")
def list_audit_logs(
    action: str = "", user_id: int = 0, page: int = 1, page_size: int = 50,
    admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db),
):
    """查看操作审计日志"""
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    total = q.count()
    logs = q.order_by(desc(AuditLog.id)).offset((page - 1) * page_size).limit(page_size).all()

    # 关联管理员名
    admin_ids = list({l.user_id for l in logs})
    admins_map = {a.id: a for a in db.query(Admin).filter(Admin.id.in_(admin_ids)).all()} if admin_ids else {}

    return {"code": 0, "message": "获取成功", "data": {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": l.id, "admin_id": l.user_id,
            "admin_name": admins_map.get(l.user_id, {}).username if l.user_id in admins_map else "未知",
            "action": l.action, "target_type": l.target_type, "target_id": l.target_id,
            "detail": l.detail, "ip_address": l.ip_address,
            "created_at": str(l.created_at),
        } for l in logs],
    }}


@router.get("/audit-logs/actions")
def get_audit_actions(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """获取所有操作类型列表（供筛选）"""
    results = db.query(AuditLog.action).distinct().all()
    return {
        "code": 0, "message": "获取成功",
        "data": [r[0] for r in results if r[0]],
    }


# ═══════════════════════════════════════════════════════════════
# 增强统计
# ═══════════════════════════════════════════════════════════════

@router.get("/stats/emotion-trends")
def emotion_trends(days: int = 30,
                   admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """情绪趋势统计"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(EmotionLog.emotion_label, func.count(EmotionLog.id).label("cnt"))
        .filter(EmotionLog.created_at >= cutoff)
        .group_by(EmotionLog.emotion_label)
        .order_by(desc("cnt"))
        .all()
    )
    total = sum(row.cnt for row in logs)
    return {"code": 0, "message": "获取成功", "data": {
        "period_days": days,
        "total_logs": total,
        "distribution": [{
            "emotion": row.emotion_label,
            "count": row.cnt,
            "percentage": round(row.cnt / total * 100, 1) if total > 0 else 0,
        } for row in logs],
    }}


@router.get("/stats/user-growth")
def user_growth(days: int = 30,
                admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """用户增长统计（按天）"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("cnt"),
        )
        .filter(User.created_at >= cutoff)
        .group_by("date")
        .order_by("date")
        .all()
    )
    return {"code": 0, "message": "获取成功", "data": {
        "period_days": days,
        "daily": [{"date": str(row.date), "new_users": row.cnt} for row in rows],
    }}


@router.get("/stats/revenue")
def revenue_stats(days: int = 30,
                  admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """营收统计"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.status.in_(("paid", "shipped", "completed")), Order.created_at >= cutoff)
        .scalar()
    ) or 0

    daily_rows = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("amount"),
        )
        .filter(Order.status.in_(("paid", "shipped", "completed")), Order.created_at >= cutoff)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return {"code": 0, "message": "获取成功", "data": {
        "period_days": days,
        "total_revenue": float(total_revenue),
        "daily": [{
            "date": str(row.date),
            "orders": row.order_count,
            "revenue": float(row.amount or 0),
        } for row in daily_rows],
    }}


@router.get("/stats/overview")
def stats_overview(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """综合统计概览（含本周数据）"""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)

    # 本周 vs 上周
    this_week_users = db.query(func.count(User.id)).filter(User.created_at >= this_week_start).scalar()
    last_week_users = db.query(func.count(User.id)).filter(
        User.created_at >= last_week_start, User.created_at < this_week_start
    ).scalar()

    this_week_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.status.in_(("paid", "shipped", "completed")), Order.created_at >= this_week_start)
        .scalar()
    ) or 0

    most_logged_emotion = (
        db.query(EmotionLog.emotion_label, func.count(EmotionLog.id).label("cnt"))
        .filter(EmotionLog.created_at >= this_week_start)
        .group_by(EmotionLog.emotion_label)
        .order_by(desc("cnt"))
        .first()
    )

    crisis_this_week = db.query(func.count(CrisisAlert.id)).filter(
        CrisisAlert.created_at >= this_week_start
    ).scalar()

    return {"code": 0, "message": "获取成功", "data": {
        "this_week": {
            "new_users": this_week_users,
            "new_users_vs_last_week": this_week_users - last_week_users if last_week_users else this_week_users,
            "revenue": float(this_week_revenue),
            "top_emotion": most_logged_emotion.emotion_label if most_logged_emotion else "暂无数据",
            "crisis_alerts": crisis_this_week,
        },
    }}
