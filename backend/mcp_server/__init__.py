"""
心语陪伴 MCP 服务器模块

将情绪平台的核心能力暴露为 MCP (Model Context Protocol) 工具/资源/提示词，
供 Claude Desktop、VS Code 及其他 AI 客户端通过 HTTP/SSE 协议调用。

启动方式:
    python -m mcp_server.server           # 默认 HTTP 模式 :8765
    python -m mcp_server.server --stdio   # stdio 模式（Claude Desktop 集成）
    python -m mcp_server.server --sse     # SSE 模式
"""
