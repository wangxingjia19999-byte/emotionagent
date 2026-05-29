"""
管理员后台 API
所有接口需要 admin 或 super_admin 角色
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.emotion_log import EmotionLog
from app.models.post import Post, Comment
from app.models.questionnaire import QuestionnaireRecord
from app.models.shop import (
    CartItem, Order, OrderItem, Product, ProductCategory, UserAddress,
)
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.admin import Admin
from app.utils.jwt import get_current_admin

router = APIRouter(prefix="/admin", tags=["管理后台"])


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
def delete_product(product_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(p)
    db.commit()
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
def update_order_status(order_id: int, status_val: str,
                        admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="订单不存在")
    o.status = status_val
    db.commit()
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
def update_user(user_id: int, nickname: Optional[str] = None, role: Optional[str] = None,
                status_val: Optional[str] = Query(None, alias="status"),
                admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的管理员权限")
    if nickname is not None:
        user.nickname = nickname
    if role is not None:
        user.role = role
    if status_val is not None:
        user.status = status_val
    db.commit()
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
def delete_post(post_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="帖子不存在")
    p.is_deleted = 1
    db.commit()
    return {"code": 0, "message": "帖子已删除", "data": None}


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="评论不存在")
    c.is_deleted = 1
    db.commit()
    return {"code": 0, "message": "评论已删除", "data": None}
