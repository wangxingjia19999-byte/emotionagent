import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.shop import CartItem, Order, OrderItem, Product, ProductCategory, UserAddress
from app.models.user import User
from app.schemas.shop import (
    AddressCreate, AddressResponse, AddressUpdate,
    CartItemCreate, CartItemResponse, CartItemUpdate, CartListResponse,
    CategoryResponse,
    OrderCreate, OrderPageResponse, OrderResponse,
    ProductPageResponse, ProductResponse,
)
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/shop", tags=["商城"])


# ═══════════════════════════════════════════════════════════════
# 商品分类
# ═══════════════════════════════════════════════════════════════

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(ProductCategory).order_by(ProductCategory.sort_order).all()
    return {
        "code": 0,
        "message": "获取成功",
        "data": [CategoryResponse.model_validate(c).model_dump() for c in categories],
    }


# ═══════════════════════════════════════════════════════════════
# 商品
# ═══════════════════════════════════════════════════════════════

@router.get("/products")
def list_products(
    category_id: Optional[int] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    sort: str = Query(default="default", description="default / sales / price_asc / price_desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(Product.is_on_sale == 1)

    if category_id:
        q = q.filter(Product.category_id == category_id)
    if keyword:
        q = q.filter(Product.name.contains(keyword))

    if sort == "sales":
        q = q.order_by(desc(Product.sales_count))
    elif sort == "price_asc":
        q = q.order_by(Product.price)
    elif sort == "price_desc":
        q = q.order_by(desc(Product.price))
    else:
        q = q.order_by(desc(Product.sort_order), desc(Product.id))

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "code": 0,
        "message": "获取成功",
        "data": ProductPageResponse(
            items=[ProductResponse.from_orm_model(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump(),
    }


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_on_sale == 1).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return {
        "code": 0,
        "message": "获取成功",
        "data": ProductResponse.from_orm_model(product).model_dump(),
    }


# ═══════════════════════════════════════════════════════════════
# 购物车
# ═══════════════════════════════════════════════════════════════

@router.post("/cart")
def add_to_cart(
    body: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == body.product_id, Product.is_on_sale == 1).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    if product.stock < body.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="库存不足")

    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == body.product_id,
    ).first()

    if existing:
        existing.quantity += body.quantity
        if existing.quantity > product.stock:
            existing.quantity = product.stock
        db.commit()
        db.refresh(existing)
        return {"code": 0, "message": "已更新购物车数量", "data": {"id": existing.id, "quantity": existing.quantity}}

    item = CartItem(user_id=current_user.id, product_id=body.product_id, quantity=body.quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"code": 0, "message": "已加入购物车", "data": {"id": item.id, "quantity": item.quantity}}


@router.get("/cart")
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id)
        .order_by(desc(CartItem.id))
        .all()
    )
    # eagerly load product relationship
    for item in items:
        if item.product_id:
            item.product = db.query(Product).filter(Product.id == item.product_id).first()
    return {
        "code": 0,
        "message": "获取成功",
        "data": CartListResponse(
            items=[CartItemResponse.from_orm_model(i) for i in items]
        ).model_dump(),
    }


