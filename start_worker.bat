@echo off
REM ────────────────────────────────────────────────────
REM 心语陪伴 arq Worker — 启动脚本 (Windows)
REM 后台异步任务：邮件发送、情绪日志、通知等
REM ────────────────────────────────────────────────────

setlocal enabledelayedexpansion

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   📬 心语陪伴 arq Worker 启动脚本
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /d "%~dp0backend"

python --version
echo ✅ Python 已就绪

REM 检查 .env
if not exist ".env" (
    echo ⚠️  未找到 .env 文件，将使用默认 Redis 配置
)

REM 检查 arq
python -c "import arq" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  arq 未安装，正在安装...
    pip install arq
)

echo.
echo   启动 arq Worker...
echo   已注册任务: send_verification_email_task, save_emotion_log_task,
echo              send_notification_email_task, send_email_task
echo.

python -m arq backend.app.worker.WorkerSettings

endlocal
