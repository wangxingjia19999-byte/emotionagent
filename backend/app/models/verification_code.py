from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    email = Column(String(100), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(20), nullable=False, default="register")
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
