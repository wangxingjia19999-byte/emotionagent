"""
MCP 情绪分析工具

提供情绪文本分析、量表评估、用户画像查询、情绪历史、
商城推荐等核心能力，复用现有 agent_service 的业务逻辑。
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# 确保 backend 在 path 中
_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _base not in sys.path:
    sys.path.insert(0, _base)


def analyze_emotion(text: str) -> str:
    """
    分析文本中蕴含的情绪状态。输入一段用户描述的文字，
    返回情绪标签、强度评估和陪伴建议。

    适用场景：你想了解一段文字中表达了什么情绪时调用。

    Args:
        text: 用户输入的文本内容，描述其当前感受或经历
    """
    if not text.strip():
        return "请提供需要分析的文本内容。"

    from agent.agent_service import emotion_agent_service

    try:
        emotion_agent_service.initialize()
        result = emotion_agent_service._agent.analyze_and_respond(text)
        return result
    except Exception as e:
        # 回退：只做基础检索
        from agent.agent_service import query_emotion_knowledge_base
        return query_emotion_knowledge_base.invoke({"query": text})


def emotion_assessment(answers: list[int], scale: str = "brief-4") -> str:
    """
    情绪量表简评工具。传入一组 0-3 的答案（0=无,1=轻度,2=中度,3=重度），
    返回总分、程度等级和后续建议。

    适用场景：用户完成情绪自评问卷后，需要得到评分结果和解释时调用。

    Args:
        answers: 整数列表，每个值 0-3，表示 无/轻/中/重
        scale: 量表类型，目前支持 "brief-4"（4题简评）
    """
    from agent.agent_service import emotion_scale_assessment as _assessment
    result = _assessment.invoke({"answers": answers, "scale": scale})
    return result


def get_user_profile(user_id: str) -> str:
    """
    获取用户在"心语陪伴"平台上的个人画像信息，包括昵称、性别、年龄、职业、
    压力来源等背景资料。

    适用场景：需要了解用户的背景来提供更有针对性的情绪支持时调用。

    Args:
        user_id: 用户 ID（数字字符串，如 "1"、"42"）
    """
    from agent.agent_service import get_user_profile as _profile
    return _profile.invoke({"user_id": user_id})


def get_emotion_history(user_id: str, days: int = 7) -> str:
    """
    查看用户近期的情绪记录历史，了解情绪变化轨迹。

    适用场景：
    - 想了解用户最近一段时间的情绪波动模式
    - 在对话前了解用户之前的情绪状态作为上下文

    Args:
        user_id: 用户 ID（数字字符串）
        days: 查看最近多少天的记录，默认 7 天
    """
    from agent.agent_service import get_emotion_history as _history
    return _history.invoke({"user_id": user_id, "days": days})


def recommend_products(user_id: str, emotion_label: str = "", limit: int = 5) -> str:
    """
    根据用户的情绪状态，从商城推荐适合的减压/陪伴商品。

    适用场景：
    - 用户表达情绪困扰（焦虑/悲伤/压力/低落等）
    - 用户主动寻求"有什么推荐的"购物建议
    - 作为情绪安抚策略的一部分推荐商品

    Args:
        user_id: 用户 ID（数字字符串）
        emotion_label: 当前情绪标签（焦虑/悲伤/压力/低落/愤怒/孤独/恐惧/平静）。
                       留空则从近期记录自动推断。
        limit: 推荐数量上限，默认 5
    """
    from agent.agent_service import recommend_shop_products as _recommend
    return _recommend.invoke({
        "user_id": user_id,
        "emotion_label": emotion_label,
        "limit": limit,
    })
