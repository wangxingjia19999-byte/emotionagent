"""
MCP 情绪数据资源

将用户情绪记录、知识库内容等以 Resource 形式暴露，
客户端可以通过 resource URI 直接读取结构化的情绪数据。
"""

import os
import sys

_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _base not in sys.path:
    sys.path.insert(0, _base)


def get_emotion_summary(user_id: str) -> str:
    """
    获取用户的情绪摘要信息，整合近期情绪记录、问卷结果和用户画像。

    Resource URI: emotion://users/{user_id}/summary

    返回格式化的文本摘要，包含：
    - 用户基本信息（昵称、年龄等）
    - 近 7 天情绪记录概况
    - 最近一次问卷评估结果
    """
    from datetime import datetime, timedelta, timezone

    from app.models.emotion_log import EmotionLog
    from app.models.questionnaire import QuestionnaireRecord
    from app.models.user import User
    from app.models.user_profile import UserProfile
    from app.schemas.questionnaire import SCALES as _SCALES
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        uid = int(user_id)
    except ValueError:
        return "user_id 必须为数字"

    try:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            return f"未找到用户 ID={user_id} 的信息。"

        lines = ["# 用户情绪摘要", ""]

        # 基本信息
        lines.append("## 基本信息")
        lines.append(f"- 昵称: {user.nickname or '未设置'}")
        if user.gender:
            lines.append(f"- 性别: {user.gender}")
        if user.age:
            lines.append(f"- 年龄: {user.age}岁")
        if user.occupation:
            lines.append(f"- 职业: {user.occupation}")

        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
        if profile and profile.stressors:
            lines.append(f"- 压力来源: {profile.stressors}")
        lines.append("")

        # 近期情绪记录
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        logs = (
            db.query(EmotionLog)
            .filter(EmotionLog.user_id == uid, EmotionLog.created_at >= cutoff)
            .order_by(EmotionLog.created_at.desc())
            .limit(10)
            .all()
        )
        lines.append("## 近 7 天情绪记录")
        if logs:
            for log in logs:
                time_str = log.created_at.strftime("%m-%d %H:%M") if log.created_at else "未知"
                intensity_bar = "●" * log.intensity + "○" * (5 - log.intensity) if log.intensity else ""
                note = f" — {log.raw_text}" if log.raw_text else ""
                lines.append(f"- [{time_str}] {log.emotion_label} {intensity_bar}{note}")
        else:
            lines.append("暂无记录")
        lines.append("")

        # 最近问卷
        qr = (
            db.query(QuestionnaireRecord)
            .filter(QuestionnaireRecord.user_id == uid)
            .order_by(QuestionnaireRecord.created_at.desc())
            .first()
        )
        lines.append("## 最近问卷评估")
        if qr:
            scale_name = _SCALES.get(qr.scale_type, {}).get("name", qr.scale_type)
            time_str = qr.created_at.strftime("%Y-%m-%d %H:%M") if qr.created_at else ""
            lines.append(f"- 量表: {scale_name}")
            lines.append(f"- 时间: {time_str}")
            lines.append(f"- 总分: {qr.total_score}")
            lines.append(f"- 等级: {qr.result_level}")
        else:
            lines.append("暂无问卷记录")

        return "\n".join(lines)
    finally:
        db.close()


def get_knowledge_topic(topic: str) -> str:
    """
    获取特定情绪主题的知识摘要。从 RAG 知识库中检索并按主题返回。

    Resource URI: emotion://knowledge/{topic}

    Args:
        topic: 情绪主题，如 anxiety（焦虑）、depression（抑郁）、stress（压力）、
               anger（愤怒）、loneliness（孤独）、selfcare（自我关怀）、
               crisis（危机干预）、communication（沟通技巧）
    """
    from agent.agent_service import query_emotion_knowledge_base as _search

    # 主题 → 中文查询映射
    topic_map = {
        "anxiety": "焦虑情绪干预陪伴策略和话术",
        "depression": "抑郁低落情绪的陪伴方法和干预策略",
        "stress": "压力缓解的陪伴方式和减压策略",
        "anger": "愤怒情绪的管理和安抚陪伴方法",
        "loneliness": "孤独感的陪伴方式和社交支持策略",
        "selfcare": "自我关怀和情绪调节的方法和技巧",
        "crisis": "心理危机干预话术和应对策略",
        "communication": "情绪陪伴中的共情沟通技巧和话术",
    }

    query = topic_map.get(topic, topic)
    return _search.invoke({"query": query})
