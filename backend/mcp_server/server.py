"""
心语陪伴 MCP 服务器

将情绪平台的核心能力以 MCP 协议暴露，支持 HTTP/SSE/stdio 传输。

启动方式:
    python -m mcp_server.server                    # HTTP 模式 :8765
    python -m mcp_server.server --transport sse    # SSE 模式
    python -m mcp_server.server --transport stdio  # stdio 模式
    python -m mcp_server.server --port 9000        # 自定义端口

客户端配置 (Claude Desktop claude_desktop_config.json):
    {
      "mcpServers": {
        "emotion-platform": {
          "url": "http://localhost:8765/sse"
        }
      }
    }

或者用 stdio 模式:
    {
      "mcpServers": {
        "emotion-platform": {
          "command": "python",
          "args": ["-m", "mcp_server.server", "--transport", "stdio"],
          "cwd": "/path/to/backend"
        }
      }
    }
"""

import argparse
import os
import sys

# 确保 backend 目录在 sys.path 中，使 app 和 agent 模块可导入
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _base_dir not in sys.path:
    sys.path.insert(0, _base_dir)

from fastmcp import FastMCP

# ── 导入工具和资源函数 ────────────────────────────────────
from mcp_server.tools.emotion_tools import (
    analyze_emotion,
    emotion_assessment,
    get_emotion_history,
    get_user_profile,
    recommend_products,
    get_user_activity_overview,
    get_my_posts,
    get_unread_messages,
    get_community_square_posts,
    publish_community_post,
)
from mcp_server.tools.knowledge_tools import (
    get_conversation_memory,
    get_questionnaire_history,
    search_knowledge_base,
)
from mcp_server.resources.emotion_resources import (
    get_emotion_summary,
    get_knowledge_topic,
)

# ── 创建 FastMCP 服务器实例 ──────────────────────────────────
mcp = FastMCP(
    name="心语陪伴 Emotion Platform",
    instructions="""你是"心语陪伴"情绪互助平台的 AI 助手。你可以通过以下工具帮助用户：

**情绪分析类：**
- analyze_emotion — 分析文本中的情绪状态
- emotion_assessment — 运行情绪量表评估
- search_knowledge_base — 从专业知识库检索情绪陪伴策略

**用户数据类：**
- get_user_profile — 查看用户的个人画像
- get_emotion_history — 查看用户近期情绪变化
- get_conversation_memory — 查看最近的对话记录
- get_questionnaire_history — 查看用户的问卷测评历史
- get_user_activity_overview — 查看用户平台活动概况（AI聊天次数/帖子数/未读消息等）
- get_my_posts — 查看用户自己发表的帖子
- get_unread_messages — 查看用户的未读私信

**社区与推荐类：**
- get_community_square_posts — 查看社区广场帖子，分析社区集体情绪氛围
- publish_community_post — 帮用户在社区广场发布帖子（需先获得用户许可）
- recommend_products — 根据情绪状态推荐减压商品

使用原则：
1. 先倾听，再回应。不要急于给建议。
2. 调用用户数据工具时，需要提供有效的 user_id。
3. 推荐商品前最好先了解用户的情绪状态。
""",
    version="1.0.0",
)


# ── 注册 MCP 工具 (Tools) ──────────────────────────────────

mcp.tool(
    name="analyze_emotion",
    description="分析文本中蕴含的情绪状态。输入一段用户描述的文字，返回情绪分析结果和陪伴建议。",
)(analyze_emotion)

mcp.tool(
    name="emotion_assessment",
    description="情绪量表简评工具。传入一组 0-3 的答案（0=无,1=轻,2=中,3=重），返回总分、程度等级和建议。",
)(emotion_assessment)

mcp.tool(
    name="get_user_profile",
    description="获取用户在平台上的个人画像（昵称、年龄、职业、压力来源等）。需要提供 user_id。",
)(get_user_profile)

mcp.tool(
    name="get_emotion_history",
    description="查看用户近期的情绪记录历史，了解情绪变化轨迹。需要提供 user_id。",
)(get_emotion_history)

mcp.tool(
    name="recommend_products",
    description="根据用户的情绪状态推荐商城减压商品。需要提供 user_id，可选 emotion_label。",
)(recommend_products)

mcp.tool(
    name="get_user_activity_overview",
    description="获取用户在平台上的活动概况（AI聊天次数、帖子数、收藏数、未读私信数、好友数）。需要提供 user_id。",
)(get_user_activity_overview)

mcp.tool(
    name="get_my_posts",
    description="查看用户自己发表的帖子列表，包含标题、内容预览、心情标签、互动数据。需要提供 user_id。",
)(get_my_posts)

mcp.tool(
    name="get_unread_messages",
    description="查看用户的未读私信，包括发送者、内容预览和时间。需要提供 user_id。",
)(get_unread_messages)

