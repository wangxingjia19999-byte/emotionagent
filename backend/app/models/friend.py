from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import relationship

from app.database import Base


class FriendRequest(Base):
    __tablename__ = "friend_requests"
    __table_args__ = (
        UniqueConstraint("from_user_id", "to_user_id", name="uq_friend_request_from_to"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    from_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default=text("'pending'"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_friendship_user_friend"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    friend_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])


class PrivateMessage(Base):
    __tablename__ = "private_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
