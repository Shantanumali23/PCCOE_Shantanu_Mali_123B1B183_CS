"""
CodeSecure AI — Findings Management & Reviewer Disposition Endpoints
Supports finding queries, filtering, and reviewer disposition updates (Confirm, Reject, Mark Fixed).
"""

from typing import Any, Dict, List, Optional
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.schemas import FindingResponse, FindingStatusUpdate
from app.security.authorization import has_permission, Permission
from app.services.finding_service import finding_service
from app.utils.logging_utils import get_logger

logger = get_logger("findings_api")
router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get("", response_model=List[FindingResponse])
def get_findings(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    review_session_id: Optional[int] = None,
    limit: int = 100,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Lists findings with optional filtering by severity, category, or review status."""
    if not has_permission(user["role"], Permission.FINDINGS_VIEW):
        raise HTTPException(status_code=403, detail="Unauthorized to view findings.")

    items = finding_service.get_findings(
        severity=severity,
        category=category,
        status=status,
        review_session_id=review_session_id,
        limit=limit,
    )
    return items


@router.patch("/{finding_id}")
def update_finding_disposition(
    finding_id: int,
    update: FindingStatusUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Updates finding disposition (Human-in-the-loop review governance).
    Permitted for Reviewer, Security Engineer, and Admin roles.
    """
    if not has_permission(user["role"], Permission.FINDINGS_DISPOSITION):
        raise HTTPException(
            status_code=403,
            detail="Role not authorized to disposition findings (requires reviewer, security_eng, or admin).",
        )

    try:
        updated = finding_service.update_disposition(
            finding_id=finding_id,
            update=update,
            user_id=user["id"],
            username=user["username"],
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Finding not found.")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
