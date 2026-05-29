"""
MCP 知识检索工具

提供 RAG 情绪知识库检索、对话记忆管理等能力。
"""

import os
import sys

_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _base not in sys.path:
    sys.path.insert(0, _base)


def search_knowledge_base(query: str) -> str:
    """
    从情绪陪伴专业知识库中检索相关信息。知识库包含情绪干预策略、
    心理疏导话术和危机应对指导。

    适用场景：
    - 面对用户描述的情绪问题，需要专业的干预策略和话术
    - 查探特定情绪主题（如"如何安抚焦虑的人"）的陪伴指南
    - 作为 AI 回复时的参考资料

    注意：返回的内容是参考资料，不是直接回复用户的话。
    你需要用自己的语气和风格整合这些信息。

    Args:
        query: 检索查询，描述你想查找的情绪主题或具体问题
    """
    from agent.agent_service import query_emotion_knowledge_base as _search
    return _search.invoke({"query": query})


def get_conversation_memory(user_id: str, limit: int = 5) -> str:
    """
    获取用户最近的对话记忆，了解之前聊过什么。

    适用场景：在连续对话中，需要回顾之前的交流内容时调用。

    Args:
        user_id: 用户 ID（数字字符串）
        limit: 返回最近几条记忆，默认 5，最大 20
    """
    from agent.agent_service import get_recent_memory as _memory
    return _memory.invoke({"user_id": user_id, "limit": limit})


def get_questionnaire_history(user_id: str, scale_type: str = "", days: int = 30) -> str:
    """
    查看用户的情绪问卷填写历史，包括 PHQ-9（抑郁筛查）、GAD-7（焦虑筛查）、
    每日快评和自测量表。

    适用场景：想了解用户近期的心理健康测评趋势时调用。

    Args:
        user_id: 用户 ID（数字字符串）
        scale_type: 量表类型筛选。可选: daily_mood, phq9, gad7, self_scale。留空返回全部。
        days: 查看最近多少天，默认 30 天
    """
    from agent.agent_service import get_questionnaire_history as _qh
    return _qh.invoke({
        "user_id": user_id,
        "scale_type": scale_type,
        "days": days,
    })
