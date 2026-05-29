@echo off
REM ============================================================================
REM 心语陪伴 - 项目启动脚本 (Windows)
REM 用法: start.bat
REM ============================================================================

setlocal enabledelayedexpansion

REM 颜色定义
REM 由于 Windows CMD 的颜色支持有限，使用简单的文本输出

echo.
echo ============================================================================
echo 心语陪伴 - 项目启动脚本
echo ============================================================================
echo.

REM 获取项目根目录
set "PROJECT_ROOT=%cd%"
echo 项目路径: %PROJECT_ROOT%

REM ============================================================================
REM 1. 检查前置条件
REM ============================================================================
echo.
echo [检查前置条件...]

python --version >nul 2>&1
if errorlevel 1 (
  echo [错误] 未找到 Python，请先安装 Python 3.10+
  pause
  exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [✓] Python 已安装 (版本: %PYTHON_VERSION%)

node --version >nul 2>&1
if errorlevel 1 (
  echo [错误] 未找到 Node.js，请先安装
  pause
  exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [✓] Node.js 已安装 (版本: %NODE_VERSION%)

npm --version >nul 2>&1
if errorlevel 1 (
  echo [错误] 未找到 npm，请先安装
  pause
  exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [✓] npm 已安装 (版本: %NPM_VERSION%)

REM ============================================================================
REM 2. 创建必要的目录
REM ============================================================================
echo.
echo [创建必要目录...]

if not exist "%PROJECT_ROOT%\backend\logs" mkdir "%PROJECT_ROOT%\backend\logs"
if not exist "%PROJECT_ROOT%\backend\data" mkdir "%PROJECT_ROOT%\backend\data"
if not exist "%PROJECT_ROOT%\frontend\node_modules" mkdir "%PROJECT_ROOT%\frontend\node_modules"
echo [✓] 目录结构已准备就绪

REM ============================================================================
REM 3. 配置后端
REM ============================================================================
echo.
echo [配置后端环境...]

cd /d "%PROJECT_ROOT%\backend"

if not exist .env (
  echo [提示] .env 文件不存在，从 .env.example 创建...
  if exist .env.example (
    copy .env.example .env >nul
    echo [✓] .env 文件已创建 (请根据需要修改)
  ) else (
    echo [错误] .env.example 文件不存在
    pause
    exit /b 1
  )
) else (
  echo [✓] .env 文件已存在
)

if not exist venv (
  echo [提示] 创建 Python 虚拟环境...
  python -m venv venv
  echo [✓] 虚拟环境已创建
) else (
  echo [✓] 虚拟环境已存在
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [提示] 安装 Python 依赖（这可能需要几分钟）...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
  echo [警告] Python 依赖安装可能出现问题，建议手动执行: pip install -r requirements.txt
) else (
  echo [✓] Python 依赖已安装
)

REM ============================================================================
REM 4. 配置前端
REM ============================================================================
echo.
echo [配置前端环境...]

cd /d "%PROJECT_ROOT%\frontend"

echo [提示] 安装 npm 依赖（这可能需要几分钟）...
call npm install >nul 2>&1
if errorlevel 1 (
  echo [警告] npm 依赖安装可能出现问题，建议手动执行: npm install
) else (
  echo [✓] npm 依赖已安装
)

REM ============================================================================
REM 5. 完成并显示启动说明
REM ============================================================================
echo.
echo ============================================================================
echo 准备工作已完成！
echo ============================================================================
echo.
echo 现在需要在两个不同的命令行窗口中启动服务：
echo.
echo [步骤 1] 启动后端服务 (FastAPI)
echo 在第一个命令行中执行：
echo   cd %PROJECT_ROOT%\backend
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo   后端将在 http://localhost:8000 运行
echo   API 文档: http://localhost:8000/docs
echo.
echo [步骤 2] 启动前端服务 (Vite)
echo 在第二个命令行中执行：
echo   cd %PROJECT_ROOT%\frontend
echo   npm run dev
echo.
echo   前端将在 http://localhost:5173 运行
echo.
echo ============================================================================
echo 数据库初始化（首次运行时执行）
echo ============================================================================
echo.
echo 如果是首次运行，请先在 MySQL 中创建数据库：
echo   # 使用 MySQL 客户端执行
echo   CREATE DATABASE emotion_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo.
echo 然后应用数据库迁移：
echo   cd %PROJECT_ROOT%\backend
echo   venv\Scripts\activate.bat
echo   alembic upgrade head
echo.
echo ============================================================================
echo [✓] 脚本执行完成！请按照上述说明启动服务。
echo ============================================================================
echo.

pause
