from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    age = Column(Integer, nullable=True)
    occupation = Column(String(100), nullable=True)
    stressors = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
