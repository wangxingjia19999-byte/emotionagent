"""
增强版情绪陪伴 Agent，集成 MCP 工具与 RAG 知识库。
支持:
- 情绪知识库 RAG 检索
- 情绪量表评估
- 对话记忆管理
- MCP 外部工具调用（搜索、抓取、天气等）
"""

import logging
import os
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.config import settings as app_settings
from .agent_service import (
    query_emotion_knowledge_base,
    emotion_scale_assessment,
    save_conversation_memory,
    get_recent_memory,
    get_user_profile,
    get_emotion_history,
    save_emotion_log,
    get_questionnaire_history,
    get_shop_categories,
    get_shop_products,
    recommend_shop_products,
)
from .mcp_manager import mcp_manager, load_preset_mcp_configs


class MCPEmotionAgent:
    """
    集成 MCP 工具的情绪分析 Agent
    使用 LangGraph ReAct Agent 模式，自动决策何时调用工具
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

        self._llm = None
        self._builtin_tools = [
            query_emotion_knowledge_base,
            emotion_scale_assessment,
            save_conversation_memory,
            get_recent_memory,
            get_user_profile,
            get_emotion_history,
            save_emotion_log,
            get_questionnaire_history,
            get_shop_categories,
            get_shop_products,
            recommend_shop_products,
        ]

        self._mcp_tools: list[BaseTool] = []
        self._mcp_initialized = False

        # 初始化预设 MCP 配置
        load_preset_mcp_configs()

    def _get_llm(self):
        """懒加载 LLM，避免导入时因缺少 API key 而报错"""
        if self._llm is None:
            api_key = app_settings.openai_api_key
            if not api_key:
                raise RuntimeError("未配置 OPENAI_API_KEY，请在 .env 中设置")
            self._llm = ChatOpenAI(
                model=app_settings.openai_model_name,
                temperature=0.4,
                api_key=api_key,
                base_url=app_settings.openai_base_url,
            )
        return self._llm

    async def _init_mcp_tools(self) -> list[BaseTool]:
        """异步初始化 MCP 工具"""
        if self._mcp_initialized:
            return self._mcp_tools

        try:
            self._mcp_tools = await mcp_manager.get_all_tools()
        except Exception as e:
            print(f"⚠️ MCP 工具加载失败: {e}")
            self._mcp_tools = []

        self._mcp_initialized = True
        return self._mcp_tools

    def _get_all_tools_sync(self) -> list[BaseTool]:
        """同步获取所有工具（含 MCP）"""
        import asyncio

        tools = list(self._builtin_tools)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return tools
        except RuntimeError:
            pass

        try:
            mcp_tools = asyncio.run(self._init_mcp_tools())
            tools.extend(mcp_tools)
        except Exception as e:
            print(f"⚠️ 同步加载 MCP 工具失败: {e}")

        return tools

    def build_system_prompt(self, user_id: str | None = None) -> str:
        """构建系统提示词"""
        uid = user_id or "anonymous"
        mcp_tool_names = [t.name for t in self._mcp_tools]
        mcp_desc = ""
        if mcp_tool_names:
            mcp_desc = f"\n【可用外部工具】: {', '.join(mcp_tool_names)}"

        return f"""你是一个温暖、真诚的情绪陪伴者，名字叫"心语"。你是"心语陪伴"情绪互助平台的 AI 伙伴。

当前和你聊天的用户 ID 是: {uid}

你不是心理医生，不是诊疗机器人，而是一个愿意倾听、能共情的朋友。让人感觉舒服和安心是你最重要的目标。

对话原则：
- 先倾听，后回应。不要急着给建议，先让对方感到被听见
- 说话像朋友，不要用专业术语或模板化的结构
- 适度使用自然的口语："我懂那种感觉"、"听起来你今天……"、"谢谢你愿意和我说这些"
- 回复保持在 1-3 段，不要太长
- 不要在任何情况下说教、否定或轻描淡写

可以使用的工具（按需调用，不要每次都全用）：
情绪陪伴类：
- 遇到不懂的情绪问题，可以调用 `query_emotion_knowledge_base` 查一下陪伴知识和回应思路
- 想了解之前聊了什么，可以调用 `get_recent_memory`
- 聊完后，用 `save_conversation_memory` 记一下要点
- 可以调用 `get_user_profile` 了解用户的个人画像（年龄、职业、压力来源等）
- 可以调用 `get_emotion_history` 和 `get_questionnaire_history` 了解用户近期的情绪状态和变化趋势
- 如果对方持续描述焦虑/抑郁的症状，可以委婉地邀请用 `emotion_scale_assessment` 做个小评估，但不要强迫

商城与推荐类：
- 当用户想浏览或搜索商品时，调用 `get_shop_categories` 或 `get_shop_products`
- 当用户表达情绪困扰、问"有什么推荐的吗"、或你想主动关心并推荐一些减压好物时，调用 `recommend_shop_products` 根据用户的真实情绪状态做个性化推荐。推荐完后可以用自然的语气介绍，比如"我看你最近压力挺大的，商城里有几个减压的小东西，要不要看看？"
{mcp_desc}

安全提醒（只在确实遇到危机信号时才自然提及）：
如果对方表达出自伤、自杀或暴力倾向，先表达关心和心疼，再温和地提到可以拨打心理援助热线 400-161-9995。不要惊慌失措。
"""

    async def chat_async(self, user_input: str, user_id: str | None = None) -> str:
        """异步聊天接口（支持 MCP 工具）"""
        await self._init_mcp_tools()
        all_tools = self._builtin_tools + self._mcp_tools
        system_prompt = self.build_system_prompt(user_id)

        agent = create_react_agent(self._get_llm(), all_tools)
        response = agent.invoke({
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input),
            ]
        })
        return response["messages"][-1].content

    def chat(self, user_input: str, user_id: str | None = None) -> str:
        """同步聊天接口"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                tools = self._get_all_tools_sync()
                system_prompt = self.build_system_prompt(user_id)
                agent = create_react_agent(self._get_llm(), tools)
                response = agent.invoke({
                    "messages": [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input),
                    ]
                })
                return response["messages"][-1].content
            else:
                return asyncio.run(self.chat_async(user_input, user_id))
        except Exception as e:
            # 回退到基础 RAG 管道
            from .agent_service import emotion_agent_service
            return emotion_agent_service.chat(user_input)

    def get_tools_info(self) -> list[dict[str, Any]]:
        """获取当前所有可用工具的信息"""
        tools_info = []
        for t in self._builtin_tools:
            tools_info.append({
                "name": t.name,
                "description": t.description,
                "source": "builtin",
            })
        for t in self._mcp_tools:
            tools_info.append({
                "name": t.name,
                "description": t.description,
                "source": "mcp",
            })
        return tools_info


# 全局单例
mcp_emotion_agent = MCPEmotionAgent()
