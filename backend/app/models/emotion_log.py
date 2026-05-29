from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, func

from app.database import Base


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    emotion_label = Column(String(50), nullable=False)
    intensity = Column(Integer, nullable=False)
    suggestion = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