@router.put("/cart/{item_id}")
def update_cart_item(
    item_id: int,
    body: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项不存在")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product and body.quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="库存不足")

    item.quantity = body.quantity
    db.commit()
    return {"code": 0, "message": "已更新", "data": {"id": item.id, "quantity": item.quantity}}


@router.delete("/cart/{item_id}")
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项不存在")
    db.delete(item)
    db.commit()
    return {"code": 0, "message": "已移除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 收货地址
# ═══════════════════════════════════════════════════════════════

@router.post("/addresses")
def create_address(
    body: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.is_default:
        db.query(UserAddress).filter(
            UserAddress.user_id == current_user.id, UserAddress.is_default == 1
        ).update({"is_default": 0})

    addr = UserAddress(user_id=current_user.id, **body.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return {"code": 0, "message": "地址已保存", "data": AddressResponse.model_validate(addr).model_dump()}


@router.get("/addresses")
def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addresses = (
        db.query(UserAddress)
        .filter(UserAddress.user_id == current_user.id)
        .order_by(desc(UserAddress.is_default), desc(UserAddress.id))
        .all()
    )
    return {
        "code": 0,
        "message": "获取成功",
        "data": [AddressResponse.model_validate(a).model_dump() for a in addresses],
    }


@router.put("/addresses/{address_id}")
def update_address(
    address_id: int,
    body: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(UserAddress).filter(
        UserAddress.id == address_id, UserAddress.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地址不存在")

    if body.is_default:
        db.query(UserAddress).filter(
            UserAddress.user_id == current_user.id, UserAddress.is_default == 1
        ).update({"is_default": 0})

    for key, value in body.model_dump().items():
        setattr(addr, key, value)
    db.commit()
    db.refresh(addr)
    return {"code": 0, "message": "地址已更新", "data": AddressResponse.model_validate(addr).model_dump()}


@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(UserAddress).filter(
        UserAddress.id == address_id, UserAddress.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地址不存在")
    db.delete(addr)
    db.commit()
    return {"code": 0, "message": "已删除", "data": None}


# ═══════════════════════════════════════════════════════════════
# 订单
# ═══════════════════════════════════════════════════════════════

def _generate_order_no() -> str:
    return uuid.uuid4().hex[:20].upper()


def _check_cart_items(db: Session, user_id: int) -> list[CartItem]:
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="购物车为空")
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.is_on_sale == 1).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"商品已下架，请先移除后再下单")
        if product.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"「{product.name}」库存不足")
    return items


@router.post("/orders")
def create_order(
    body: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = _check_cart_items(db, current_user.id)

    # 检查是否包含实体商品，如果是则需要地址
    has_physical = False
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product.product_type == "physical":
            has_physical = True
        total += float(product.price) * item.quantity

    if has_physical and not body.address_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="实体商品需要填写收货地址")

    if body.address_id:
        addr = db.query(UserAddress).filter(
            UserAddress.id == body.address_id, UserAddress.user_id == current_user.id
        ).first()
        if not addr:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="收货地址不存在")

    order = Order(
        order_no=_generate_order_no(),
        user_id=current_user.id,
        address_id=body.address_id,
        total_amount=total,
        status="pending_payment",
        payment_method=body.payment_method,
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.image_url,
            price=product.price,
            quantity=item.quantity,
        )
        db.add(order_item)

    # 清空购物车中已下单的商品
    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)

    # load relationships
    order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    if order.address_id:
        order.address = db.query(UserAddress).filter(UserAddress.id == order.address_id).first()

    return {"code": 0, "message": "下单成功", "data": OrderResponse.from_orm_model(order).model_dump()}


@router.get("/orders")
def list_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Order).filter(Order.user_id == current_user.id)
    if status_filter:
        q = q.filter(Order.status == status_filter)

    total = q.count()
    orders = q.order_by(desc(Order.id)).offset((page - 1) * page_size).limit(page_size).all()

    for order in orders:
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        if order.address_id:
            order.address = db.query(UserAddress).filter(UserAddress.id == order.address_id).first()

    return {
        "code": 0,
        "message": "获取成功",
        "data": OrderPageResponse(
            items=[OrderResponse.from_orm_model(o) for o in orders],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump(),
    }


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    if order.address_id:
        order.address = db.query(UserAddress).filter(UserAddress.id == order.address_id).first()

    return {"code": 0, "message": "获取成功", "data": OrderResponse.from_orm_model(order).model_dump()}


@router.put("/orders/{order_id}/pay")
def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending_payment":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态不允许支付")

    from datetime import datetime
    order.status = "paid"
    order.paid_at = datetime.now()

    # 增加销量
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.sales_count += item.quantity
            product.stock = max(0, product.stock - item.quantity)

    db.commit()
    db.refresh(order)
    order.items = items
    if order.address_id:
        order.address = db.query(UserAddress).filter(UserAddress.id == order.address_id).first()

    return {"code": 0, "message": "支付成功", "data": OrderResponse.from_orm_model(order).model_dump()}


@router.put("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status not in ("pending_payment", "paid"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不允许取消")

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    if order.address_id:
        order.address = db.query(UserAddress).filter(UserAddress.id == order.address_id).first()

    return {"code": 0, "message": "订单已取消", "data": OrderResponse.from_orm_model(order).model_dump()}
