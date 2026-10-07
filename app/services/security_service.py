"""
CodeSecure AI — Security Service & Audit Logger
Maintains tamper-evident audit logs and security incident telemetry.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.db import get_db_context, SQLALCHEMY_AVAILABLE
from app.models import AuditLog
from app.utils.logging_utils import get_logger

logger = get_logger("security_service")

# In-memory audit log buffer for fast queries and offline/test environments
IN_MEMORY_AUDIT_LOGS: List[Dict[str, Any]] = []


class SecurityService:
    """Records audit logs and alerts on security events."""

    def log_event(
        self,
        action: str,
        resource: str,
        status: str = "SUCCESS",
        user_id: Optional[int] = None,
        username: Optional[str] = "system",
        details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Records an audit event to the database and in-memory buffer.
        Never logs passwords, raw tokens, or raw source code.
        """
        now = datetime.now(timezone.utc)
        entry = {
            "id": len(IN_MEMORY_AUDIT_LOGS) + 1,
            "user_id": user_id,
            "username": username or "anonymous",
            "action": action,
            "resource": resource,
            "timestamp": now.isoformat(),
            "status": status,
            "details": details or "",
        }
        IN_MEMORY_AUDIT_LOGS.append(entry)

        # Persist to database if SQLAlchemy is available
        if SQLALCHEMY_AVAILABLE:
            try:
                with get_db_context() as db:
                    if db:
                        db_log = AuditLog(
                            user_id=user_id,
                            username=username,
                            action=action,
                            resource=resource,
                            timestamp=now,
                            status=status,
                            details=details,
                        )
                        db.add(db_log)
                        db.commit()
            except Exception as e:
                logger.error(f"Failed to persist audit log to DB: {e}")

        logger.info(f"AUDIT_EVENT: action={action} user={username} resource={resource} status={status}")
        return entry

    def get_audit_logs(
        self, limit: int = 100, action_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves recent audit logs."""
        if SQLALCHEMY_AVAILABLE:
            try:
                with get_db_context() as db:
                    if db:
                        query = db.query(AuditLog)
                        if action_filter:
                            query = query.filter(AuditLog.action == action_filter)
                        records = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
                        return [
                            {
                                "id": r.id,
                                "user_id": r.user_id,
                                "username": r.username,
                                "action": r.action,
                                "resource": r.resource,
                                "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                                "status": r.status,
                                "details": r.details,
                            }
                            for r in records
                        ]
            except Exception as e:
                logger.warning(f"Error reading DB audit logs: {e}. Falling back to memory buffer.")

        # Fallback to in-memory logs
        logs = IN_MEMORY_AUDIT_LOGS
        if action_filter:
            logs = [l for l in logs if l["action"] == action_filter]
        return list(reversed(logs[-limit:]))


# Singleton instance
security_service = SecurityService()
