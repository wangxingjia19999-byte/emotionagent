#!/bin/bash
# ────────────────────────────────────────────────────
# 心语陪伴 arq Worker — 启动脚本 (macOS/Linux)
# 后台异步任务：邮件发送、情绪日志、通知等
# ────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📬 心语陪伴 arq Worker 启动脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 Python
PYTHON=$(command -v python3 || command -v python)
echo "✅ Python: $($PYTHON --version)"

# 检查 .env
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，将使用默认 Redis 配置"
fi

# 检查 arq
$PYTHON -c "import arq" 2>/dev/null || {
    echo "⚠️  arq 未安装，正在安装..."
    pip install arq
}

# 检查 Redis 是否可达
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
if command -v redis-cli &>/dev/null; then
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &>/dev/null; then
        echo "✅ Redis: $REDIS_HOST:$REDIS_PORT 连接正常"
    else
        echo "⚠️  Redis 未响应，请先启动 Redis 服务"
        echo "   macOS: brew services start redis"
        echo "   Linux: sudo systemctl start redis"
    fi
else
    echo "ℹ️  未安装 redis-cli，跳过连接检查"
fi

echo ""
echo "  启动 arq Worker..."
echo "  已注册任务: send_verification_email_task, save_emotion_log_task,"
echo "              send_notification_email_task, send_email_task"
echo ""

# 启动 arq worker
cd "$SCRIPT_DIR/backend"
$PYTHON -m arq backend.app.worker.WorkerSettings
