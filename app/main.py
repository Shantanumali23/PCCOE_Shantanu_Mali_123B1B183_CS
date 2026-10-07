"""
CodeSecure AI — Primary FastAPI Application Server
Provides secure REST API endpoints for AI code review, RAG retrieval, log analysis,
findings disposition, evaluation metrics, and audit logging.
"""

from contextlib import asynccontextmanager
from app.utils.fastapi_compat import (
    FastAPI,
    Request,
    CORSMiddleware,
    JSONResponse,
)
from app.config import settings
from app.db import init_db
from app.api.auth import router as auth_router
from app.api.review import router as review_router
from app.api.logs import router as logs_router
from app.api.findings import router as findings_router
from app.api.rag import router as rag_router
from app.api.evaluation import router as evaluation_router
from app.api.audit import router as audit_router
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.utils.logging_utils import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing CodeSecure AI Application...")
    # Initialize DB tables
    init_db()
    # Check Ollama and RAG health
    ollama_status = llm_service.check_health()
    logger.info(f"Ollama Status: {ollama_status['reachable']} (Model: {ollama_status['configured_model']})")
    rag_stats = rag_service.get_stats()
    logger.info(f"RAG Knowledge Base: {rag_stats['total_chunks']} chunks loaded via {rag_stats['vector_backend']}.")
    yield
    logger.info("Shutting down CodeSecure AI...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Privacy-Preserving Secure Code Debugging and Review using Local LLM and RAG. "
        "Academic capstone project for Tata Technologies Tech Pulse FY-26 (CS4)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (configured for local development and Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(review_router)
app.include_router(logs_router)
app.include_router(findings_router)
app.include_router(rag_router)
app.include_router(evaluation_router)
app.include_router(audit_router)


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint providing status of application, database, and local LLM."""
    ollama_info = llm_service.check_health()
    rag_info = rag_service.get_stats()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_service": ollama_info,
        "rag_service": {
            "total_chunks": rag_info["total_chunks"],
            "backend": rag_info["vector_backend"],
        },
        "disclaimer": "AI-assisted analysis — human review required. Does not replace certified MISRA tools.",
    }


@app.get("/", tags=["System"])
def root():
    """Root metadata endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Privacy-Preserving Secure Code Debugging and Review using Local LLM and RAG",
        "documentation": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler preventing stack trace leakage to clients."""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
