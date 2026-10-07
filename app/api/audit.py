"""
CodeSecure AI — Audit Log API Endpoints
Provides security compliance event retrieval with role-based access restrictions.
"""

from typing import Any, Dict, List, Optional
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas import AuditLogEntry
from app.security.authorization import has_permission, Permission
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("audit_api")
router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogEntry])
def get_audit_logs(
    action: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieves tamper-evident audit logs.
    Restricted to Security Engineers and Admins.
    """
    if not has_permission(user["role"], Permission.AUDIT_VIEW):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Audit logs are restricted to Security Engineers and Administrators.",
        )

    logs = security_service.get_audit_logs(limit=limit, action_filter=action)
    return [AuditLogEntry(**l) for l in logs]
