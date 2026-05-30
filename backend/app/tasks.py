"""
任务入队辅助模块

封装 arq 的任务入队操作，供 FastAPI 路由层使用。
"""

from arq.connections import ArqRedis

from app.config import settings

# 全局 arq Redis 连接（用于入队，非 worker）
_arq_redis: ArqRedis | None = None


async def init_arq() -> ArqRedis:
    """初始化 arq Redis 连接池（用于入队任务）"""
    global _arq_redis
    _arq_redis = await ArqRedis.from_url(settings.redis_url)
    return _arq_redis


async def close_arq() -> None:
    """关闭 arq Redis 连接"""
    global _arq_redis
    if _arq_redis:
        await _arq_redis.close()
        _arq_redis = None


async def get_arq_redis() -> ArqRedis:
    """获取 arq Redis 连接"""
    if _arq_redis is None:
        raise RuntimeError("arq Redis 未初始化，请先调用 init_arq()")
    return _arq_redis


# ── 便捷入队函数 ──────────────────────────────────


async def enqueue_send_verification_email(to_email: str, code: str) -> str | None:
    """
    入队：发送验证码邮件。
    返回 job_id，调用方不需要等待邮件发送完成。
    """
    r = await get_arq_redis()
    job = await r.enqueue_job("send_verification_email_task", to_email, code)
    return job.job_id if job else None


async def enqueue_save_emotion_log(
    user_id: int,
    emotion_label: str,
    intensity: int,
    raw_text: str = "",
) -> str | None:
    """入队：保存情绪记录"""
    r = await get_arq_redis()
    job = await r.enqueue_job(
        "save_emotion_log_task", user_id, emotion_label, intensity, raw_text
    )
    return job.job_id if job else None


async def enqueue_notification_email(
    to_email: str,
    title: str,
    message: str,
) -> str | None:
    """入队：发送通知邮件"""
    r = await get_arq_redis()
    job = await r.enqueue_job("send_notification_email_task", to_email, title, message)
    return job.job_id if job else None
