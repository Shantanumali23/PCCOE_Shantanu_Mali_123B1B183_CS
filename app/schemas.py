"""
CodeSecure AI — Data Transfer Objects & Schemas (Pydantic)
Enforces strict JSON schema validation for structured LLM outputs, API requests, and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    # Graceful mock BaseModel if pydantic is not installed
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
        def dict(self):
            return self.__dict__
    def Field(default=None, **kwargs):
        return default


# ==============================================================================
# 1. Authentication & Users
# ==============================================================================

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "developer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==============================================================================
# 2. Projects & Repositories
# ==============================================================================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None


class RepositoryCreate(BaseModel):
    project_id: int
    name: str
    path: str
    authorized_roles: str = "developer,reviewer,security_engineer,admin"


class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    name: str
    path: str
    authorized_roles: str


# ==============================================================================
# 3. Structured Findings & Review
# ==============================================================================

class FindingCitation(BaseModel):
    document_id: str
    chunk_id: str
    citation_code: str


class StructuredFindingItem(BaseModel):
    id: str = "F001"
    severity: str = "Medium"  # Critical, High, Medium, Low, Informational
    category: str = "General"
    file: str = "source.cpp"
    function: Optional[str] = None
    line: Optional[int] = None
    issue: str
    evidence: Optional[str] = None
    root_cause: Optional[str] = None
    recommendation: str
    rule: Optional[str] = None
    confidence: float = 0.85
    status: str = "Open"
    citations: List[str] = []


class StructuredFindingsResponse(BaseModel):
    findings: List[StructuredFindingItem] = []


class CodeReviewRequest(BaseModel):
    code: str
    file_name: str = "source.cpp"
    review_type: str = "Security Review"  # Security Review, MISRA-Oriented Review, Code Explanation, General Code Review
    repository_id: Optional[int] = None


class CodeReviewResponse(BaseModel):
    review_session_id: int
    review_type: str
    file_name: str
    summary: str
    findings: List[StructuredFindingItem]
    citations_retrieved: List[Dict[str, Any]] = []
    prompt_security_status: str = "Clean"
    model_used: str = "local-llm"
    created_at: Optional[datetime] = None


# ==============================================================================
# 4. Log Analysis
# ==============================================================================

class LogAnalysisRequest(BaseModel):
    log_content: str
    log_type: str = "compiler"  # compiler, static_analysis, runtime


class LogIssueItem(BaseModel):
    file: Optional[str] = None
    line: Optional[int] = None
    error_code: Optional[str] = None
    severity: str = "Warning"
    message: str
    probable_cause: str
    suggested_step: str
    relevant_guideline: Optional[str] = None


class LogAnalysisResponse(BaseModel):
    total_issues: int
    errors: int
    warnings: int
    issues: List[LogIssueItem]
    rag_guidelines_cited: List[str] = []


# ==============================================================================
# 5. Reviewer Disposition
# ==============================================================================

class FindingStatusUpdate(BaseModel):
    status: str  # Open, Confirmed, Rejected, Fixed, Needs Review
    reviewer_comment: Optional[str] = None


class FindingResponse(BaseModel):
    id: int
    review_session_id: int
    finding_code: str
    severity: str
    category: str
    file: str
    function: Optional[str] = None
    line: Optional[int] = None
    issue: str
    evidence: Optional[str] = None
    root_cause: Optional[str] = None
    recommendation: str
    rule: Optional[str] = None
    confidence: float
    status: str
    reviewer_comment: Optional[str] = None
    citations: List[str] = []
    updated_at: Optional[datetime] = None


# ==============================================================================
# 6. RAG Schemas
# ==============================================================================

class RAGSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 4


class RAGChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    citation_code: str
    category: str
    topic: str
    content: str
    score: float


class RAGIngestResponse(BaseModel):
    documents_ingested: int
    chunks_created: int
    status: str


# ==============================================================================
# 7. Audit & Evaluation
# ==============================================================================

class AuditLogEntry(BaseModel):
    id: int
    username: Optional[str] = None
    action: str
    resource: str
    timestamp: datetime
    status: str
    details: Optional[str] = None


class EvaluationMetrics(BaseModel):
    status: str  # "Not yet executed" or "Completed"
    test_cases_evaluated: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    severity_accuracy: float = 0.0
    category_accuracy: float = 0.0
    citation_accuracy: float = 0.0
    false_positive_rate: float = 0.0
    average_response_time_ms: float = 0.0
    timestamp: Optional[str] = None
