# 🚀 快速启动指南

> 这是一份 **5 分钟快速启动** 参考手册

## 方案 A：自动启动（推荐 ⭐）

### macOS / Linux
```bash
chmod +x start.sh
./start.sh
```

### Windows
```bash
start.bat
```

脚本会自动：
✅ 检查前置条件  
✅ 创建虚拟环境  
✅ 安装依赖  
✅ 显示启动步骤  

---

## 方案 B：手动启动

### 步骤 1：准备数据库

```bash
# macOS/Linux/Windows 使用 MySQL 客户端
mysql -u root -p

# 在 MySQL 中执行
CREATE DATABASE emotion_platform 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 步骤 2：配置后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置 .env 文件
cp .env.example .env
# 编辑 .env，填入你的 MySQL 密码等配置

# 应用数据库迁移
alembic upgrade head
```

### 步骤 3：启动后端

```bash
# 在后端目录，虚拟环境已激活的情况下
uvicorn app.main:app --reload --port 8000
```

✅ 后端在 `http://localhost:8000`

### 步骤 4：启动前端（**新的终端窗口**）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

✅ 前端在 `http://localhost:5173`

---

## 📱 访问应用

| 应用 | URL | 说明 |
|------|-----|------|
| **前端** | http://localhost:5173 | 用户界面 |
| **后端 API** | http://localhost:8000 | 接口基地址 |
| **API 文档** | http://localhost:8000/docs | Swagger UI（推荐） |
| **API 文档** | http://localhost:8000/redoc | ReDoc |

---

## 🔧 常见问题速查

### ❌ 虚拟环境激活失败

```bash
# 删除重建
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
```

### ❌ MySQL 连接失败

1. 确认 MySQL 正在运行
2. 检查 `.env` 中的数据库配置
3. 验证密码正确

### ❌ 端口被占用

```bash
# 更换后端端口
uvicorn app.main:app --reload --port 8001

# 前端的话修改 vite.config.js 中的 port 配置
```

### ❌ npm install 很慢

```bash
# 使用淘宝镜像
npm install -g cnpm --registry=https://registry.npm.taobao.org
cnpm install
```

---

## 📝 环境变量速查

最重要的配置项 (.env)：

```env
# 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=emotion_platform

# JWT 密钥（开发可用默认值，生产必须修改！）
JWT_SECRET_KEY=your-secret-key-here

# 调试模式（开发时设为 true）
DEBUG=true
```

---

## ✨ 验证启动成功

### 后端检查
```bash
# 在浏览器中访问
http://localhost:8000/docs

# 或用 curl 测试
curl http://localhost:8000/
```

### 前端检查
```bash
# 浏览器访问
http://localhost:5173

# 应该看到登录或首页界面
```

---

## 📂 项目结构记住这些就够了

```
emotionagent/
├── backend/          # 🔧 后端服务
│   ├── app/         # ⚙️ FastAPI 应用
│   ├── requirements.txt  # 📦 依赖列表
│   └── .env         # 🔑 环境配置
├── frontend/        # 🎨 前端应用
│   └── src/        # 💻 源代码
└── README.md       # 📖 完整文档
```

---

## 🎯 下一步

当成功启动后，可以：

✅ 在 http://localhost:5173 注册账户  
✅ 测试登录功能  
✅ 查看 API 文档 http://localhost:8000/docs  
✅ 开始开发功能  

---

## 🆘 遇到问题？

1. 查看 `README.md` 获取详细说明
2. 检查终端输出的错误信息
3. 查看 `后续开发计划与提示词.md` 了解项目详情

---

**祝你启动顺利！🎉**
