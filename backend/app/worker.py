"""
arq 后台 Worker

定义异步任务，由 arq worker 进程执行。
所有任务通过 Redis 队列调度，与 FastAPI 主进程分离。

启动方式:
    arq backend.app.worker.WorkerSettings
"""

import smtplib
from email.mime.text import MIMEText

from arq.connections import RedisSettings

from app.config import settings as app_settings


# ── arq Worker 配置 ──────────────────────────────────

class WorkerSettings:
    """arq worker 配置类"""
    functions: list = []  # 将在文件末尾注册
    redis_settings = RedisSettings(
        host=app_settings.redis_host,
        port=app_settings.redis_port,
        password=app_settings.redis_password or None,
        database=app_settings.redis_db,
    )
    max_jobs = 20
    job_timeout = 60  # 单任务最大 60 秒
    keep_result = 300  # 结果保留 5 分钟
    health_check_interval = 5


# ── 后台任务定义 ─────────────────────────────────────

async def send_email_task(ctx, to_email: str, subject: str, body: str) -> bool:
    """
    异步发送邮件。
    由邮件验证码、通知等场景入队调用。
    """
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = app_settings.smtp_from or app_settings.smtp_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP(app_settings.smtp_host, app_settings.smtp_port, timeout=15) as server:
            server.starttls()
            if app_settings.smtp_user and app_settings.smtp_password:
                server.login(app_settings.smtp_user, app_settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        # arq 会自动记录异常，这里简单返回失败
        return False


async def send_verification_email_task(ctx, to_email: str, code: str) -> bool:
    """异步发送验证码邮件（专用任务，封装了邮件模板）"""
    subject = "【心语陪伴】邮箱验证码"
    body = f"""<div style="max-width:480px;margin:0 auto;padding:32px 24px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
background:#f8f9fc;border-radius:18px;text-align:center">
  <h2 style="color:#6074df;margin:0 0 8px">心语陪伴</h2>
  <p style="color:#6a7281;margin:0 0 24px">让情绪被看见，让陪伴更靠近</p>
  <div style="background:#fff;border-radius:14px;padding:28px 20px;
box-shadow:0 8px 24px rgba(44,52,73,.06)">
    <p style="margin:0 0 8px;color:#526073">你的验证码是</p>
    <p style="font-size:32px;font-weight:700;letter-spacing:6px;
color:#6074df;margin:0 0 16px">{code}</p>
    <p style="margin:0;font-size:12px;color:#a9b1be">
      5 分钟内有效，请勿转发给他人
    </p>
  </div>
</div>"""
    return await send_email_task(ctx, to_email, subject, body)


async def save_emotion_log_task(
    ctx,
    user_id: int,
    emotion_label: str,
    intensity: int,
    raw_text: str = "",
) -> dict:
    """异步保存情绪记录到数据库"""
    from app.database import SessionLocal
    from app.models.emotion_log import EmotionLog

    db = SessionLocal()
    try:
        log = EmotionLog(
            user_id=user_id,
            emotion_label=emotion_label[:50],
            intensity=max(1, min(5, intensity)),
            raw_text=raw_text[:500] if raw_text else None,
        )
        db.add(log)
        db.commit()
        return {"id": log.id, "emotion_label": emotion_label}
    finally:
        db.close()


async def send_notification_email_task(
    ctx,
    to_email: str,
    title: str,
    message: str,
) -> bool:
    """异步发送通知邮件（好友申请、系统通知等）"""
    subject = f"【心语陪伴】{title}"
    body = f"""<div style="max-width:480px;margin:0 auto;padding:32px 24px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
background:#f8f9fc;border-radius:18px">
  <h2 style="color:#6074df;margin:0 0 16px">心语陪伴</h2>
  <div style="background:#fff;border-radius:14px;padding:24px 20px;
box-shadow:0 8px 24px rgba(44,52,73,.06)">
    <p style="margin:0;color:#526073;line-height:1.8">{message}</p>
  </div>
  <p style="margin:16px 0 0;font-size:12px;color:#a9b1be;text-align:center">
    此邮件由系统自动发送，请勿回复
  </p>
</div>"""
    return await send_email_task(ctx, to_email, subject, body)


# ── 注册所有任务到 Worker ─────────────────────────────

WorkerSettings.functions = [
    send_email_task,
    send_verification_email_task,
    save_emotion_log_task,
    send_notification_email_task,
]
