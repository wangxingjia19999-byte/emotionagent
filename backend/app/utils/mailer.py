import logging
import smtplib
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("mailer")


def send_verification_email(to_email: str, code: str) -> bool:
    """发送验证码邮件。成功返回 True，失败返回 False。"""
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

    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info("verification_code_sent", extra={"to": to_email})
        return True
    except Exception as e:
        logger.error("send_verification_email_failed", extra={"to": to_email, "error": str(e)})
        return False
