# 后端启动说明

## 数据库

先在 MySQL 中创建数据库：

```sql
CREATE DATABASE emotion_platform
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

项目启动后会自动创建 `users` 表。

## 配置

1. 复制 `.env.example` 为 `.env`
2. 修改数据库账号、密码和 JWT 密钥

## 安装与启动

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 接口地址

- Swagger: http://127.0.0.1:8000/docs
- 注册: POST /api/auth/register
- 登录: POST /api/auth/login
- 当前用户: GET /api/user/profile

## 初始化管理员账号

如果需要先创建管理员和系统管理员账号，可以在 `users` 表已生成后执行 [sql/init_admin.sql](sql/init_admin.sql)。
