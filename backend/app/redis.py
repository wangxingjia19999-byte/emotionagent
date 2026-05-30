"""
Redis 连接管理模块

提供全局异步 Redis 客户端，在 FastAPI 生命周期中管理连接。
"""

import logging

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger("redis")

# 全局 Redis 客户端（异步）
redis_client: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis:
    """初始化 Redis 连接池"""
    global redis_client
    redis_client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=50,
        socket_timeout=5,
        socket_connect_timeout=5,
    )
    # 连接验证
    await redis_client.ping()
    logger.info("redis_connected", extra={"url": settings.redis_url})
    return redis_client


async def close_redis() -> None:
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("redis_disconnected")


async def get_redis() -> aioredis.Redis:
    """获取 Redis 客户端（依赖注入用）"""
    if redis_client is None:
        raise RuntimeError("Redis 未初始化，请先调用 init_redis()")
    return redis_client
