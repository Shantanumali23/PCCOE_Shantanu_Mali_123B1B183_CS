"""
CodeSecure AI — Findings Management & Reviewer Disposition Service
Provides querying, filtering, and reviewer disposition workflows (Confirm, Reject, Mark Fixed, Needs Review).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.db import get_db_context, SQLALCHEMY_AVAILABLE
from app.models import Finding
from app.schemas import FindingResponse, FindingStatusUpdate
from app.services.review_service import IN_MEMORY_FINDINGS
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("finding_service")


class FindingService:
    """Manages finding lifecycles and human-in-the-loop disposition."""

    VALID_STATUSES = {"Open", "Confirmed", "Rejected", "Fixed", "Needs Review"}

    def get_findings(
        self,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        review_session_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieves findings matching specified filter criteria."""
        if SQLALCHEMY_AVAILABLE:
            try:
                with get_db_context() as db:
                    if db:
                        query = db.query(Finding)
                        if severity:
                            query = query.filter(Finding.severity == severity)
                        if category:
                            query = query.filter(Finding.category == category)
                        if status:
                            query = query.filter(Finding.status == status)
                        if review_session_id:
                            query = query.filter(Finding.review_session_id == review_session_id)

                        records = query.order_by(Finding.id.desc()).limit(limit).all()
                        results = []
                        for r in records:
                            citations = [c.citation_code for c in r.citations]
                            results.append({
                                "id": r.id,
                                "review_session_id": r.review_session_id,
                                "finding_code": r.finding_code,
                                "severity": r.severity,
                                "category": r.category,
                                "file": r.file,
                                "function": r.function,
                                "line": r.line,
                                "issue": r.issue,
                                "evidence": r.evidence,
                                "root_cause": r.root_cause,
                                "recommendation": r.recommendation,
                                "rule": r.rule,
                                "confidence": r.confidence,
                                "status": r.status,
                                "reviewer_comment": r.reviewer_comment,
                                "citations": citations,
                                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                            })
                        return results
            except Exception as e:
                logger.warning(f"Error reading findings from DB: {e}. Checking memory buffer.")

        # Fallback to in-memory findings
        results = []
        for f in IN_MEMORY_FINDINGS.values():
            if severity and f.get("severity") != severity:
                continue
            if category and f.get("category") != category:
                continue
            if status and f.get("status") != status:
                continue
            if review_session_id and f.get("review_session_id") != review_session_id:
                continue
            results.append(f)
        return list(reversed(results[-limit:]))

    def update_disposition(
        self,
        finding_id: int,
        update: FindingStatusUpdate,
        user_id: Optional[int] = None,
        username: Optional[str] = "reviewer",
    ) -> Optional[Dict[str, Any]]:
        """
        Updates the review disposition of an AI-generated finding.
        Enforces human-in-the-loop governance.
        """
        if update.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{update.status}'. Allowed: {self.VALID_STATUSES}")

        now = datetime.now(timezone.utc)
        updated_record = None

        if SQLALCHEMY_AVAILABLE:
            try:
                with get_db_context() as db:
                    if db:
                        finding = db.query(Finding).filter(Finding.id == finding_id).first()
                        if finding:
                            finding.status = update.status
                            finding.reviewer_comment = update.reviewer_comment
                            finding.updated_at = now
                            db.commit()
                            updated_record = {
                                "id": finding.id,
                                "finding_code": finding.finding_code,
                                "status": finding.status,
                                "reviewer_comment": finding.reviewer_comment,
                                "updated_at": now.isoformat(),
                            }
            except Exception as e:
                logger.error(f"Error updating finding in DB: {e}")

        # Update in-memory record as well
        if finding_id in IN_MEMORY_FINDINGS:
            f = IN_MEMORY_FINDINGS[finding_id]
            f["status"] = update.status
            f["reviewer_comment"] = update.reviewer_comment
            f["updated_at"] = now.isoformat()
            if not updated_record:
                updated_record = f

        if updated_record:
            security_service.log_event(
                action="FINDING_DISPOSITION_UPDATED",
                resource=f"finding:{finding_id}",
                status="SUCCESS",
                user_id=user_id,
                username=username,
                details=f"NewStatus={update.status}, Comment={update.reviewer_comment or 'None'}",
            )

        return updated_record


# Singleton instance
finding_service = FindingService()
