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


def get_user_activity_overview(user_id: str) -> str:
    """
    获取用户在平台上的活动概况，包括：AI 聊天次数、发表的帖子数、
    收藏数、未读私信数和好友数。

    适用场景：
    - 首次接触用户时了解其平台参与度
    - 用户询问"我的数据"、"我的活动"时
    - 作为对话前的用户背景了解

    Args:
        user_id: 用户 ID（数字字符串）
    """
    from agent.agent_service import get_user_activity_overview as _overview
    return _overview.invoke({"user_id": user_id})


def get_my_posts(user_id: str, limit: int = 10) -> str:
    """
    查看用户自己发表的帖子列表，包括标题、内容预览、心情标签、互动数据。

    适用场景：
    - 用户提到"我的帖子"、"我之前分享过"
    - 了解用户的历史分享和心情变化
    - 分析用户通过帖子自我表达的情绪模式

    Args:
        user_id: 用户 ID（数字字符串）
        limit: 返回条数，默认 10，最大 20
    """
    from agent.agent_service import get_my_posts as _posts
    return _posts.invoke({"user_id": user_id, "limit": limit})


def get_unread_messages(user_id: str) -> str:
    """
    查看用户的未读私信，包括未读总数、每条消息的发送者和内容预览。

    适用场景：
    - 用户问"有人找我吗"、"有消息吗"
    - 检查用户是否错过了社交互动
    - 了解用户近期收到的关心和联系

    Args:
        user_id: 用户 ID（数字字符串）
    """
    from agent.agent_service import get_unread_messages as _unread
    return _unread.invoke({"user_id": user_id})


def get_community_square_posts(
    keyword: str = "",
    mood_tag: str = "",
    category: str = "",
    sort: str = "latest",
    limit: int = 10,
) -> str:
    """
    查看社区广场的帖子，了解社区中其他用户的分享和情绪状态。
    可以按关键词、心情标签、分类筛选，支持最新/最热排序。

    适用场景：
    - 用户问"社区最近怎么样"、"大家都在聊什么"
    - 了解特定情绪（如"焦虑"、"难过"）的社区用户分享
    - 分析社区集体情绪氛围
    - 在对话中引入"社区中也有其他人经历了类似的感受"来减轻用户孤独感

    Args:
        keyword: 搜索关键词（搜索标题和内容），留空则不搜索
        mood_tag: 心情标签筛选（如 焦虑/难过/开心/愤怒/孤独/温暖/平静），留空则不筛选
        category: 分类筛选（情绪倾诉/学习生活/人际关系/校园日常/其他），留空则不筛选
        sort: 排序方式，latest=最新，hot=最热
        limit: 返回条数，默认 10，最大 20
    """
    from agent.agent_service import get_community_square_posts as _community
    return _community.invoke({
        "keyword": keyword,
        "mood_tag": mood_tag,
        "category": category,
        "sort": sort,
        "limit": limit,
    })


def publish_community_post(
    user_id: str,
    title: str,
    content: str,
    mood_tag: str = "",
    category: str = "情绪倾诉",
    is_anonymous: bool = False,
) -> str:
    """
    帮用户在社区广场发布一篇帖子，将心情分享给社区。

    适用场景：
    - 用户心情低落，agent 帮ta整理心情并发帖寻求社区支持
    - 用户想分享感受，agent 代为撰写并发布
    - 作为情绪安抚策略：将内心感受写出来获得社区回应

    ⚠️ 使用前必须先告知用户并获得许可，不要擅自代发。

    Args:
        user_id: 用户 ID（数字字符串）
        title: 帖子标题（1-100字）
        content: 帖子正文
        mood_tag: 心情标签（开心/难过/焦虑/愤怒/温暖/平静/孤独/恐惧/惊讶/感激）
        category: 分类（情绪倾诉/学习生活/人际关系/校园日常/其他），默认"情绪倾诉"
        is_anonymous: 是否匿名发布，默认 False
    """
    from agent.agent_service import publish_community_post as _publish
    return _publish.invoke({
        "user_id": user_id,
        "title": title,
        "content": content,
        "mood_tag": mood_tag,
        "category": category,
        "is_anonymous": is_anonymous,
    })


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
