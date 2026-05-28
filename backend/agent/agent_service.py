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
