import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import time

from .RAG.enterprise_rag_app import EmotionAnalystRAG
from langchain_core.tools import tool

# 确保 backend 在 path 中以便导入 app 模块
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _base_dir not in sys.path:
    sys.path.insert(0, _base_dir)

from app.config import settings as app_settings

class AgentService:
    """
    Agent 服务层，用于与 FastAPI 后端提供单例交互接口。
    避免由于频繁请求重复加载大模型及嵌入模型。
    """
    _instance = None
    _agent = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        """初始化 RAG Agent 和向量库。建议在 FastAPI 的 lifespan/on_event("startup") 中调用。"""
        if self._agent is None:
            # 获取当前文件所在路径作为基础，以保证正确找到本地的 Chroma DB
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "RAG", "chroma_db")
            
            import logging
            logger = logging.getLogger("app")
            logger.info("initializing_emotion_agent")
            self._agent = EmotionAnalystRAG(
                vector_db_uri=db_path,
                llm_model_name=app_settings.openai_model_name
            )
            import logging
            logging.getLogger("app").info("emotion_agent_ready")

    def chat(self, user_input: str) -> str:
        """
        调用情绪分析师 Agent 响应用户的问题。
        """
        if self._agent is None:
            self.initialize()
        return self._agent.analyze_and_respond(user_input)

# 暴露单一实例供 routers 调用
emotion_agent_service = AgentService()

_memory_dir = Path(__file__).resolve().parent / "memory"
_memory_file = _memory_dir / "conversation_memory.jsonl"

def _append_memory(record: dict) -> None:
    _memory_dir.mkdir(parents=True, exist_ok=True)
    with _memory_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _read_memory(user_id: str, limit: int) -> list[dict]:
    if not _memory_file.exists():
        return []
    items = []
    with _memory_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            if record.get("user_id") == user_id:
                items.append(record)
    return items[-limit:]

# --- 提供给智能体 (Agent) 使用的 Tool 封装 ---

@tool
def query_emotion_knowledge_base(query: str) -> str:
    """
    当需要获取情绪干预、心理疏导策略、历史心理咨询对话时，使用此工具检索企业级情绪指导知识库。
    输入参数为用户的具体诉求或心理状态的描述片段。
    工具将返回最匹配的指导建议、干预法则(AVER法则)与话术。
    """
    # 如果服务尚未初始化则初始化
    if emotion_agent_service._agent is None:
        emotion_agent_service.initialize()
    
    # 提取内部的 retriever 直接用来做信息检索，将检索到的上下文合并返回给 Agent 阅读
    retrieved_docs = emotion_agent_service._agent.retriever.invoke(query)
    if not retrieved_docs:
        return "知识库中未能检索到相关的干预指导。"
    
    # 将找到的文档拼接在一起
    doc_strings = [f"参考片段 {i+1}: {doc.page_content}" for i, doc in enumerate(retrieved_docs)]
    return "\n\n".join(doc_strings)


@tool
def emotion_scale_assessment(answers: list[int], scale: str = "brief-4") -> str:
    """
    情绪量表简评工具。answers 为整数列表，取值 0-3，表示无/轻/中/重。
    scale 支持: brief-4。
    """
    if scale != "brief-4":
        return "当前仅支持 brief-4 量表。"

    if not answers or any(a < 0 or a > 3 for a in answers):
        return "量表答案需为 0-3 的整数列表。"

    score = sum(answers)
    if score <= 3:
        level = "轻度"
    elif score <= 7:
        level = "中度"
    else:
        level = "较重"

    return f"量表: brief-4\n总分: {score}\n程度: {level}\n建议: 可结合情绪调节与支持资源进一步评估。"


@tool
def save_conversation_memory(user_id: str, user_text: str, assistant_text: str, tags: str | None = None) -> str:
    """
    保存对话记忆，供后续检索。tags 可填: 情绪标签/主题/风险提示。
    """
    record = {
        "user_id": user_id,
        "user_text": user_text,
        "assistant_text": assistant_text,
        "tags": tags,
        "ts": int(time())
    }
    _append_memory(record)
    return "记忆已保存。"


@tool
def get_recent_memory(user_id: str, limit: int = 5) -> str:
    """
    读取最近对话记忆，limit 默认 5。
    """
    items = _read_memory(user_id, max(1, min(limit, 20)))
    if not items:
        return "暂无历史记忆。"

    lines = []
    for i, item in enumerate(items, start=1):
        lines.append(
            f"[{i}] 用户: {item.get('user_text', '')}\n助手: {item.get('assistant_text', '')}\n标签: {item.get('tags', '')}"
        )
    return "\n\n".join(lines)


