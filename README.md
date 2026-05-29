# 心语陪伴 - 情绪陪伴与社交互助平台

一个基于 Vue3 + FastAPI 的全栈情绪陪伴与社交互助平台。提供用户认证、好友系统、社区交流和AI情绪陪伴功能。

## 🎯 项目特性

- ✅ 用户认证与授权（JWT + Bcrypt）
- ✅ 好友聊天系统
- ✅ 社区论坛模块
- ✅ 个人资料管理
- ✅ 问卷调查功能
- ✅ 商品商城
- ✅ 后台管理
- ✅ 限流保护
- ✅ CORS跨域支持

## 📋 前置要求

在启动项目前，请确保已安装以下工具：

| 工具 | 版本 | 说明 |
|------|------|------|
| **Python** | >= 3.10 | 后端环境 |
| **Node.js** | >= 16 | 前端环境 |
| **npm** | >= 8 | 包管理器 |
| **MySQL** | >= 5.7 | 数据库 |

## 🚀 快速启动

### 1️⃣ 克隆与初始化

```bash
# 进入项目目录
cd emotionagent

# 初始化项目结构
mkdir -p backend/logs
mkdir -p backend/data
```

### 2️⃣ 后端启动

#### 步骤1：安装依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2：配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```bash
cat > .env << 'EOF'
# App 配置
APP_NAME=心语陪伴
APP_VERSION=1.0.0
DEBUG=true

# MySQL 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotion_platform

# JWT 密钥（生产环境请修改！）
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# OpenAI / 阿里云百炼
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=qwen-plus

# SMTP 邮件配置（可选）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your-email@qq.com
SMTP_PASSWORD=your-email-password
SMTP_FROM=your-email@qq.com

# CORS 配置
CORS_ORIGINS=["http://localhost:5173"]
EOF
```

#### 步骤3：初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE emotion_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移（如需要）
alembic upgrade head

# 导入初始数据（可选）
mysql -u root -p emotion_platform < sql/init_admin.sql
mysql -u root -p emotion_platform < sql/seed_admin.sql
mysql -u root -p emotion_platform < sql/seed_shop.sql
```

#### 步骤4：启动后端服务

```bash
# 返回到 backend 目录
cd /path/to/backend

# 启动 FastAPI 服务（开发模式）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动，API文档可访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3️⃣ 前端启动

#### 步骤1：安装依赖

```bash
cd frontend

# 安装项目依赖
npm install
```

#### 步骤2：启动开发服务器

```bash
# 启动 Vite 开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

#### 步骤3（可选）：生产构建

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 🔐 API 端点速览

| 功能 | 方法 | 端点 |
|------|------|------|
| 用户注册 | POST | `/api/auth/register` |
| 用户登录 | POST | `/api/auth/login` |
| 获取用户信息 | GET | `/api/user/profile` |
| 更新用户信息 | PUT | `/api/user/profile` |
| 好友列表 | GET | `/api/friends` |
| 发送好友请求 | POST | `/api/friends/request` |
| 社区帖子 | GET | `/api/posts` |
| 发布帖子 | POST | `/api/posts` |
| 私聊消息 | GET/POST | `/api/private-message` |

完整API文档请访问 `http://localhost:8000/docs`

## 📁 项目结构

```
emotionagent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── routers/           # API 路由
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── utils/             # 工具函数
│   │   └── middleware.py      # 中间件
│   ├── agent/                 # AI Agent 相关
│   ├── RAG/                   # RAG 模块
│   ├── requirements.txt       # Python 依赖
│   ├── .env                   # 环境变量（需创建）
│   └── alembic/               # 数据库迁移
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── main.js            # 应用入口
│   │   ├── App.vue            # 根组件
│   │   ├── router/            # 路由配置
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 可复用组件
│   │   ├── api/               # API 请求模块
│   │   └── styles/            # 全局样式
│   ├── package.json           # npm 依赖
│   ├── vite.config.js         # Vite 配置
│   └── index.html             # 入口 HTML
└── README.md                  # 项目说明
```

## 🔧 常见问题

### Q1: MySQL 连接失败怎么办？

**检查步骤：**
1. 确认 MySQL 服务在运行：`mysql --version`
2. 验证连接配置在 `.env` 文件中正确
3. 检查用户权限：
   ```bash
   mysql -u root -p -e "SHOW GRANTS FOR 'your_user'@'localhost';"
   ```

### Q2: 端口被占用怎么办？

**后端（修改端口）：**
```bash
uvicorn app.main:app --reload --port 8001
```

**前端（修改 vite.config.js）：**
```javascript
export default {
  server: {
    port: 5174
  }
}
```

### Q3: 前端无法连接后端？

检查 `backend/app/config.py` 中的 CORS 配置：
```python
CORS_ORIGINS=["http://localhost:5173"]  # 确保前端地址正确
```

### Q4: 虚拟环境激活失败？

```bash
# 删除旧虚拟环境并重建
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

## 📝 开发工作流

### 后端开发

1. **修改代码**：编辑 `backend/app/` 中的文件
2. **自动重载**：使用 `--reload` 标志会自动重启服务
3. **查看日志**：终端输出会显示详细日志

### 前端开发

1. **修改代码**：编辑 `frontend/src/` 中的文件
2. **热更新**：Vite 会自动刷新浏览器
3. **API 调试**：使用浏览器开发者工具调试

## 🗄️ 数据库初始化

如果需要从零开始初始化数据库：

```bash
cd backend

# 清除旧迁移（如需要）
# alembic downgrade base

# 创建新迁移
alembic revision --autogenerate -m "Initial schema"

# 应用迁移
alembic upgrade head
```

## 🔑 默认凭证

| 账户 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 后台管理登录 |

**⚠️ 警告**：这些是默认凭证，**生产环境必须修改！**

## 📦 依赖版本

### 后端主要依赖
- FastAPI 0.115.0
- SQLAlchemy 2.0.34
- Uvicorn 0.30.6
- PyMySQL 1.1.1
- LangChain 0.3.0+
- MCP 1.0.0+

### 前端主要依赖
- Vue 3.5.10
- Element Plus 2.8.7
- Axios 1.7.7
- Vite 5.4.8

## 🚢 部署建议

### 生产环境检查清单

- [ ] 修改 `.env` 中的 `JWT_SECRET_KEY`
- [ ] 设置 `DEBUG=false`
- [ ] 配置正确的 MySQL 凭证
- [ ] 更新 CORS_ORIGINS 为实际域名
- [ ] 配置 SMTP 邮件服务（可选）
- [ ] 建议使用 Gunicorn/Uvicorn 作为 WSGI 服务器
- [ ] 使用 Nginx 反向代理
- [ ] 启用 HTTPS
- [ ] 配置数据库备份策略

### 使用 Docker 部署（可选）

```bash
# 构建镜像
docker build -t emotion-platform:latest .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e MYSQL_HOST=db \
  -e DEBUG=false \
  emotion-platform:latest
```

## 📞 获取帮助

- 查看 `后续开发计划与提示词.md` 了解项目规划
- 查看代码注释了解实现细节
- 使用 FastAPI Swagger UI (`/docs`) 测试 API

## 📄 License

MIT License - 详见 LICENSE 文件

## 👥 贡献指南

欢迎提交问题和改进建议！

---

**祝你使用愉快！🎉**
