"""
CodeSecure AI — Compiler & Log Analysis API Endpoint
Receives diagnostic and crash logs and returns parsed, structured findings with RAG grounding.
"""

from typing import Any, Dict
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.schemas import LogAnalysisRequest, LogAnalysisResponse
from app.security.authorization import has_permission, Permission
from app.services.log_analysis_service import log_analysis_service
from app.utils.logging_utils import get_logger

logger = get_logger("logs_api")
router = APIRouter(prefix="/reviews", tags=["Log Analysis"])


@router.post("/log", response_model=LogAnalysisResponse)
def analyze_logs(
    request: LogAnalysisRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Submits compiler diagnostics or runtime logs for structured defect extraction and guideline linking.
    """
    if not has_permission(user["role"], Permission.LOG_ANALYZE):
        raise HTTPException(status_code=403, detail="Unauthorized to analyze logs.")

    try:
        response = log_analysis_service.parse_log(
            request=request,
            user_id=user["id"],
            username=user["username"],
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Log parsing error: {e}")
        raise HTTPException(status_code=500, detail="Internal log analysis error.")