# --- 用户画像与情绪记录工具 ---


def _get_db_session():
    """获取数据库会话"""
    from app.database import SessionLocal
    return SessionLocal()


@tool
def get_user_profile(user_id: str) -> str:
    """
    查看用户的个人画像信息，包括：昵称、性别、年龄、职业、压力来源等。
    当用户提到工作、学业压力，或需要了解用户背景来提供更个性化的陪伴时使用。
    user_id 为用户ID（数字字符串）。
    """
    from app.models.user import User
    from app.models.user_profile import UserProfile

    db = _get_db_session()
    try:
        uid = int(user_id)
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            return "未找到该用户的信息。"

        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()

        parts = []
        if user.nickname:
            parts.append(f"昵称: {user.nickname}")
        if user.gender:
            parts.append(f"性别: {user.gender}")
        if user.age:
            parts.append(f"年龄: {user.age}岁")
        if user.occupation:
            parts.append(f"职业: {user.occupation}")

        if profile:
            if profile.stressors:
                parts.append(f"压力来源: {profile.stressors}")

        if not parts:
            return "该用户尚未完善个人画像信息。可以引导用户填写，以便提供更贴心的陪伴。"

        return "用户画像:\n" + "\n".join(parts)
    finally:
        db.close()


@tool
def get_emotion_history(user_id: str, days: int = 7) -> str:
    """
    查看用户近期的情绪记录历史，了解情绪变化趋势。
    用于了解用户近期的情绪状态、是否有持续的情绪问题等。
    user_id 为用户ID，days 为查看最近多少天的记录（默认7天）。
    """
    from app.models.emotion_log import EmotionLog

    db = _get_db_session()
    try:
        uid = int(user_id)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        logs = (
            db.query(EmotionLog)
            .filter(
                EmotionLog.user_id == uid,
                EmotionLog.created_at >= cutoff
            )
            .order_by(EmotionLog.created_at.desc())
            .limit(20)
            .all()
        )

        if not logs:
            return "暂无近期的情绪记录。可以在对话中逐步了解用户的情绪状态。"

        lines = [f"最近 {days} 天的情绪记录 (共 {len(logs)} 条):"]
        for log in logs:
            time_str = log.created_at.strftime("%m-%d %H:%M") if log.created_at else "未知时间"
            intensity_bar = "●" * log.intensity + "○" * (5 - log.intensity) if log.intensity else ""
            lines.append(
                f"  [{time_str}] {log.emotion_label} 强度:{intensity_bar} "
                f"{'备注: ' + log.raw_text if log.raw_text else ''}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool
def save_emotion_log(
    user_id: str, emotion_label: str, intensity: int, raw_text: str = ""
) -> str:
    """
    保存用户的情绪记录。在对话结束后或识别到明显情绪时调用，用于追踪用户的情绪变化。
    user_id: 用户ID
    emotion_label: 情绪标签，如 快乐/悲伤/焦虑/愤怒/平静/低落/恐惧/惊讶/孤独/压力
    intensity: 情绪强度 1-5 (1为轻微, 5为强烈)
    raw_text: 用户原始表达的关键内容（可选）
    """
    from app.models.emotion_log import EmotionLog

    db = _get_db_session()
    try:
        log = EmotionLog(
            user_id=int(user_id),
            emotion_label=emotion_label[:50],
            intensity=max(1, min(5, intensity)),
            raw_text=raw_text[:500] if raw_text else None,
        )
        db.add(log)
        db.commit()
        return f"已记录: {emotion_label} (强度 {intensity}/5)"
    finally:
        db.close()


@tool
def get_questionnaire_history(user_id: str, scale_type: str = "", days: int = 30) -> str:
    """
    查看用户的情绪问卷历史记录和趋势。
    当用户提到问卷、测评、最近情绪状态变化，或想要了解自己的情绪趋势时调用。
    user_id: 用户ID
    scale_type: 量表类型，可选值: daily_mood(每日快评)、phq9(抑郁筛查)、gad7(焦虑筛查)，留空则返回所有
    days: 查看最近多少天，默认30天
    """
    from datetime import datetime, timedelta, timezone
    from app.models.questionnaire import QuestionnaireRecord
    from app.schemas.questionnaire import SCALES as _SCALES

    db = _get_db_session()
    try:
        uid = int(user_id)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        query = db.query(QuestionnaireRecord).filter(
            QuestionnaireRecord.user_id == uid,
            QuestionnaireRecord.created_at >= cutoff,
        )
        if scale_type:
            query = query.filter(QuestionnaireRecord.scale_type == scale_type)

        records = query.order_by(QuestionnaireRecord.created_at.desc()).limit(20).all()

        if not records:
            return "该用户近期没有填写过情绪问卷。可以邀请用户进行一次情绪自评。"

        lines = [f"最近 {days} 天的问卷记录 (共 {len(records)} 条):"]
        for r in records:
            scale_name = _SCALES.get(r.scale_type, {}).get("name", r.scale_type)
            time_str = r.created_at.strftime("%m-%d %H:%M") if r.created_at else ""
            lines.append(
                f"  [{time_str}] {scale_name}: 总分{r.total_score}, 等级:{r.result_level}"
            )

        # 简单趋势分析
        if len(records) >= 3:
            recent_scores = [r.total_score for r in records[:5]]
            if recent_scores[0] < recent_scores[-1]:
                lines.append("\n趋势: 近期得分呈上升趋势，情绪状态可能有所恶化，需要更多关注。")
            elif recent_scores[0] > recent_scores[-1]:
                lines.append("\n趋势: 近期得分呈下降趋势，情绪状态可能在好转。")
            else:
                lines.append("\n趋势: 近期得分基本平稳。")

        return "\n".join(lines)
    finally:
        db.close()


# --- 用户活动与社区工具 ---


@tool
def get_user_activity_overview(user_id: str) -> str:
    """
    查看用户在平台上的活动概况，包括：AI聊天次数、发表的帖子数、
    收藏数、未读私信数、好友数。
    当首次接触用户、想了解用户的平台参与度、或需要活动背景时调用。
    user_id 为用户ID（数字字符串）。
    """
    from app.database import SessionLocal
    from sqlalchemy import inspect, text

    db = _get_db_session()
    try:
        uid = int(user_id)
        inspector = inspect(db.get_bind())
        existing_tables = set(inspector.get_table_names())

        def _find_table(candidates):
            for t in candidates:
                if t in existing_tables:
                    return t
            return None

        def _find_column(table_name, candidates):
            columns = {c["name"] for c in inspector.get_columns(table_name)}
            for c in candidates:
                if c in columns:
                    return c
            return None

        def _count(table_candidates, user_col_candidates, extra_filter="", extra_params=None):
            table_name = _find_table(table_candidates)
            if not table_name:
                return 0
            user_col = _find_column(table_name, user_col_candidates)
            if not user_col:
                return 0
            sql = f"SELECT COUNT(*) FROM `{table_name}` WHERE `{user_col}` = :uid"
            params = {"uid": uid}
            if extra_filter:
                sql += f" AND ({extra_filter})"
            if extra_params:
                params.update(extra_params)
            try:
                return int(db.execute(text(sql), params).scalar_one_or_none() or 0)
            except Exception:
                return 0

        # AI 聊天次数
        ai_count = _count(
            ["ai_chat_sessions", "ai_sessions", "chat_sessions", "conversations", "dialogue_sessions"],
            ["user_id", "owner_id", "created_by", "uid", "author_id"],
        )

        # 帖子数
        post_count = _count(
            ["posts", "community_posts", "forum_posts"],
            ["user_id", "owner_id", "created_by", "uid", "author_id"],
        )

        # 收藏数
        fav_count = _count(
            ["favorites", "favorite_posts", "post_favorites", "collections"],
            ["user_id", "owner_id", "created_by", "uid"],
        )

        # 好友数
        friend_count = _count(
            ["friendships", "friend_relations", "friends", "user_friends"],
            ["user_id", "owner_id", "created_by", "uid"],
        )

        # 未读私信数
        pm_table = _find_table(["private_messages", "messages", "chat_messages", "direct_messages"])
        unread_count = 0
        if pm_table:
            receiver_col = _find_column(pm_table, ["receiver_id", "recipient_id", "to_user_id", "user_id"])
            if receiver_col:
                read_col = _find_column(pm_table, ["is_read", "read", "has_read", "read_flag"])
                if read_col:
                    sql = (
                        f"SELECT COUNT(*) FROM `{pm_table}` "
                        f"WHERE `{receiver_col}` = :uid AND COALESCE(`{read_col}`, 0) = 0"
                    )
                    try:
                        unread_count = int(db.execute(text(sql), {"uid": uid}).scalar_one_or_none() or 0)
                    except Exception:
                        unread_count = 0

        parts = ["用户在平台上的活动概况:"]
        parts.append(f"  AI 聊天次数: {ai_count} 次")
        parts.append(f"  发表的帖子: {post_count} 篇")
        parts.append(f"  收藏的帖子: {fav_count} 篇")
        parts.append(f"  好友数量: {friend_count} 人")
        parts.append(f"  未读私信: {unread_count} 条")

        if ai_count == 0 and post_count == 0:
            parts.append("\n提示: 该用户是平台新用户，活动记录较少。可以引导用户开始第一次情绪对话或发表第一篇帖子。")
        if unread_count > 0:
            parts.append(f"\n注意: 用户有 {unread_count} 条未读私信，可能错过了社交互动。")

        return "\n".join(parts)
    finally:
        db.close()


@tool
def get_my_posts(user_id: str, limit: int = 10) -> str:
    """
    查看用户自己发表的帖子列表，了解用户曾分享的内容和当时的心情状态。
    当用户提到"我的帖子"、"我之前写过"、或需要了解用户的分享历史时调用。
    user_id: 用户ID（数字字符串）
    limit: 返回条数，默认10
    """
    from app.models.post import Post

    db = _get_db_session()
    try:
        uid = int(user_id)
        posts = (
            db.query(Post)
            .filter(Post.user_id == uid, Post.is_deleted == False)
            .order_by(Post.created_at.desc())
            .limit(max(1, min(limit, 20)))
            .all()
        )

        if not posts:
            return "你还没有发表过帖子。在社区广场分享你的心情和故事，会得到大家的温暖回应哦～"

        lines = [f"你的帖子 (共展示 {len(posts)} 篇):"]
        for i, p in enumerate(posts, 1):
            mood_str = f" | 心情: {p.mood_tag}" if p.mood_tag else ""
            content_preview = p.content[:150] + "..." if len(p.content) > 150 else p.content
            time_str = p.created_at.strftime("%m-%d %H:%M") if p.created_at else ""
            lines.append(
                f"\n  [{i}] {p.title}{mood_str} | 分类: {p.category}"
                f"\n      {content_preview}"
                f"\n      ❤️{p.like_count} 抱抱{p.hug_count} 评论{p.comment_count} | {time_str}"
            )

        # 分析用户发帖中的情绪模式
        mood_tags = [p.mood_tag for p in posts if p.mood_tag]
        if mood_tags:
            from collections import Counter
            mood_counter = Counter(mood_tags)
            top_moods = mood_counter.most_common(3)
            mood_summary = "、".join(f"{m}({c}次)" for m, c in top_moods)
            lines.append(f"\n心情标签统计: {mood_summary}")

        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_unread_messages(user_id: str) -> str:
    """
    查看用户的未读私信情况，包括未读总数和每条未读消息的发送者及内容。
    当用户提到"消息"、"私信"、"有人找我"、或需要了解未读通知时调用。
    user_id: 用户ID（数字字符串）
    """
    from app.models.friend import PrivateMessage
    from app.models.user import User

    db = _get_db_session()
    try:
        uid = int(user_id)
        messages = (
            db.query(PrivateMessage)
            .filter(
                PrivateMessage.receiver_id == uid,
                PrivateMessage.is_read == False,
            )
            .order_by(PrivateMessage.created_at.desc())
            .limit(10)
            .all()
        )

        if not messages:
            return "你没有未读私信。一切安好～"

        # 按发送者分组统计
        sender_counts = {}
        for msg in messages:
            sender = db.query(User).filter(User.id == msg.sender_id).first()
            sender_name = sender.nickname if sender and sender.nickname else f"用户{msg.sender_id}"
            if sender_name not in sender_counts:
                sender_counts[sender_name] = {"count": 0, "latest": msg}
            sender_counts[sender_name]["count"] += 1

        lines = [f"你有 {len(messages)} 条未读私信:"]
        for sender_name, info in sender_counts.items():
            latest = info["latest"]
            content_preview = latest.content[:80] + "..." if len(latest.content) > 80 else latest.content
            time_str = latest.created_at.strftime("%m-%d %H:%M") if latest.created_at else ""
            lines.append(
                f"\n  来自 {sender_name} ({info['count']}条未读)"
                f"\n  最新: {content_preview}"
                f"\n  时间: {time_str}"
            )

        lines.append("\n提示: 有人关心和陪伴是很温暖的事，记得去看看哦～")
        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_community_square_posts(
    keyword: str = "",
    mood_tag: str = "",
    category: str = "",
    sort: str = "latest",
    limit: int = 10,
) -> str:
    """
    查看社区广场的帖子，了解社区中其他用户的分享和情绪状态。
    这是核心的社区广场内容获取工具，用于分析社区集体情绪氛围。

    使用场景：
    - 用户问"社区最近怎么样"、"大家都在聊什么"
    - 需要了解特定情绪（如"焦虑"、"难过"）的用户在社区中分享了什么
    - 分析社区中某个分类（情绪倾诉/学习生活/人际关系等）的讨论
    - 作为分析用户所在社区情绪氛围的上下文

    keyword: 搜索关键词（在标题和内容中搜索），留空则不搜索
    mood_tag: 心情标签筛选（如 焦虑/难过/开心/愤怒/孤独/温暖/平静），留空则不筛选
    category: 分类筛选（情绪倾诉/学习生活/人际关系/校园日常/其他），留空则不筛选
    sort: 排序方式，latest=最新, hot=最热（点赞+评论+浏览）
    limit: 返回条数，默认10，最大20
    """
    from app.models.post import Post
    from app.models.user import User

    db = _get_db_session()
    try:
        q = db.query(Post).filter(Post.is_deleted == False)

        if keyword:
            q = q.filter(
                (Post.title.contains(keyword)) | (Post.content.contains(keyword))
            )
        if mood_tag:
            q = q.filter(Post.mood_tag == mood_tag)
        if category:
            q = q.filter(Post.category == category)

        if sort == "hot":
            q = q.order_by(
                (Post.like_count + Post.comment_count + Post.view_count).desc(),
                Post.created_at.desc(),
            )
        else:
            q = q.order_by(Post.created_at.desc())

        posts = q.limit(max(1, min(limit, 20))).all()

        if not posts:
            filter_desc = []
            if mood_tag:
                filter_desc.append(f"心情「{mood_tag}」")
            if category:
                filter_desc.append(f"分类「{category}」")
            if keyword:
                filter_desc.append(f"关键词「{keyword}」")
            desc = "、".join(filter_desc) if filter_desc else "广场"
            return f"{desc}下暂无帖子。社区需要你的第一次分享～"

        # 收集心情标签分布
        mood_dist = {}
        for p in posts:
            if p.mood_tag:
                mood_dist[p.mood_tag] = mood_dist.get(p.mood_tag, 0) + 1

        filter_desc_parts = []
        if mood_tag:
            filter_desc_parts.append(f"心情「{mood_tag}」")
        if category:
            filter_desc_parts.append(f"分类「{category}」")
        if keyword:
            filter_desc_parts.append(f"搜索「{keyword}」")
        header = f"社区广场{' - ' + '、'.join(filter_desc_parts) if filter_desc_parts else ''} 帖子 (共展示 {len(posts)} 篇):"

        lines = [header]

        # 心情氛围概览
        if mood_dist:
            mood_lines = []
            for m, c in sorted(mood_dist.items(), key=lambda x: x[1], reverse=True):
                mood_lines.append(f"{m}({c}篇)")
            lines.append(f"心情分布: {', '.join(mood_lines[:5])}")
            lines.append("")

        for i, p in enumerate(posts, 1):
            # 获取作者昵称
            author = db.query(User).filter(User.id == p.user_id).first()
            author_name = author.nickname if author and author.nickname else "匿名用户"
            mood_str = f" | 心情: {p.mood_tag}" if p.mood_tag else ""
            content_preview = p.content[:150] + "..." if len(p.content) > 150 else p.content
            time_str = p.created_at.strftime("%m-%d %H:%M") if p.created_at else ""

            lines.append(
                f"  [{i}] {p.title}{mood_str} | 分类: {p.category}"
                f"\n      作者: {author_name}"
                f"\n      {content_preview}"
                f"\n      ❤️{p.like_count} 抱抱{p.hug_count} 评论{p.comment_count} 浏览{p.view_count} | {time_str}"
            )

        # 社区情绪分析
        if mood_dist:
            total = sum(mood_dist.values())
            negative_moods = {"难过", "焦虑", "愤怒", "孤独", "恐惧", "低落"}
            negative_count = sum(c for m, c in mood_dist.items() if m in negative_moods)
            negative_ratio = negative_count / total if total > 0 else 0

            lines.append("\n--- 社区情绪分析 ---")
            if negative_ratio >= 0.5:
                lines.append(
                    f"注意: 当前展示的帖子中，负面情绪占比 {negative_ratio:.0%}，"
                    f"社区中较多用户正在经历困难情绪，需要更多的温暖和共情。"
                )
            elif negative_ratio >= 0.3:
                lines.append(
                    f"当前展示的帖子中，负面情绪占比 {negative_ratio:.0%}，"
                    f"社区情绪整体偏中性，有部分用户需要关注。"
                )
            else:
                lines.append(
                    f"当前展示的帖子中，负面情绪占比 {negative_ratio:.0%}，"
                    f"社区氛围整体偏积极温暖。"
                )

        return "\n".join(lines)
    finally:
        db.close()


@tool
def publish_community_post(
    user_id: str,
    title: str,
    content: str,
    mood_tag: str = "",
    category: str = "情绪倾诉",
    is_anonymous: bool = False,
) -> str:
    """
    帮用户在社区广场发布一篇帖子。当用户在倾诉中表达了强烈的情绪，
    或 agent 判断发布到社区可以获得更多温暖回应和支持时，可以主动提议使用此工具。

    使用场景：
    - 用户心情低落，agent 帮ta整理心情并发帖寻求社区支持
    - 用户表达了想分享的意愿，agent 代为撰写并发布
    - 作为情绪安抚策略：将内心的感受写出来、发出去，获得社区回应

    重要：使用前应先告知用户，获得许可后再发布。不要擅自代发。

    user_id: 用户ID（数字字符串）
    title: 帖子标题（1-100字）
    content: 帖子正文内容
    mood_tag: 心情标签（开心/难过/焦虑/愤怒/温暖/平静/孤独/恐惧/惊讶/感激）
    category: 分类（情绪倾诉/学习生活/人际关系/校园日常/其他），默认"情绪倾诉"
    is_anonymous: 是否匿名发布，默认False
    """
    from app.models.post import Post

    db = _get_db_session()
    try:
        uid = int(user_id)

        # 验证标题和内容
        title = title.strip()
        content = content.strip()
        if not title or len(title) > 100:
            return "发帖失败：标题需 1-100 个字符。"
        if not content:
            return "发帖失败：内容不能为空。"

        # 验证分类
        allowed_categories = {"情绪倾诉", "学习生活", "人际关系", "校园日常", "其他"}
        if category not in allowed_categories:
            category = "情绪倾诉"

        # 验证心情标签
        allowed_moods = {"开心", "难过", "焦虑", "愤怒", "温暖", "平静", "孤独", "恐惧", "惊讶", "感激"}
        if mood_tag and mood_tag not in allowed_moods:
            mood_tag = ""

        post = Post(
            user_id=uid,
            title=title[:100],
            content=content,
            category=category,
            mood_tag=mood_tag if mood_tag else None,
            is_anonymous=is_anonymous,
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        anonymous_note = "（匿名发布）" if is_anonymous else ""
        mood_note = f" | 心情: {mood_tag}" if mood_tag else ""
        result = (
            f"帖子发布成功！{anonymous_note}\n"
            f"  标题: {post.title}{mood_note}\n"
            f"  分类: {post.category}\n"
            f"  帖子ID: {post.id}\n"
            f"\n你的心情已经分享到社区广场了，相信会有温暖的人来回应你 💙"
        )
        return result
    except Exception as e:
        db.rollback()
        return f"发帖失败: {str(e)}"
    finally:
        db.close()


# --- 面部表情工具 ---


@tool
def get_current_facial_expression(user_id: str) -> str:
    """
    获取用户当前通过摄像头检测到的面部表情。
    当用户在聊天中提到"看看我现在的表情"、"你知道我现在什么表情吗"、
    或任何涉及当前面部状态的询问时调用此工具。
    如果用户没有开启摄像头或未检测到表情，工具会返回相应提示。

    user_id: 用户ID（数字字符串）
    """
    from .facial_expression import get_current_expression

    result = get_current_expression(user_id)
    if result is None:
        return (
            "当前没有检测到用户的面部表情。可能的原因："
            "1) 用户尚未开启摄像头；"
            "2) 摄像头未对准面部；"
            "3) 光线不足导致检测失败。"
            "你可以礼貌地提醒用户开启摄像头或调整位置，例如说："
            "'如果你想让我看看你的表情，可以在聊天窗口打开摄像头哦 📷'"
        )

    # 表情对应的情绪解读
    expression_tips = {
        "neutral": "用户看起来表情平静，情绪状态较为平和。可以自然展开对话。",
        "happy": "用户在笑！嘴角上扬，看起来心情不错。可以分享这份开心，或适当引导更深层的交流。",
        "sad": "用户看起来有些悲伤，嘴角下垂，眉头微蹙。需要更多共情和陪伴，不要急于给出建议，先倾听。",
        "surprised": "用户表情惊讶，眉毛抬高、眼睛睁大。可能看到了意外的信息。",
        "angry": "用户看起来有些愤怒，眉毛压低、眼神紧张。说话要温和、给用户空间，不要火上浇油。",
        "fearful": "用户表情透露出恐惧或紧张。需要安抚和共情，创造安全感。",
        "disgusted": "用户表情有些厌恶或不满。可能需要关注用户的体验，询问是否有什么不适。",
    }

    tip = expression_tips.get(result.label, f"用户当前表情为: {result.label_cn}")

    return (
        f"📷 用户当前面部表情: {result.label_cn} (置信度: {result.confidence:.0%})\n"
        f"解读: {tip}\n"
        f"请自然地将此信息融入对话中，不需要生硬地汇报检测结果。"
        f"例如可以根据表情调整你的语气和回应策略。"
    )


# --- 商城与推荐工具 ---


@tool
def get_shop_categories() -> str:
    """
    获取商城所有商品分类列表。
    当用户提到想买东西、想购物、问有什么商品类别、或者想通过购物缓解情绪时调用。
    返回分类名称和描述，帮助了解商城有哪些类型的商品。
    """
    from app.models.shop import ProductCategory

    db = _get_db_session()
    try:
        categories = db.query(ProductCategory).order_by(ProductCategory.sort_order).all()
        if not categories:
            return "商城暂无分类。"
        lines = ["商城商品分类:"]
        for c in categories:
            lines.append(f"  [{c.id}] {c.name} - {c.description}")
        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_shop_products(
    category_id: str = "",
    keyword: str = "",
    sort: str = "default",
    limit: int = 10,
) -> str:
    """
    获取商城商品列表。支持按分类、关键词搜索、排序。
    当用户想浏览商品、搜索特定商品、或需要根据用户情绪推荐商品时调用。
    category_id: 分类ID（数字字符串），留空则返回所有分类的商品
    keyword: 搜索关键词，按商品名称搜索
    sort: 排序方式，可选 default(默认)/sales(销量)/price_asc(价格升序)/price_desc(价格降序)
    limit: 返回数量上限，默认10
    """
    from app.models.shop import Product

    db = _get_db_session()
    try:
        q = db.query(Product).filter(Product.is_on_sale == 1)

        if category_id:
            q = q.filter(Product.category_id == int(category_id))
        if keyword:
            q = q.filter(Product.name.contains(keyword))

        if sort == "sales":
            q = q.order_by(Product.sales_count.desc())
        elif sort == "price_asc":
            q = q.order_by(Product.price)
        elif sort == "price_desc":
            q = q.order_by(Product.price.desc())
        else:
            q = q.order_by(Product.sort_order, Product.id.desc())

        products = q.limit(max(1, min(limit, 20))).all()

        if not products:
            return "没有找到符合条件的商品。可以换个关键词或分类试试。"

        lines = ["商品列表:"]
        for p in products:
            cat_name = p.category.name if p.category else "未分类"
            ptype = "服务" if p.product_type == "service" else "实物"
            lines.append(
                f"  [{p.id}] {p.name} | 分类:{cat_name} | 价格:¥{float(p.price):.2f} "
                f"(原价:¥{float(p.original_price):.2f}) | 类型:{ptype} | 销量:{p.sales_count}\n"
                f"      描述: {p.description[:120]}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool
def recommend_shop_products(user_id: str, emotion_label: str = "", limit: int = 5) -> str:
    """
    根据用户的情绪状态推荐商城商品。这是核心推荐工具。
    先分析用户近期的情绪记录和问卷结果，再结合商城商品进行个性化推荐。
    当用户表达情绪困扰、问"有没有什么推荐的"、或想要通过购物来缓解情绪时使用。
    user_id: 用户ID
    emotion_label: 当前情绪标签（如焦虑/悲伤/压力/低落/愤怒/孤独），留空则自动从历史记录推断
    limit: 推荐数量，默认5
    """
    from app.models.emotion_log import EmotionLog
    from app.models.questionnaire import QuestionnaireRecord
    from app.models.shop import Product, ProductCategory
    from app.schemas.questionnaire import SCALES as _SCALES

    db = _get_db_session()
    try:
        uid = int(user_id)

        # 1. 收集用户情绪数据
        recent_logs = (
            db.query(EmotionLog)
            .filter(EmotionLog.user_id == uid)
            .order_by(EmotionLog.created_at.desc())
            .limit(10)
            .all()
        )

        recent_questionnaire = (
            db.query(QuestionnaireRecord)
            .filter(QuestionnaireRecord.user_id == uid)
            .order_by(QuestionnaireRecord.created_at.desc())
            .first()
        )

        # 2. 分析情绪状态
        analysis_parts = []

        if recent_logs:
            emotion_counts: dict[str, int] = {}
            for log in recent_logs:
                label = log.emotion_label
                emotion_counts[label] = emotion_counts.get(label, 0) + 1
            top_emotion = max(emotion_counts, key=emotion_counts.get)
            if not emotion_label:
                emotion_label = top_emotion
            analysis_parts.append(
                f"近期主要情绪: {top_emotion} (共{len(recent_logs)}条记录中占{emotion_counts[top_emotion]}次)"
            )
        else:
            analysis_parts.append("暂无情绪记录")

        if recent_questionnaire:
            scale_name = _SCALES.get(recent_questionnaire.scale_type, {}).get(
                "name", recent_questionnaire.scale_type
            )
            analysis_parts.append(
                f"最近问卷: {scale_name}，得分{recent_questionnaire.total_score}，等级:{recent_questionnaire.result_level}"
            )

        # 3. 情绪 → 分类映射
        emotion_category_map: dict[str, list[str]] = {
            "焦虑": ["解压玩具", "香薰好物", "解压服务"],
            "悲伤": ["身心好物", "香薰好物", "解压服务"],
            "压力": ["解压玩具", "解压服务", "身心好物"],
            "低落": ["身心好物", "香薰好物", "解压玩具"],
            "愤怒": ["解压玩具", "解压服务"],
            "孤独": ["身心好物", "解压服务", "香薰好物"],
            "恐惧": ["身心好物", "香薰好物"],
            "惊讶": ["解压玩具", "身心好物"],
            "平静": ["香薰好物", "身心好物", "解压玩具"],
        }

        target_categories = emotion_category_map.get(emotion_label, ["解压玩具", "香薰好物", "身心好物"])

        # 4. 根据分类查询商品
        recommendations = []
        for cat_name in target_categories:
            if len(recommendations) >= limit:
                break
            category = db.query(ProductCategory).filter(ProductCategory.name == cat_name).first()
            if not category:
                continue
            products = (
                db.query(Product)
                .filter(
                    Product.category_id == category.id,
                    Product.is_on_sale == 1,
                )
                .order_by(Product.sales_count.desc())
                .limit(3)
                .all()
            )
            for p in products:
                if len(recommendations) >= limit:
                    break
                if p.id not in [r["id"] for r in recommendations]:
                    recommendations.append({
                        "id": p.id,
                        "name": p.name,
                        "category": cat_name,
                        "price": float(p.price),
                        "original_price": float(p.original_price),
                        "description": p.description[:150],
                        "sales_count": p.sales_count,
                        "product_type": p.product_type,
                    })

        if not recommendations:
            return "暂时没有适合的推荐商品。"

        # 5. 构建推荐回复
        emotion_cn_map = {
            "焦虑": "焦虑的时候，给自己一些安抚和掌控感会很有帮助",
            "悲伤": "悲伤的时候，温柔的自我照料是最好的礼物",
            "压力": "压力大的时候，适当地给身心放个假很重要",
            "低落": "情绪低落时，一些温暖的小物件可以带来安慰",
            "愤怒": "愤怒需要出口，捏一捏揉一揉会好很多",
            "孤独": "感到孤独的时候，送自己一份陪伴和温暖",
            "恐惧": "害怕的时候，创造安全感是最好的疗愈",
            "平静": "保持这份平静，选些好物来滋养自己",
        }

        intro = emotion_cn_map.get(emotion_label, "根据你当前的情绪状态，为你推荐以下商品")

        lines = ["=" * 40]
        lines.append("个性化推荐")
        lines.append("=" * 40)
        lines.append("\n【情绪分析】")
        lines.extend(analysis_parts)
        lines.append(f"\n推荐理由: {intro}")
        lines.append(f"\n【为你推荐以下 {len(recommendations)} 件商品】")

        for i, item in enumerate(recommendations, 1):
            ptype = "服务" if item["product_type"] == "service" else "实物"
            lines.append(
                f"\n  {i}. [{item['category']}] {item['name']}\n"
                f"     价格: ¥{item['price']:.2f} (原价 ¥{item['original_price']:.2f}) | {ptype}\n"
                f"     {item['description']}"
            )

        lines.append(
            "\n提示: 以上推荐基于你的情绪状态和商品销量综合考量。"
        )

        return "\n".join(lines)
    finally:
        db.close()
