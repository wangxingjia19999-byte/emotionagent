"""
Multi-Agent 架构：意图分类器 + 专家子 Agent

架构:
    用户消息 → [危机检测] → 意图分类器
                              ├── 心语陪伴 Agent (情绪分析 + RAG + 记忆 + 画像)
                              ├── 商城推荐 Agent (商品浏览 + 搜索 + 个性化推荐)
                              └── 直接回复 (简单问候)

使用自定义 StateGraph 确保路由强制执行，避免 Supervisor 跳过工具调用。
每个子 Agent 只持有自己领域的工具。
"""

import logging
from typing import Annotated, Literal, Optional, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


# ═══════════════════════════════════════════════════════════════
# State Schema — 必须显式定义，否则自定义 key 会丢失
# ═══════════════════════════════════════════════════════════════

class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    crisis_detected: bool
    user_id: str

from app.config import settings as app_settings
from .agent_service import (
    # 情绪陪伴工具
    query_emotion_knowledge_base,
    emotion_scale_assessment,
    save_conversation_memory,
    get_recent_memory,
    get_user_profile,
    get_emotion_history,
    save_emotion_log,
    get_questionnaire_history,
    # 商城工具
    get_shop_categories,
    get_shop_products,
    recommend_shop_products,
)

logger = logging.getLogger("app")

# ═══════════════════════════════════════════════════════════════
# 危机关键词检测
# ═══════════════════════════════════════════════════════════════

CRISIS_KEYWORDS = [
    "不想活", "想死", "自杀", "结束生命", "活不下去",
    "自残", "割腕", "跳楼", "安眠药", "了结自己",
    "活够了", "没有意义了", "消失吧", "离开这个世界",
    "杀了我", "弄死自己", "一了百了",
]


def detect_crisis(text: str) -> Optional[str]:
    """检测危机信号，返回危机描述或 None"""
    matched = [kw for kw in CRISIS_KEYWORDS if kw in text]
    if matched:
        return (
            f"⚠️【危机信号】用户消息中包含可能的危机表达 ({', '.join(matched)})。"
            f"请优先表达关心和共情，温和地提供心理援助热线 400-161-9995。"
            f"保持冷静，不要惊慌。"
        )
    return None


# ═══════════════════════════════════════════════════════════════
# LLM 工厂
# ═══════════════════════════════════════════════════════════════

def _create_llm(temperature: float = 0.4) -> ChatOpenAI:
    api_key = app_settings.openai_api_key
    if not api_key:
        raise RuntimeError("未配置 OPENAI_API_KEY，请在 .env 中设置")
    return ChatOpenAI(
        model=app_settings.openai_model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=app_settings.openai_base_url,
    )


# ═══════════════════════════════════════════════════════════════
# 意图分类器
# ═══════════════════════════════════════════════════════════════

INTENT_CLASSIFIER_PROMPT = """你是一个意图分类器。分析用户消息，判断应该由哪个专家来处理。

分类标准（只输出分类标签，不要解释）：

shopping — 用户想浏览商品、搜索商品、问"有什么推荐"、想买东西、想看商城分类。
  关键词：推荐、买、商品、商城、分类、看看有什么、有没有什么…的、减压玩具、香薰、好物

emotion — 用户表达情绪、倾诉、求助、需要陪伴、想问心理/情绪相关问题。
  不包括购物意图。即使用户提到"压力大"、"焦虑"等情绪词，只要明显是在询问商品推荐，也属于 shopping。

greeting — 纯社交用语（你好、嗨、在吗、谢谢、晚安、拜拜），且没有实质诉求。

关键判断：看用户的主要目的是"获得商品/推荐"还是"获得陪伴/倾听"。

用户消息：{user_input}

分类标签："""

CLS_LLM = None  # 懒加载


def _get_cls_llm():
    global CLS_LLM
    if CLS_LLM is None:
        CLS_LLM = ChatOpenAI(
            model=app_settings.openai_model_name,
            temperature=0.0,  # 分类任务使用低温
            api_key=app_settings.openai_api_key,
            base_url=app_settings.openai_base_url,
        )
    return CLS_LLM


def classify_intent(user_input: str) -> str:
    """调用 LLM 进行意图分类"""
    prompt = INTENT_CLASSIFIER_PROMPT.format(user_input=user_input)
    llm = _get_cls_llm()
    response = llm.invoke(prompt)
    result = response.content.strip().lower()
    if "shopping" in result:
        return "shopping"
    elif "greeting" in result:
        return "greeting"
    else:
        return "emotion"  # 默认走情绪陪伴