mcp.tool(
    name="get_community_square_posts",
    description="查看社区广场的帖子，可按关键词、心情标签、分类筛选，支持最新/最热排序。用于分析社区集体情绪氛围。",
)(get_community_square_posts)

mcp.tool(
    name="publish_community_post",
    description="帮用户在社区广场发布帖子。使用前必须先告知用户并获得许可。需要 user_id、title、content，可选 mood_tag、category、is_anonymous。",
)(publish_community_post)

mcp.tool(
    name="search_knowledge_base",
    description="从情绪陪伴专业知识库中检索信息，包含情绪干预策略、疏导话术和危机应对指导。",
)(search_knowledge_base)

mcp.tool(
    name="get_conversation_memory",
    description="获取用户最近的对话记忆，了解之前聊了什么。需要提供 user_id。",
)(get_conversation_memory)

mcp.tool(
    name="get_questionnaire_history",
    description="查看用户的情绪问卷填写历史（PHQ-9 抑郁筛查、GAD-7 焦虑筛查等）。",
)(get_questionnaire_history)


# ── 注册 MCP 资源 (Resources) ──────────────────────────────

mcp.resource(
    "emotion://users/{user_id}/summary",
    name="用户情绪摘要",
    description="获取用户的情绪摘要，包含基本信息、近期情绪记录和问卷评估结果。",
)(get_emotion_summary)

mcp.resource(
    "emotion://knowledge/{topic}",
    name="情绪知识主题",
    description="按主题获取情绪陪伴知识。topic 可选: anxiety, depression, stress, anger, loneliness, selfcare, crisis, communication",
)(get_knowledge_topic)


# ── 注册 MCP 提示词 (Prompts) ──────────────────────────────

@mcp.prompt(
    name="companion_chat",
    description="生成情绪陪伴对话的系统提示词，可传入用户 ID 和上下文来定制",
)
def companion_chat(user_id: str = "anonymous", context: str = "") -> str:
    """生成一个温暖、专业的情绪陪伴对话提示词模板。"""
    uid = user_id or "anonymous"
    extra = f"\n\n{context}" if context else ""
    return f"""你是一个温暖、真诚的情绪陪伴者，名字叫"心语"。你是"心语陪伴"情绪互助平台的 AI 伙伴。

当前和你聊天的用户 ID 是: {uid}

你不是心理医生，不是诊疗机器人，而是一个愿意倾听、能共情的朋友。让人感觉舒服和安心是你最重要的目标。

对话原则：
- 先倾听，后回应。不要急着给建议，先让对方感到被听见
- 说话像朋友，不要用专业术语或模板化的结构
- 适度使用自然的口语："我懂那种感觉"、"听起来你今天……"、"谢谢你愿意和我说这些"
- 回复保持在 1-3 段，不要太长
- 不要在任何情况下说教、否定或轻描淡写

安全提醒：如果对方表达出自伤、自杀或暴力倾向，先表达关心和心疼，再温和地提到可以拨打心理援助热线 400-161-9995。不要惊慌失措。{extra}"""


# ── 启动入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="心语陪伴 MCP 服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m mcp_server.server                        # HTTP 模式, 端口 8765
  python -m mcp_server.server --transport sse        # SSE 模式
  python -m mcp_server.server --transport stdio      # stdio 模式 (Claude Desktop)
  python -m mcp_server.server --port 9000 --host 127.0.0.1
        """,
    )
    parser.add_argument(
        "--transport", "-t",
        default="http",
        choices=["http", "sse", "stdio", "streamable-http"],
        help="传输协议 (默认: http)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="绑定地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8765,
        help="监听端口 (默认: 8765)",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="不显示启动横幅",
    )
    args = parser.parse_args()

    # 异步获取注册数量
    import asyncio as _asyncio

    async def _count():
        t = await mcp.list_tools()
        r = await mcp.list_resources()
        r_t = await mcp.list_resource_templates()
        p = await mcp.list_prompts()
        return len(t), len(r) + len(r_t), len(p)

    tool_n, res_n, prompt_n = _asyncio.run(_count())

    listen_addr = (
        "stdio (Claude Desktop)"
        if args.transport == "stdio"
        else f"http://{args.host}:{args.port}"
    )
    print(f"""
╔══════════════════════════════════════════════════════════╗
║      💙 心语陪伴 MCP 服务器 v1.0.0                      ║
║      Emotion Platform — Model Context Protocol           ║
╠══════════════════════════════════════════════════════════╣
║  传输协议: {args.transport:<44} ║
║  监听地址: {listen_addr:<42} ║
╠══════════════════════════════════════════════════════════╣
║  已注册 {tool_n:>2} 个工具, {res_n:>2} 个资源, {prompt_n:>2} 个提示词            ║
╚══════════════════════════════════════════════════════════╝
""")

    if args.transport == "stdio":
        mcp.run(transport="stdio", show_banner=not args.no_banner)
    else:
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            show_banner=not args.no_banner,
        )


if __name__ == "__main__":
    main()
