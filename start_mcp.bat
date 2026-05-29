@echo off
REM ────────────────────────────────────────────────────
REM 心语陪伴 MCP 服务器 — 启动脚本 (Windows)
REM ────────────────────────────────────────────────────

setlocal enabledelayedexpansion

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   💙 心语陪伴 MCP 服务器启动脚本
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /d "%~dp0backend"

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python，请先安装 Python 3.10+
    exit /b 1
)

python --version
echo ✅ Python 已就绪

REM 检查 .env
if not exist ".env" (
    echo ⚠️  未找到 .env 文件，将使用默认配置
)

REM 检查依赖
echo 📦 检查依赖...
python -c "import fastmcp" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  fastmcp 未安装，正在安装...
    pip install fastmcp
)

REM 默认参数
set TRANSPORT=%1
if "%TRANSPORT%"=="" set TRANSPORT=http
set PORT=%2
if "%PORT%"=="" set PORT=8765
set HOST=%3
if "%HOST%"=="" set HOST=0.0.0.0

echo.
echo   传输协议: %TRANSPORT%
if "%TRANSPORT%" neq "stdio" (
    echo   监听地址: http://%HOST%:%PORT%
)
echo.

python -m mcp_server.server --transport %TRANSPORT% --port %PORT% --host %HOST%

endlocal
