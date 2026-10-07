"""
CodeSecure AI — Evaluation API Endpoints
Runs reproducible evaluation and retrieves measured performance telemetry.
"""

from typing import Any, Dict
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.schemas import EvaluationMetrics
from app.security.authorization import has_permission, Permission
from app.services.evaluation_service import evaluation_service
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("evaluation_api")
router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/results", response_model=EvaluationMetrics)
def get_evaluation_results(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns latest measured evaluation metrics.
    Reports 'Not yet executed' if evaluation has not been initiated.
    """
    results = evaluation_service.get_results()
    return EvaluationMetrics(**results)


@router.post("/run", response_model=EvaluationMetrics)
def run_evaluation(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes automated evaluation pipeline across synthetic test cases against ground truth.
    Available to Reviewers, Security Engineers, and Admins.
    """
    if not has_permission(user["role"], Permission.FINDINGS_DISPOSITION):
        raise HTTPException(status_code=403, detail="Unauthorized to trigger evaluation pipeline.")

    report = evaluation_service.run_evaluation()

    security_service.log_event(
        action="EVALUATION_RUN_COMPLETED",
        resource="evaluation_pipeline",
        user_id=user["id"],
        username=user["username"],
        details=f"TestCases={report['test_cases_evaluated']}, F1={report['f1_score']}",
    )

    return EvaluationMetrics(**report)
