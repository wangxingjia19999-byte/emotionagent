#!/bin/bash
# ────────────────────────────────────────────────────
# 心语陪伴 MCP 服务器 — 启动脚本 (macOS/Linux)
# ────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  💙 心语陪伴 MCP 服务器启动脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
echo "✅ Python: $($PYTHON --version)"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，将使用默认配置"
    echo "   如需配置 LLM API Key，请: cp .env.example .env"
fi

# 检查依赖
echo "📦 检查依赖..."
$PYTHON -c "import fastmcp" 2>/dev/null || {
    echo "⚠️  fastmcp 未安装，正在安装..."
    pip install fastmcp
}

# 解析参数
TRANSPORT="${1:-http}"
PORT="${2:-8765}"
HOST="${3:-0.0.0.0}"

echo ""
echo "  传输协议: $TRANSPORT"
if [ "$TRANSPORT" != "stdio" ]; then
    echo "  监听地址: http://$HOST:$PORT"
fi
echo ""

# 启动 MCP 服务器
cd "$SCRIPT_DIR/backend"
$PYTHON -m mcp_server.server \
    --transport "$TRANSPORT" \
    --port "$PORT" \
    --host "$HOST"
