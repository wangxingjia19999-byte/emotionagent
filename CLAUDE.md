# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

心语陪伴 (XinYu Companion) — a full-stack emotional companionship and social mutual-help platform. Vue 3 + Element Plus frontend, FastAPI backend, with AI-powered emotional support via LangChain/LangGraph agents, RAG knowledge retrieval, and MCP protocol integration.

## Commands

### Backend (Python/FastAPI)

```bash
cd backend
source venv/bin/activate

# Start dev server (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start arq background worker (async emails, emotion logs)
python -m arq backend.app.worker.WorkerSettings

# Start MCP server (expose platform tools to external AI apps)
python -m mcp_server.server                              # HTTP mode :8765
python -m mcp_server.server --transport sse              # SSE mode
python -m mcp_server.server --transport stdio            # stdio mode

# DB migrations
alembic revision --autogenerate -m "description"         # create migration
alembic upgrade head                                     # apply all migrations
alembic downgrade -1                                     # rollback one

# Initialize DB from scratch
mysql -u root -p -e "CREATE DATABASE emotion_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p emotion_platform < sql/init_all_tables.sql
```

### Frontend (Vue 3 / Vite)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production build
```

### Convenience Scripts

```bash
./start.sh          # setup venv, deps, print launch instructions
./start_worker.sh   # start arq worker with Redis health check
./start_mcp.sh      # start MCP server (HTTP mode, :8765)
```

## Architecture

### Backend Layer (`backend/app/`)

**Entry & Wiring:** `main.py` creates the FastAPI app, registers all routers under `/api` prefix, mounts middleware (CORS → RequestID → global exception handlers), and wires lifecycle events (Redis, arq, auto-create tables in dev).

**Config:** `config.py` uses `pydantic-settings` with `.env` file. Key settings: MySQL DSN, JWT secrets, OpenAI-compatible LLM (defaults to Aliyun Bailian qwen-plus), Redis URL, SMTP, CORS origins.

**Database:** `database.py` creates SQLAlchemy engine with connection pooling (pool_size=20, pool_recycle=3600). `get_db()` yields sessions — use as FastAPI `Depends`.

**Auth flow:** `utils/jwt.py` — JWT with `python-jose`, `HTTPBearer` auto-error, Redis-backed token blacklist on logout. `get_current_user` / `get_current_admin` for dependency injection. Two separate auth routers: `auth.py` (users) and `admin_auth.py` (admins).

**Models** (SQLAlchemy ORM, all imported at startup in `main.py`):
- `user.py` — User (id, username, email, password_hash, role)
- `admin.py` — Admin (separate table from User)
- `post.py` — Post + Comment (community forum)
- `shop.py` — Product, ProductCategory, Order, OrderItem, CartItem, UserAddress
- `friend.py` — FriendRequest, Friendship
- `questionnaire.py` — QuestionnaireRecord
- `emotion_log.py` — EmotionLog
- `crisis_alert.py` — CrisisAlert
- `ai_chat_session.py` — AiChatSession (chat history persistence)
- `audit_log.py` — AuditLog (admin action auditing)
- `verification_code.py` — VerificationCode
- `user_profile.py` — UserProfile
- `mcp_config.py` — MCP server configs

**Routers:** Each router file handles a domain. `admin.py` is the largest (~1000 lines), with role checks (`get_current_admin`, `_require_super_admin`) and audit logging (`_write_audit`).

**Background tasks:** `worker.py` defines arq tasks (`send_verification_email_task`, `save_emotion_log_task`, `send_notification_email_task`). `tasks.py` provides enqueue helpers. Redis required for both.

### AI Agent Layer (`backend/agent/`)

Three tiers of increasing capability:

1. **Basic RAG** (`agent_service.py` → `RAG/enterprise_rag_app.py`):
   - Singleton `AgentService` wraps `EmotionAnalystRAG`
   - `EmotionAnalystRAG`: ChromaDB vector store + `BAAI/bge-small-zh-v1.5` embeddings (MPS-optimized for macOS) + `MultiQueryRetriever` + LLM via LangChain LCEL chain
   - Knowledge base: `RAG/emotion_knowledge_base.md`
   - API: `POST /api/agent/chat`

2. **Enhanced Agent** (`mcp_agent.py`):
   - `MCPEmotionAgent` — LangGraph ReAct agent with emotion tools + optional MCP external tools
   - API: `POST /api/agent/chat/enhanced` (requires auth)

3. **Multi-Agent** (`multi_agent.py`):
   - Custom `StateGraph` (NOT Supervisor pattern — explicit routing to avoid skipped tool calls)
   - Pipeline: crisis keyword detection → LLM intent classifier (`shopping` | `emotion` | `greeting`) → domain-specific sub-agent
   - Emotion companion has 15+ tools: RAG query, profile, emotion history, memory read/write, assessment, community posts, shop browsing
   - API: `POST /api/agent/chat/multi` (requires auth)

**Tool functions** live in `agent_service.py` (lines 60+): `query_emotion_knowledge_base`, `get_user_profile`, `get_emotion_history`, `save_conversation_memory`, `get_recent_memory`, `get_shop_products`, `recommend_shop_products`, community tools, etc. These are shared between `mcp_agent.py` and `multi_agent.py`.

**Conversation memory:** File-based JSONL at `backend/agent/memory/conversation_memory.jsonl` (per-user). Simple append+read-last-N pattern.

### MCP Server (`backend/mcp_server/`)

Uses `FastMCP` to expose platform capabilities as MCP tools/resources/prompts for external AI applications (Claude Desktop, VS Code, etc.). Tools split across `tools/emotion_tools.py` (user-facing) and `tools/knowledge_tools.py` (knowledge retrieval). Resources in `resources/emotion_resources.py`.

### Frontend (`frontend/src/`)

- **Router** (`router/index.js`): `createWebHistory`, lazy-loaded views, two layouts (public `Layout` + `/admin` with `AdminLayout`). Route guards check `localStorage.access_token` + admin role.
- **API layer** (`api/`): each file wraps axios calls to a backend domain. `request.js` is the shared axios instance with interceptors.
- **Views**: Core user flow — Home → Login/Register → AiChat, Community, Friends, Shop, DailyCheck, Profile. Admin flow — Dashboard with 12 management pages.
- **Component library**: Element Plus (el-* components). No custom design system.

### Infrastructure & Data Flow

```
Browser → Vite dev server (:5173) → FastAPI (:8000) → MySQL
                                      ├── Redis (cache / token blacklist / arq queue)
                                      ├── arq Worker (emails, emotion logs)
                                      ├── Agent (ChromaDB RAG + LLM via Aliyun Bailian)
                                      └── MCP Server (:8765) → External AI apps
```

## Key Conventions

- **API response format:** `{ "code": int, "message": str, "data": Any }` — code=0 means success
- **Auth:** JWT in `Authorization: Bearer <token>` header. Tokens blacklisted in Redis on logout.
- **LLM:** Uses OpenAI-compatible API (default: Aliyun Bailian `qwen-plus`). Configured via `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL_NAME` in `.env`.
- **Dev DB:** `main.py` calls `Base.metadata.create_all()` on startup in dev. Production should use alembic only.
- **No test suite exists** — the project has zero test files.
- **Rate limiting:** slowapi with in-memory storage (dev). Production should switch to Redis storage.
