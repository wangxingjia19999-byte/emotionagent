from sqlalchemy import BigInteger, Column, DateTime, String, Text, func

from app.database import Base


class CrisisAlert(Base):
    __tablename__ = "crisis_alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    risk_type = Column(String(30), nullable=False)
    risk_level = Column(String(20), nullable=False)
    raw_text = Column(Text, nullable=False)
    guidance = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