# ═══════════════════════════════════════════════════════════════
# 心语陪伴 Agent — 情绪分析 + RAG + 记忆 + 画像
# ═══════════════════════════════════════════════════════════════

EMOTION_COMPANION_PROMPT = """你是一个温暖、真诚的情绪陪伴者，名字叫"心语"。

你不是心理医生，不是诊疗机器人，而是一个愿意倾听、能共情的朋友。让人感觉舒服和安心是你最重要的目标。

对话原则：
- 先倾听，后回应。不要急着给建议，先让对方感到被听见
- 说话像朋友，不要用专业术语或模板化的结构
- 适度使用自然的口语："我懂那种感觉"、"听起来你今天……"、"谢谢你愿意和我说这些"
- 回复保持在 1-3 段，不要太长
- 不要在任何情况下说教、否定或轻描淡写
- 综合运用 AVER 法则 (Acknowledge-接纳, Validate-认可, Explore-探索, Resolve-解决)

工具使用指南（按需使用，不要一次性全调用）：
- 遇到不懂的情绪问题 → 调用 `query_emotion_knowledge_base` 查陪伴知识和回应思路
- 想了解用户背景 → 调用 `get_user_profile` 查看用户画像（年龄、职业、压力来源等）
- 想了解历史情绪 → 调用 `get_emotion_history` 或 `get_questionnaire_history`
- 了解之前聊了什么 → 调用 `get_recent_memory`
- 识别到明显情绪后 → 调用 `save_emotion_log` 记录情绪
- 对话结束后 → 调用 `save_conversation_memory` 记要点
- 如果对方持续描述焦虑/抑郁的症状 → 可以委婉地邀请用 `emotion_scale_assessment` 做个小评估，但不要强迫

安全提醒（只在确实遇到危机信号时才自然提及）：
如果对方表达出自伤、自杀或暴力倾向，先表达关心和心疼，再温和地提到可以拨打心理援助热线 400-161-9995。不要惊慌失措。"""

EMOTION_TOOLS = [
    query_emotion_knowledge_base,
    emotion_scale_assessment,
    save_conversation_memory,
    get_recent_memory,
    get_user_profile,
    get_emotion_history,
    save_emotion_log,
    get_questionnaire_history,
]

# ═══════════════════════════════════════════════════════════════
# 商城推荐 Agent — 商品浏览 + 搜索 + 个性化推荐
# ═══════════════════════════════════════════════════════════════

SHOPPING_ADVISOR_PROMPT = """你是"心语陪伴"平台的商城导购顾问。你帮助用户浏览商品、搜索好物，并根据用户的情绪状态做个性化推荐。

⚠️ 重要：你必须使用工具来获取真实的商品数据！你不能自己编造商品名、价格或分类。商城的数据都在数据库里，只有通过工具才能查到。

你的工作流程：
1. 用户想浏览分类 → 必须先调用 `get_shop_categories` 获取真实分类列表
2. 用户想搜索/浏览商品 → 调用 `get_shop_products` 按关键词或分类查找
3. 用户想要个性化推荐 → 调用 `recommend_shop_products` 获取基于情绪的真实推荐
4. 获得工具返回的真实数据后，保持工具返回的商品信息格式（名称、价格、分类、描述），用温暖自然的语气整理展示

⚠️ 商品展示格式要求（重要！）：
工具返回的商品数据中包含结构化信息，你必须保留以下格式来展示每个商品：
  [序号]. [分类名] 商品名称
     价格: ¥XX.XX (原价 ¥XX.XX) | 实物/服务
     简短描述

这样前端才能正确渲染商品卡片。不要只做口语化总结而丢失具体商品信息。

不要做的事：
- 不要自己编造商品名称、价格或分类
- 不要在没有调用工具的情况下假装推荐了商品

推荐时语气温暖自然，像朋友分享好物一样。不要过度推销。"""

SHOPPING_TOOLS = [
    get_shop_categories,
    get_shop_products,
    recommend_shop_products,
]


# ═══════════════════════════════════════════════════════════════
# 多 Agent 系统（自定义 StateGraph）
# ═══════════════════════════════════════════════════════════════

