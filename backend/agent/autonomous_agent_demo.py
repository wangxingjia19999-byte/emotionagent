import os
import sys

# 确保绝对路径在 sys.path 中，以便允许正常导入 backend 模块
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent.agent_service import (
    emotion_scale_assessment,
    get_recent_memory,
    query_emotion_knowledge_base,
    save_conversation_memory,
)

def run_autonomous_agent(user_query: str) -> str:
    """
    运行带有 Tool 调用能力的情绪分析 Agent。
    必要时调用 query_emotion_knowledge_base 执行 RAG 检索。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME", "qwen-plus"),
        temperature=0.4,
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    )

    tools = [
        query_emotion_knowledge_base,
        emotion_scale_assessment,
        get_recent_memory,
        save_conversation_memory,
    ]

    user_id = "demo_user"

    system_prompt = f"""你是一名高级情绪分析师与心理健康代理。
你的职责是帮助用户缓解负面情绪，并提供心理疏导。

【当前用户ID】{user_id}

【工作流程】
1. 当用户表现出情绪困扰、心理压力时，你应当调用工具 `query_emotion_knowledge_base`，向知识库查询相关的情绪干预策略或指导。
2. 如需了解历史上下文，可先调用 `get_recent_memory` 获取最近记忆。
3. 当用户描述持续性焦虑/抑郁/愤怒等症状时，可使用 `emotion_scale_assessment` 进行简要量表评估。
4. 生成回复后，使用 `save_conversation_memory` 记录对话摘要与标签。
5. 回复请综合运用“AVER法则”(Acknowledge-接纳, Validate-认可, Explore-探索, Resolve-解决)，语气温和、耐心且包容。"""

    agent = create_react_agent(llm, tools)

    print(f"\n🙋‍♂️ [用户诉求]: {user_query}")
    print("🤖 [Agent 正在思考并执行任务]...")

    response = agent.invoke({"messages": [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]})
    final_answer = response["messages"][-1].content

    print(f"\n💡 [Agent 最终回复]:\n{final_answer}")
    return final_answer

if __name__ == "__main__":
    # 测试不同场景
    test_queries = [
        "我因为项目延期被领导批评了，感觉自己好没用，心里很难受。",
        "你们的系统总是崩溃，今天又因为这事耽误了我一整天的工作，真的是糟糕透顶！"
    ]

    for q in test_queries:
        run_autonomous_agent(q)
        print("="*60)
