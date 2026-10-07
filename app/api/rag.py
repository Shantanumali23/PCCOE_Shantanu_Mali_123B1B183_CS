"""
CodeSecure AI — RAG Knowledge Base API Endpoints
Provides search, ingestion, and telemetry for local vector knowledge base.
"""

from typing import Any, Dict, List, Optional
from app.utils.fastapi_compat import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas import RAGChunkResponse, RAGIngestResponse, RAGSearchRequest
from app.security.authorization import has_permission, Permission
from app.services.rag_service import rag_service
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("rag_api")
router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


@router.get("/search", response_model=List[RAGChunkResponse])
def search_knowledge_base(
    query: str = Query(..., min_length=2),
    category: Optional[str] = None,
    top_k: int = Query(4, ge=1, le=20),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieves top-K semantic chunks from the local knowledge base."""
    results = rag_service.search(query=query, category=category, top_k=top_k)
    return results


@router.post("/ingest", response_model=RAGIngestResponse)
def trigger_ingestion(user: Dict[str, Any] = Depends(get_current_user)):
    """Triggers knowledge base re-indexing into local vector database."""
    if not has_permission(user["role"], Permission.RAG_INGEST):
        raise HTTPException(status_code=403, detail="Unauthorized to trigger knowledge base ingestion.")

    result = rag_service.ingest_knowledge_base()
    security_service.log_event(
        action="KNOWLEDGE_BASE_INGESTED",
        resource="knowledge_base",
        user_id=user["id"],
        username=user["username"],
        details=f"Documents={result['documents_ingested']}, Chunks={result['chunks_created']}",
    )
    return RAGIngestResponse(**result)


@router.get("/stats")
def get_knowledge_base_stats(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns vector database status and chunk distribution."""
    return rag_service.get_stats()
