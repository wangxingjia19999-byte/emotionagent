from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="其他", server_default=text("'其他'"))
    image_url = Column(String(255), nullable=True)
    image_urls = Column(Text, nullable=True)
    view_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    like_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    comment_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    favorite_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    author = relationship("User")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    post = relationship("Post")
    author = relationship("User")


class PostLike(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_likes_post_id_user_id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post")
    author = relationship("User")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_favorites_post_id_user_id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post")
    author = relationship("User")