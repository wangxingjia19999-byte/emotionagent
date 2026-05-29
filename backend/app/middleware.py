"""全局中间件：请求 ID 追踪、结构化日志、统一异常处理"""

import time
import traceback
import uuid

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求注入唯一 trace_id，并在响应头返回"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        request.state.request_id = request_id
        request.state.start_time = time.time()

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{(time.time() - request.state.start_time) * 1000:.0f}ms"
        return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """捕获所有未处理异常，返回统一格式"""
    request_id = getattr(request.state, "request_id", "unknown")
    trace_id = uuid.uuid4().hex[:8]

    # 记录完整错误
    import logging
    logger = logging.getLogger("app")
    logger.error(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "trace_id": trace_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误" if not settings.debug else str(exc),
            "trace_id": trace_id,
        },
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """统一 HTTPException 返回格式"""
    from fastapi.exceptions import HTTPException as FastAPIHTTPException

    if isinstance(exc, FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
            },
        )

    return await global_exception_handler(request, exc)
