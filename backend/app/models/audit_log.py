from sqlalchemy import BigInteger, Column, DateTime, String, Text, func

from app.database import Base


class AuditLog(Base):
    """操作审计日志"""

    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    action = Column(String(50), nullable=False, comment="操作类型: delete_post/delete_comment/remove_friend/admin_disable_user/...")
    target_type = Column(String(50), nullable=False, comment="操作对象类型: post/comment/friendship/user")
    target_id = Column(BigInteger, nullable=False, comment="操作对象 ID")
    detail = Column(Text, nullable=True, comment="操作详情 JSON")
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
