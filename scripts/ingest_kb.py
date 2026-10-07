"""
CodeSecure AI — Knowledge Base Ingestion Script
Parses and indexes synthetic guidelines into ChromaDB / resilient vector store.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import rag_service
from app.utils.logging_utils import get_logger

logger = get_logger("ingest_kb_script")

if __name__ == "__main__":
    logger.info("Starting Knowledge Base Ingestion...")
    result = rag_service.ingest_knowledge_base()
    logger.info(f"Ingestion result: {result}")
    stats = rag_service.get_stats()
    logger.info(f"Total chunks in vector store: {stats['total_chunks']}")
    logger.info(f"Available citations: {stats['citations_available']}")
