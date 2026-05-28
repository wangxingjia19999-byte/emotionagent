import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.middleware import RequestIDMiddleware, global_exception_handler, http_exception_handler

# ── 结构化日志 ───────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)
logger = logging.getLogger("app")

# ── 模型导入（确保 Base.metadata 感知所有表） ────────────
import app.models.friend as _friend_model  # noqa: F401
import app.models.mcp_config as _mcp_config_model  # noqa: F401
import app.models.post as _post_model  # noqa: F401
import app.models.questionnaire as _questionnaire_model  # noqa: F401
import app.models.user as _user_model  # noqa: F401
import app.models.crisis_alert as _crisis_model  # noqa: F401
import app.models.emotion_log as _emotion_log_model  # noqa: F401
import app.models.shop as _shop_model  # noqa: F401
import app.models.user_profile as _profile_model  # noqa: F401
import app.models.verification_code as _vc_model  # noqa: F401

from app.routers import agent, auth, friends, home, mcp, posts, private_message, questionnaire, shop, user

# ── 限流器 ──────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# ── App 创建 ──────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── 静态文件 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "posts").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── 中间件（顺序从外到内） ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

# ── 全局异常处理 ───────────────────────────────────────────
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, lambda req, exc: JSONResponse(
    status_code=422,
    content={"code": 422, "message": "请求参数校验失败", "data": None},
))


# ── 启动事件 ──────────────────────────────────────────────
@app.on_event("startup")
def startup() -> None:
    logger.info("app_startup", extra={"app": settings.app_name, "version": settings.app_version})

    # 自动建表（开发环境），生产环境应使用 alembic upgrade head
    Base.metadata.create_all(bind=engine)

    logger.info("app_started")


@app.on_event("shutdown")
def shutdown() -> None:
    logger.info("app_shutdown")


# ── 健康检查 ──────────────────────────────────────────────
@app.get("/health")
def health_check():
    """服务健康检查：验证数据库连接"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": settings.app_version,
    }


@app.get("/")
def root():
    return {"name": settings.app_name, "version": settings.app_version}


# ── 路由注册 ──────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(private_message.router, prefix="/api")
app.include_router(home.router, prefix="/api/home", tags=["首页"])
app.include_router(agent.router, prefix="/api")
app.include_router(mcp.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(questionnaire.router, prefix="/api")
app.include_router(shop.router, prefix="/api")
app.include_router(user.router, prefix="/api")