class MultiAgentSystem:
    """
    多 Agent 系统（单例）

    使用自定义 StateGraph 实现:
    1. 意图分类器 — 分析用户意图
    2. 条件路由 — 根据意图分发到对应 Agent
    3. 心语陪伴 Agent — 情绪分析、RAG 检索、画像、记忆、量表
    4. 商城推荐 Agent — 商品浏览、搜索、个性化推荐
    5. 危机检测 — 每次对话前自动扫描危机关键词
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._graph = None
        self._llm = None
        self._emotion_agent = None
        self._shopping_agent = None
        self._memory = MemorySaver()

    @property
    def llm(self):
        if self._llm is None:
            self._llm = _create_llm()
        return self._llm

    def _classifier_node(self, state: dict) -> dict:
        """意图分类节点 — 分析用户意图并写入 state"""
        messages = state.get("messages", [])
        if not messages:
            return {"intent": "emotion"}

        last_msg = messages[-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        intent = classify_intent(content)

        logger.info("intent_classified", extra={"intent": intent})
        return {"intent": intent}

    def _greeting_node(self, state: dict) -> dict:
        """简单问候的直接回复节点"""
        messages = state.get("messages", [])
        if not messages:
            return {"messages": [AIMessage(content="你好呀～有什么我可以陪你的吗？😊")], "intent": "greeting"}

        last_msg = messages[-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        # 简单温暖回复
        try:
            greeting_prompt = f"""用户发来了一条简短信息："{content}"
