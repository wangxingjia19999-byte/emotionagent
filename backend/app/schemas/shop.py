from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── 商品分类 ──────────────────────────────────────────────────
class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str = ""
    icon: str = ""
    sort_order: int = 0


# ── 商品 ──────────────────────────────────────────────────────
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    description: str
    price: float
    original_price: float = 0
    image_url: str = ""
    stock: int = 0
    sales_count: int = 0
    product_type: str = "physical"
    is_on_sale: int = 1
    sort_order: int = 0
    created_at: Optional[datetime] = None

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=obj.id,
            category_id=obj.category_id,
            name=obj.name,
            description=obj.description,
            price=float(obj.price),
            original_price=float(obj.original_price),
            image_url=obj.image_url,
            stock=obj.stock,
            sales_count=obj.sales_count,
            product_type=obj.product_type,
            is_on_sale=obj.is_on_sale,
            sort_order=obj.sort_order,
            created_at=obj.created_at,
        )


class ProductPageResponse(BaseModel):
    items: list[ProductResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10


# ── 购物车 ────────────────────────────────────────────────────
class CartItemCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=obj.id,
            product_id=obj.product_id,
            quantity=obj.quantity,
            product=ProductResponse.from_orm_model(obj.product) if obj.product else None,
        )


class CartListResponse(BaseModel):
    items: list[CartItemResponse] = Field(default_factory=list)


# ── 收货地址 ──────────────────────────────────────────────────
class AddressCreate(BaseModel):
    receiver_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)
    province: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    district: str = Field(..., min_length=1, max_length=50)
    detail: str = Field(..., min_length=1, max_length=200)
    is_default: int = Field(default=0, ge=0, le=1)


class AddressUpdate(AddressCreate):
    pass


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    receiver_name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: int = 0
    created_at: Optional[datetime] = None


# ── 订单 ──────────────────────────────────────────────────────
class OrderCreate(BaseModel):
    address_id: Optional[int] = None
    payment_method: str = Field(default="mock")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    product_name: str
    product_image: str = ""
    price: float
    quantity: int


class OrderResponse(BaseModel):
    id: int
    order_no: str
    user_id: int
    address_id: Optional[int] = None
    total_amount: float
    status: str
    payment_method: str = ""
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: list[OrderItemResponse] = Field(default_factory=list)
    address: Optional[AddressResponse] = None

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=obj.id,
            order_no=obj.order_no,
            user_id=obj.user_id,
            address_id=obj.address_id,
            total_amount=float(obj.total_amount),
            status=obj.status,
            payment_method=obj.payment_method,
            paid_at=obj.paid_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            items=[OrderItemResponse.model_validate(item) for item in obj.items] if obj.items else [],
            address=AddressResponse.model_validate(obj.address) if obj.address else None,
        )


class OrderPageResponse(BaseModel):
    items: list[OrderResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
