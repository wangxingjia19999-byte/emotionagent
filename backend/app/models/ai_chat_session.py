"""
AI 聊天会话记录模型

每次用户与 AI 情绪陪伴 Agent 对话时，记录会话信息。
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import relationship

from app.database import Base


class AiChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="", server_default=text("''"))
    agent_used = Column(String(50), nullable=False, default="emotion_companion", server_default=text("'emotion_companion'"))
    message_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    first_message = Column(Text, nullable=True)
    last_message = Column(Text, nullable=True)
    crisis_detected = Column(Integer, nullable=False, default=0, server_default=text("0"))
    messages_json = Column(Text, nullable=True, comment="JSON 格式存储本轮对话 [{\"role\":\"user\",\"content\":\"...\"},{\"role\":\"assistant\",\"content\":\"...\"}]")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
