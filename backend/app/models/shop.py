from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint, func, text
)
from sqlalchemy.orm import relationship

from app.database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False, server_default=text("''"))
    icon = Column(String(100), nullable=False, server_default=text("''"))
    sort_order = Column(Integer, nullable=False, server_default=text("0"))

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    category_id = Column(BigInteger, ForeignKey("product_categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    image_url = Column(String(500), nullable=False, server_default=text("''"))
    stock = Column(Integer, nullable=False, server_default=text("0"))
    sales_count = Column(Integer, nullable=False, server_default=text("0"))
    product_type = Column(String(20), nullable=False, server_default=text("'physical'"), comment="physical / service")
    is_on_sale = Column(Integer, nullable=False, server_default=text("1"), comment="0=下架 1=上架")
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    category = relationship("ProductCategory", back_populates="products")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text("1"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    product = relationship("Product")


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    receiver_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    detail = Column(String(200), nullable=False)
    is_default = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    order_no = Column(String(32), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    address_id = Column(BigInteger, ForeignKey("user_addresses.id"), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        String(20), nullable=False, server_default=text("'pending_payment'"),
        comment="pending_payment / paid / shipped / completed / cancelled"
    )
    payment_method = Column(String(20), nullable=False, server_default=text("''"))
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order")
    address = relationship("UserAddress")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    product_image = Column(String(500), nullable=False, server_default=text("''"))
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    order = relationship("Order", back_populates="items")
