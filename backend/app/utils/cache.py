"""
Redis 缓存工具

提供函数结果缓存装饰器、缓存失效等功能。
"""

import functools
import hashlib
import json
import logging
from typing import Any, Callable

from app.redis import get_redis

logger = logging.getLogger("cache")

# 缓存键前缀
CACHE_PREFIX = "cache:"


def _make_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存键"""
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()[:16]
    return f"{CACHE_PREFIX}{prefix}:{digest}"


def cache_result(ttl: int = 60, prefix: str = "api"):
    """
    异步函数结果缓存装饰器。
    使用 Redis 存储 JSON 序列化后的返回值，TTL 到期自动失效。

    Usage:
        @cache_result(ttl=300, prefix="shop")
        async def get_products(category_id: int):
            ...

    Args:
        ttl: 缓存有效期（秒），默认 60
        prefix: 缓存键前缀，方便按模块批量失效
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            r = await get_redis()
            key = _make_key(prefix, func.__name__, *args, **kwargs)

            # 尝试读取缓存
            cached = await r.get(key)
            if cached is not None:
                logger.debug("cache_hit", extra={"key": key})
                return json.loads(cached)

            # 执行原函数并缓存
            result = await func(*args, **kwargs)
            await r.setex(key, ttl, json.dumps(result, ensure_ascii=False, default=str))
            logger.debug("cache_set", extra={"key": key, "ttl": ttl})
            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str) -> int:
    """
    按模式批量删除缓存键。

    Args:
        pattern: 匹配模式，如 "cache:shop:*"

    Returns:
        删除的键数量
    """
    r = await get_redis()
    keys = []
    async for key in r.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        return await r.delete(*keys)
    return 0


async def get_cached(key: str) -> str | None:
    """读取缓存值"""
    r = await get_redis()
    return await r.get(key)


async def set_cached(key: str, value: str, ttl: int = 60) -> None:
    """写入缓存"""
    r = await get_redis()
    await r.setex(key, ttl, value)
