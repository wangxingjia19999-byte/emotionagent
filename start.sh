#!/bin/bash

# ============================================================================
# 心语陪伴 - 项目启动脚本
# 用法: bash start.sh 或 ./start.sh
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_info "启动心语陪伴项目..."
print_info "项目路径: $PROJECT_ROOT"

# ============================================================================
# 1. 检查前置条件
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "检查前置条件..."
print_info "═══════════════════════════════════════════"

# 检查 Python
if ! command -v python3 &> /dev/null; then
  print_error "未找到 Python3，请先安装"
  exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "✅ Python3 已安装 (版本: $PYTHON_VERSION)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
  print_error "未找到 Node.js，请先安装"
  exit 1
fi
NODE_VERSION=$(node --version)
print_success "✅ Node.js 已安装 (版本: $NODE_VERSION)"

# 检查 npm
if ! command -v npm &> /dev/null; then
  print_error "未找到 npm，请先安装"
  exit 1
fi
NPM_VERSION=$(npm --version)
print_success "✅ npm 已安装 (版本: $NPM_VERSION)"

# 检查 MySQL
if ! command -v mysql &> /dev/null; then
  print_warning "未找到 mysql 命令行工具"
  print_warning "请确保 MySQL 服务已启动在 localhost:3306"
else
  print_success "✅ MySQL 已安装"
fi

# ============================================================================
# 2. 创建必要的目录
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "创建必要目录..."
print_info "═══════════════════════════════════════════"

mkdir -p "$PROJECT_ROOT/backend/logs"
mkdir -p "$PROJECT_ROOT/backend/data"
mkdir -p "$PROJECT_ROOT/frontend/node_modules"
print_success "✅ 目录结构已准备就绪"

# ============================================================================
# 3. 配置后端
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "配置后端环境..."
print_info "═══════════════════════════════════════════"

cd "$PROJECT_ROOT/backend"

# 检查 .env 文件
if [ ! -f .env ]; then
  print_warning ".env 文件不存在，从 .env.example 创建..."
  if [ -f .env.example ]; then
    cp .env.example .env
    print_success "✅ .env 文件已创建（请根据需要修改）"
  else
    print_error ".env.example 文件不存在"
    exit 1
  fi
else
  print_success "✅ .env 文件已存在"
fi

# 检查虚拟环境
if [ ! -d venv ]; then
  print_info "创建 Python 虚拟环境..."
  python3 -m venv venv
  print_success "✅ 虚拟环境已创建"
else
  print_success "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
print_info "安装 Python 依赖..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "✅ Python 依赖已安装"

# ============================================================================
# 4. 配置前端
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "配置前端环境..."
print_info "═══════════════════════════════════════════"

cd "$PROJECT_ROOT/frontend"

# 安装依赖
print_info "安装 npm 依赖..."
npm install > /dev/null 2>&1
print_success "✅ npm 依赖已安装"

# ============================================================================
# 5. 启动服务
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "启动服务..."
print_info "═══════════════════════════════════════════"

print_success "所有准备工作已完成！"
print_info ""
print_info "现在需要在两个不同的终端中启动服务："
print_info ""
print_warning "终端 1 - 启动后端服务 (FastAPI):"
echo "  cd $PROJECT_ROOT/backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
print_info "  后端将在 http://localhost:8000 运行"
print_info "  API 文档: http://localhost:8000/docs"
print_info ""
print_warning "终端 2 - 启动前端服务 (Vite):"
echo "  cd $PROJECT_ROOT/frontend"
echo "  npm run dev"
print_info "  前端将在 http://localhost:5173 运行"
print_info ""
print_success "✅ 启动脚本完成！请按照上述说明启动服务。"

# ============================================================================
# 显示数据库初始化提示
# ============================================================================
print_info "═══════════════════════════════════════════"
print_info "数据库初始化（首次运行时执行）"
print_info "═══════════════════════════════════════════"

print_info "如果是首次运行，请在启动服务前，在新的终端中执行："
echo "  # 创建数据库"
echo "  mysql -u root -p -e \"CREATE DATABASE emotion_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
echo "  "
echo "  # 应用数据库迁移"
echo "  cd $PROJECT_ROOT/backend"
echo "  source venv/bin/activate"
echo "  alembic upgrade head"

print_info ""
print_info "════════════════════════════════════════════════════════════"
