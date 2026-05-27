from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, func

from app.database import Base


class QuestionnaireRecord(Base):
    """每日情绪问卷记录"""

    __tablename__ = "questionnaire_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    scale_type = Column(String(50), nullable=False, comment="量表类型: daily_mood / phq9 / gad7")
    answers = Column(Text, nullable=False, comment="JSON 格式的答案数组")
    total_score = Column(Integer, nullable=False, comment="总分")
    result_level = Column(String(30), nullable=False, comment="结果等级: 良好/轻度/中度/较重/重度")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
