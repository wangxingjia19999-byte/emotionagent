"""审计日志工具"""

import json
import logging

from app.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger("app")


def audit_log(
    user_id: int,
    action: str,
    target_type: str,
    target_id: int,
    detail: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """写入审计日志（不抛异常，不影响主流程）"""
    try:
        db = SessionLocal()
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=json.dumps(detail, ensure_ascii=False) if detail else None,
            ip_address=ip_address,
        )
        db.add(log_entry)
        db.commit()
        db.close()
        logger.info("audit_log", extra={"action": action, "user_id": user_id, "target_id": target_id})
    except Exception as e:
        logger.error("audit_log_failed", extra={"error": str(e)})
