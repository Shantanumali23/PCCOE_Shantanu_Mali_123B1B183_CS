"""
CodeSecure AI — Code Review & Project Management Endpoints
Handles source code submission, review execution, and project/repository registration.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.db import get_db, SQLALCHEMY_AVAILABLE
from app.models import Project, Repository, ReviewSession
from app.schemas import (
    CodeReviewRequest,
    CodeReviewResponse,
    ProjectCreate,
    ProjectResponse,
    RepositoryCreate,
    RepositoryResponse,
)
from app.security.authorization import has_permission, Permission, is_role_authorized_for_repo
from app.services.review_service import IN_MEMORY_REVIEWS, review_service
from app.utils.logging_utils import get_logger

logger = get_logger("review_api")
router = APIRouter(tags=["Reviews & Projects"])

# In-memory stores for projects and repositories
IN_MEMORY_PROJECTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Automotive ECU Telemetry",
        "description": "Embedded sensor ingestion and CAN bus communications module",
        "owner_id": 1,
        "created_at": datetime.now(timezone.utc),
    }
]
IN_MEMORY_REPOSITORIES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "project_id": 1,
        "name": "ecu-telemetry-core",
        "path": "./repositories/ecu-telemetry-core",
        "authorized_roles": "developer,reviewer,security_engineer,admin",
    }
]


# ==============================================================================
# Projects & Repositories
# ==============================================================================

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(user: Dict[str, Any] = Depends(get_current_user), db=Depends(get_db)):
    """Lists registered projects."""
    if SQLALCHEMY_AVAILABLE and db:
        try:
            projs = db.query(Project).all()
            if projs:
                return [
                    ProjectResponse(
                        id=p.id,
                        name=p.name,
                        description=p.description,
                        owner_id=p.owner_id,
                        created_at=p.created_at,
                    )
                    for p in projs
                ]
        except Exception:
            pass
    return [ProjectResponse(**p) for p in IN_MEMORY_PROJECTS]


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Creates a new project (Admin or Security Engineer only)."""
    if not has_permission(user["role"], Permission.PROJECT_MANAGE):
        raise HTTPException(status_code=403, detail="Insufficient role privileges to create projects.")

    now = datetime.now(timezone.utc)
    proj_id = len(IN_MEMORY_PROJECTS) + 1

    if SQLALCHEMY_AVAILABLE and db:
        try:
            p = Project(name=data.name, description=data.description, owner_id=user["id"], created_at=now)
            db.add(p)
            db.commit()
            db.refresh(p)
            proj_id = p.id
        except Exception as e:
            logger.error(f"Error saving project: {e}")

    record = {
        "id": proj_id,
        "name": data.name,
        "description": data.description,
        "owner_id": user["id"],
        "created_at": now,
    }
    IN_MEMORY_PROJECTS.append(record)
    return ProjectResponse(**record)


@router.get("/repositories", response_model=List[RepositoryResponse])
def list_repositories(user: Dict[str, Any] = Depends(get_current_user), db=Depends(get_db)):
    """Lists repositories accessible to user's role."""
    all_repos = []
    if SQLALCHEMY_AVAILABLE and db:
        try:
            repos = db.query(Repository).all()
            if repos:
                all_repos = [
                    {
                        "id": r.id,
                        "project_id": r.project_id,
                        "name": r.name,
                        "path": r.path,
                        "authorized_roles": r.authorized_roles,
                    }
                    for r in repos
                ]
        except Exception:
            pass

    if not all_repos:
        all_repos = IN_MEMORY_REPOSITORIES

    # Filter by user role
    allowed = [r for r in all_repos if is_role_authorized_for_repo(user["role"], r.get("authorized_roles", "*"))]
    return [RepositoryResponse(**r) for r in allowed]


@router.post("/repositories", response_model=RepositoryResponse)
def create_repository(
    data: RepositoryCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Registers a repository path (Admin only)."""
    if not has_permission(user["role"], Permission.PROJECT_MANAGE):
        raise HTTPException(status_code=403, detail="Insufficient role privileges to register repositories.")

    repo_id = len(IN_MEMORY_REPOSITORIES) + 1
    if SQLALCHEMY_AVAILABLE and db:
        try:
            r = Repository(
                project_id=data.project_id,
                name=data.name,
                path=data.path,
                authorized_roles=data.authorized_roles,
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            repo_id = r.id
        except Exception as e:
            logger.error(f"Error saving repository: {e}")

    record = {
        "id": repo_id,
        "project_id": data.project_id,
        "name": data.name,
        "path": data.path,
        "authorized_roles": data.authorized_roles,
    }
    IN_MEMORY_REPOSITORIES.append(record)
    return RepositoryResponse(**record)


# ==============================================================================
# Code Review Execution
# ==============================================================================

@router.post("/reviews/code", response_model=CodeReviewResponse)
def perform_code_review(
    review_req: CodeReviewRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Submits C/C++ code for privacy-preserving AI analysis and structured finding extraction.
    """
    if not has_permission(user["role"], Permission.CODE_UPLOAD):
        raise HTTPException(status_code=403, detail="Unauthorized to upload and review code.")

    try:
        response = review_service.review_code(
            request=review_req,
            user_id=user["id"],
            username=user["username"],
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected review error: {e}")
        raise HTTPException(status_code=500, detail="Internal review processing failure.")


@router.get("/reviews/{session_id}")
def get_review_session(
    session_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Retrieves metadata of a past review session."""
    if SQLALCHEMY_AVAILABLE and db:
        try:
            sess = db.query(ReviewSession).filter(ReviewSession.id == session_id).first()
            if sess:
                return {
                    "id": sess.id,
                    "user_id": sess.user_id,
                    "repository_id": sess.repository_id,
                    "review_type": sess.review_type,
                    "created_at": sess.created_at.isoformat() if sess.created_at else None,
                    "status": sess.status,
                    "findings_count": len(sess.findings),
                }
        except Exception:
            pass

    if session_id in IN_MEMORY_REVIEWS:
        return IN_MEMORY_REVIEWS[session_id]

    raise HTTPException(status_code=404, detail="Review session not found.")