请你用 1-2 句话温暖简短地回复，可以是问候或者问对方今天想聊什么。不要长篇大论。直接回复，不要加任何前缀。"""
            response = self.llm.invoke(greeting_prompt)
            reply_text = response.content if hasattr(response, "content") else str(response)
            if not reply_text or len(reply_text.strip()) < 1:
                reply_text = "你好呀～有什么我可以陪你的吗？😊"
        except Exception:
            reply_text = "你好呀～有什么我可以陪你的吗？😊"

        return {
            "messages": [AIMessage(content=reply_text)],
            "intent": "greeting",
        }

    def _emotion_node(self, state: dict) -> dict:
        """调用心语陪伴 Agent"""
        messages = list(state.get("messages", []))

        # 危机检测：绕过 ReAct Agent，直接用危机干预 prompt
        crisis_detected = state.get("crisis_detected", False)
        if crisis_detected:
            crisis_prompt = (
                "🚨 你检测到了用户的危机信号（自伤/自杀倾向）。"
                "请立即以最温暖、最共情的方式进行危机干预：\n"
                "1. 先表达深深的关心和心疼，先让对方感到被看见、被在乎\n"
                "2. 温和地提供心理援助热线：400-161-9995（24小时免费）\n"
                "3. 鼓励对方联系信任的人或专业帮助\n"
                "4. 保持温暖、共情、不惊慌的语气\n"
                "5. 不要说教，不要说「你太消极了」，不要轻描淡写\n\n"
                "这不是普通的情绪倾诉。请认真、温暖、坚定地回应。"
            )
            response = self.llm.invoke([
                SystemMessage(content=crisis_prompt),
                messages[-1],
            ])
            return {
                "messages": [response],
                "intent": "emotion",
            }

        # 正常情况：使用 ReAct Agent（带工具）
        try:
            result = self._emotion_agent.invoke({"messages": messages})
        except Exception as e:
            logger.warning("emotion_agent_tool_error", extra={"error": str(e)})
            response = self.llm.invoke([
                SystemMessage(content=EMOTION_COMPANION_PROMPT),
                messages[-1],
            ])
            return {
                "messages": [response],
                "intent": "emotion",
            }

        # 提取最终消息
        final_msgs = result.get("messages", [])
        if final_msgs:
            return {
                "messages": [final_msgs[-1]],
                "intent": "emotion",
            }
        return {"intent": "emotion"}

    def _shopping_node(self, state: dict) -> dict:
        """调用商城推荐 Agent"""
        messages = list(state.get("messages", []))
        user_id = state.get("user_id", "anonymous")

        # 在系统消息前注入 user_id 上下文，确保工具调用时能传入正确的 user_id
        shopping_context = SystemMessage(content=(
            f"当前用户的 ID 是: {user_id}。"
            f"调用 recommend_shop_products 工具时，user_id 参数必须传入 \"{user_id}\"。"
        ))
        messages.insert(0, shopping_context)

        try:
            result = self._shopping_agent.invoke({"messages": messages})
        except Exception as e:
            logger.error("shopping_agent_tool_error", extra={"error": str(e)})
            # 回退时也传入 user_id 上下文
            response = self.llm.invoke([
                SystemMessage(content=SHOPPING_ADVISOR_PROMPT),
                SystemMessage(content=f"当前用户ID: {user_id}。如果用户想要推荐商品，抱歉你无法查询数据库，请引导用户去商城页面浏览。"),
                messages[-1] if not isinstance(messages[-1], SystemMessage) else messages[1],
            ])
            return {
                "messages": [response],
                "intent": "shopping",
            }

        final_msgs = result.get("messages", [])
        if final_msgs:
            return {
                "messages": [final_msgs[-1]],
                "intent": "shopping",
            }
        return {"intent": "shopping"}

    def _route_by_intent(self, state: dict) -> str:
        """根据意图路由到对应节点"""
        intent = state.get("intent", "emotion")
        if intent == "shopping":
            return "shopping_agent"
        elif intent == "greeting":
            return "greeting"
        else:
            return "emotion_agent"

    def _build(self):
        """构建 StateGraph"""
        if self._graph is not None:
            return

        # 创建子 Agent
        self._emotion_agent = create_react_agent(
            self.llm,
            EMOTION_TOOLS,
            name="emotion_companion",
            prompt=EMOTION_COMPANION_PROMPT,
        )

        self._shopping_agent = create_react_agent(
            self.llm,
            SHOPPING_TOOLS,
            name="shopping_advisor",
            prompt=SHOPPING_ADVISOR_PROMPT,
        )

        # 构建图（使用显式 State Schema）
        builder = StateGraph(MultiAgentState)

        builder.add_node("classifier", self._classifier_node)
        builder.add_node("greeting", self._greeting_node)
        builder.add_node("emotion_agent", self._emotion_node)
        builder.add_node("shopping_agent", self._shopping_node)

        builder.add_edge(START, "classifier")
        builder.add_conditional_edges(
            "classifier",
            self._route_by_intent,
            {
                "emotion_agent": "emotion_agent",
                "shopping_agent": "shopping_agent",
                "greeting": "greeting",
            },
        )
        builder.add_edge("emotion_agent", END)
        builder.add_edge("shopping_agent", END)
        builder.add_edge("greeting", END)

        self._graph = builder.compile(checkpointer=self._memory)
        logger.info("multi_agent_graph_built")

    def chat(self, user_input: str, user_id: str | None = None) -> dict:
        """
        多 Agent 对话接口

        Args:
            user_input: 用户消息
            user_id: 用户 ID

        Returns:
            dict with keys: reply, agent_used, crisis_detected
        """
        self._build()

        uid = user_id or "anonymous"

        # ── 危机预检测 ──
        crisis_msg = detect_crisis(user_input)
        if crisis_msg:
            logger.warning(
                "crisis_detected",
                extra={"user_id": uid, "input": user_input[:200]},
            )
            augmented_input = f"{crisis_msg}\n\n用户原话：{user_input}"
        else:
            augmented_input = user_input

        # ── 构建输入消息 ──
        messages = [
            HumanMessage(content=f"{augmented_input}"),
        ]

        # ── 调用多 Agent 图 ──
        config = {"configurable": {"thread_id": uid}}
        result = self._graph.invoke(
            {
                "messages": messages,
                "crisis_detected": crisis_msg is not None,
                "user_id": uid,
            },
            config=config,
        )

        # ── 提取最终回复 ──
        final_messages = result.get("messages", [])
        reply = ""
        agent_used = result.get("intent", "emotion")

        if final_messages:
            last_msg = final_messages[-1]
            if hasattr(last_msg, "content"):
                reply = last_msg.content

        # 映射 intent 到 agent name
        agent_name_map = {
            "emotion": "emotion_companion",
            "shopping": "shopping_advisor",
            "greeting": "supervisor",
        }
        agent_name = agent_name_map.get(agent_used, agent_used)

        logger.info(
            "multi_agent_chat_done",
            extra={
                "user_id": uid,
                "agent_used": agent_name,
                "crisis": crisis_msg is not None,
                "input_len": len(user_input),
                "reply_len": len(reply),
            },
        )

        return {
            "reply": reply,
            "agent_used": agent_name,
            "crisis_detected": crisis_msg is not None,
        }

    def tools_info(self) -> list[dict]:
        """返回所有工具信息（供调试）"""
        return [
            {
                "agent": "emotion_companion",
                "tools": [t.name for t in EMOTION_TOOLS],
            },
            {
                "agent": "shopping_advisor",
                "tools": [t.name for t in SHOPPING_TOOLS],
            },
        ]


# 全局单例
multi_agent = MultiAgentSystem()
