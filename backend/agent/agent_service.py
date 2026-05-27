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
            
            print("⏳ 正在初始化 Emotion Analyst Agent...")
            self._agent = EmotionAnalystRAG(
                vector_db_uri=db_path,
                llm_model_name=os.getenv("OPENAI_MODEL_NAME", "qwen-plus")
            )
            print("✅ Emotion Analyst Agent 初始化完成。")

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
