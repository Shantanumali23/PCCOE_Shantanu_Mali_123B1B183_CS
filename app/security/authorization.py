"""
CodeSecure AI — Authorization & RBAC Module
Enforces Role-Based Access Control across Developer, Reviewer, Security Engineer, and Admin roles.
"""

from enum import Enum
from typing import Dict, List, Set


class Role(str, Enum):
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    SECURITY_ENGINEER = "security_engineer"
    ADMIN = "admin"


# Granular Permissions
class Permission(str, Enum):
    CODE_UPLOAD = "code:upload"
    REVIEW_REQUEST = "review:request"
    LOG_ANALYZE = "log:analyze"
    FINDINGS_VIEW = "findings:view"
    FINDINGS_DISPOSITION = "findings:disposition"  # Confirm/reject/fix findings
    SECURITY_REVIEW = "review:security"
    AUDIT_VIEW = "audit:view"
    RAG_INGEST = "rag:ingest"
    PROJECT_MANAGE = "project:manage"
    USER_MANAGE = "user:manage"
    SYSTEM_CONFIG = "system:config"


ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.DEVELOPER: {
        Permission.CODE_UPLOAD,
        Permission.REVIEW_REQUEST,
        Permission.LOG_ANALYZE,
        Permission.FINDINGS_VIEW,
    },
    Role.REVIEWER: {
        Permission.CODE_UPLOAD,
        Permission.REVIEW_REQUEST,
        Permission.LOG_ANALYZE,
        Permission.FINDINGS_VIEW,
        Permission.FINDINGS_DISPOSITION,
        Permission.SECURITY_REVIEW,
    },
    Role.SECURITY_ENGINEER: {
        Permission.CODE_UPLOAD,
        Permission.REVIEW_REQUEST,
        Permission.LOG_ANALYZE,
        Permission.FINDINGS_VIEW,
        Permission.FINDINGS_DISPOSITION,
        Permission.SECURITY_REVIEW,
        Permission.AUDIT_VIEW,
        Permission.RAG_INGEST,
    },
    Role.ADMIN: {
        Permission.CODE_UPLOAD,
        Permission.REVIEW_REQUEST,
        Permission.LOG_ANALYZE,
        Permission.FINDINGS_VIEW,
        Permission.FINDINGS_DISPOSITION,
        Permission.SECURITY_REVIEW,
        Permission.AUDIT_VIEW,
        Permission.RAG_INGEST,
        Permission.PROJECT_MANAGE,
        Permission.USER_MANAGE,
        Permission.SYSTEM_CONFIG,
    },
}


def has_permission(user_role: str, permission: Permission) -> bool:
    """Verifies whether a given role holds the requested permission."""
    try:
        role_enum = Role(user_role.lower())
        allowed = ROLE_PERMISSIONS.get(role_enum, set())
        return permission in allowed
    except (ValueError, KeyError):
        return False


def is_role_authorized_for_repo(user_role: str, repo_authorized_roles: str) -> bool:
    """
    Checks if user's role is permitted to access a specific repository.
    repo_authorized_roles is a comma-separated string of roles or '*' for all.
    """
    if not repo_authorized_roles or repo_authorized_roles.strip() == "*":
        return True
    allowed_list = [r.strip().lower() for r in repo_authorized_roles.split(",")]
    if "admin" in user_role.lower():
        return True
    return user_role.lower() in allowed_list
