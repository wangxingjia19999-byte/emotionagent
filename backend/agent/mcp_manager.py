"""
MCP (Model Context Protocol) 管理器
负责连接、管理多个 MCP 服务器，并将其工具转换为 LangChain 兼容的工具。
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MCPServerConfig:
    """单个 MCP 服务器的配置"""
    name: str
    command: str  # 例如 "npx" 或 "python"
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""


# 预设的推荐 MCP 服务器配置，适合情绪陪伴场景
PRESET_MCP_SERVERS: list[dict[str, Any]] = [
    {
        "name": "brave_search",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-brave-search"],
        "env": {"BRAVE_API_KEY": ""},
        "enabled": False,
        "description": "Brave 搜索引擎，用于检索心理健康资源、求助热线、应对策略等信息",
    },
    {
        "name": "fetch",
        "command": "python",
        "args": ["-m", "mcp_server_fetch"],
        "env": {},
        "enabled": False,
        "description": "网页内容抓取，用于阅读和总结心理健康相关文章",
    },
    {
        "name": "sequential_thinking",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-sequential-thinking"],
        "env": {},
        "enabled": False,
        "description": "顺序思考工具，用于复杂情绪状态的多步推理分析",
    },
    {
        "name": "weather",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-weather"],
        "env": {},
        "enabled": False,
        "description": "天气查询，提供用户所在地天气信息作为情绪分析辅助上下文",
    },
]


class MCPServerConnection:
    """单个 MCP 服务器的连接会话"""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._session: ClientSession | None = None
        self._tools: list[StructuredTool] = []
        self._read = None
        self._write = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> list[StructuredTool]:
        """连接到 MCP 服务器并发现其工具"""
        if self._connected:
            return self._tools

        env = os.environ.copy()
        env.update({k: v for k, v in self.config.env.items() if v})

        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=env,
        )

        self._read, self._write = await stdio_client(server_params).__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await self._session.initialize()

        # 发现 MCP 工具
        mcp_tools = await self._session.list_tools()
        self._tools = []

        for mcp_tool in mcp_tools.tools:
            langchain_tool = self._create_tool_wrapper(mcp_tool.name, mcp_tool.description, mcp_tool.inputSchema)
            self._tools.append(langchain_tool)

        self._connected = True
        return self._tools

    def _create_tool_wrapper(self, name: str, description: str, schema: dict) -> StructuredTool:
        """将 MCP 工具封装为 LangChain StructuredTool"""

        def _make_call_func(tool_name: str):
            def _call(**kwargs) -> str:
                return asyncio.run(self._call_mcp_tool(tool_name, kwargs))
            return _call

        async def _async_call(**kwargs) -> str:
            return await self._call_mcp_tool(name, kwargs)

        # 根据 MCP schema 构建 args_schema
        from pydantic import BaseModel, create_model

        args_schema = None
        if "properties" in schema:
            fields = {}
            props = schema.get("properties", {})
            required = schema.get("required", [])
            for prop_name, prop_info in props.items():
                prop_type = str
                if prop_info.get("type") == "number":
                    prop_type = float
                elif prop_info.get("type") == "integer":
                    prop_type = int
                elif prop_info.get("type") == "boolean":
                    prop_type = bool

                default = ... if prop_name in required else None
                fields[prop_name] = (prop_type, default)

            if fields:
                args_schema = create_model(f"{name}_args", **fields)

        return StructuredTool(
            name=name,
            description=description,
            func=_make_call_func(name),
            coroutine=_async_call,
            args_schema=args_schema,
        )

    async def _call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """调用 MCP 工具"""
        if not self._session:
            return "MCP 会话未连接"

        try:
            result = await self._session.call_tool(tool_name, arguments)
            # 根据结果类型提取文本内容
            if hasattr(result, "content") and result.content:
                parts = []
                for item in result.content:
                    if hasattr(item, "text"):
                        parts.append(item.text)
                    elif hasattr(item, "data"):
                        parts.append(str(item.data))
                    else:
                        parts.append(str(item))
                return "\n".join(parts)
            return str(result)
        except Exception as e:
            return f"MCP 工具调用异常 ({tool_name}): {str(e)}"

    async def disconnect(self):
        """断开连接"""
        if self._session:
            try:
                await self._session.__aexit__(None, None, None)
            except Exception:
                pass
            self._session = None

        if self._read and self._write:
            try:
                await self._read.aclose()
                await self._write.aclose()
            except Exception:
                pass
            self._read = None
            self._write = None

        self._connected = False
        self._tools = []


class MCPManager:
    """
    MCP 连接管理器（单例）
    管理多个 MCP 服务器的生命周期，提供统一的工具获取接口
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections: dict[str, MCPServerConnection] = {}
            cls._instance._configs: dict[str, MCPServerConfig] = {}
        return cls._instance

    def configure_server(self, config: MCPServerConfig) -> None:
        """添加或更新 MCP 服务器配置"""
        self._configs[config.name] = config
        # 如果已有连接且配置变更，断开旧连接
        if config.name in self._connections:
            asyncio.run(self._connections[config.name].disconnect())
            del self._connections[config.name]

    def remove_server(self, name: str) -> None:
        """移除 MCP 服务器配置"""
        if name in self._connections:
            asyncio.run(self._connections[name].disconnect())
            del self._connections[name]
        self._configs.pop(name, None)

    async def connect_server(self, name: str) -> list[StructuredTool]:
        """连接到指定的 MCP 服务器并返回其工具"""
        if name not in self._configs:
            raise ValueError(f"未找到 MCP 服务器配置: {name}")

        config = self._configs[name]
        if not config.enabled:
            return []

        if name in self._connections and self._connections[name].connected:
            return self._connections[name]._tools

        conn = MCPServerConnection(config)
        tools = await conn.connect()
        self._connections[name] = conn
        return tools

    async def get_all_tools(self) -> list[StructuredTool]:
        """获取所有已启用 MCP 服务器的工具"""
        all_tools = []
        for name, config in self._configs.items():
            if config.enabled:
                try:
                    tools = await self.connect_server(name)
                    all_tools.extend(tools)
                except Exception as e:
                    print(f"⚠️ 连接 MCP 服务器 '{name}' 失败: {e}")
        return all_tools

    async def disconnect_all(self) -> None:
        """断开所有 MCP 连接"""
        for name, conn in list(self._connections.items()):
            try:
                await conn.disconnect()
            except Exception:
                pass
        self._connections.clear()

    def list_servers(self) -> list[dict[str, Any]]:
        """列出所有配置的服务器及其状态"""
        result = []
        for name, config in self._configs.items():
            conn = self._connections.get(name)
            result.append({
                "name": config.name,
                "command": config.command,
                "args": config.args,
                "enabled": config.enabled,
                "description": config.description,
                "connected": conn.connected if conn else False,
                "tools_count": len(conn._tools) if conn and conn.connected else 0,
                "has_env_keys": list(config.env.keys()),
            })
        return result

    async def test_connection(self, name: str) -> dict[str, Any]:
        """测试与 MCP 服务器的连接"""
        try:
            tools = await self.connect_server(name)
            return {
                "success": True,
                "tools": [{"name": t.name, "description": t.description} for t in tools],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局单例
mcp_manager = MCPManager()


def load_preset_mcp_configs() -> None:
    """加载预设的 MCP 服务器配置到管理器"""
    for preset in PRESET_MCP_SERVERS:
        config = MCPServerConfig(
            name=preset["name"],
            command=preset["command"],
            args=preset["args"],
            env=preset["env"],
            enabled=preset["enabled"],
            description=preset["description"],
        )
        mcp_manager.configure_server(config)
