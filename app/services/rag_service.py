"""
CodeSecure AI — Retrieval-Augmented Generation (RAG) Service
Manages knowledge base ingestion, chunking, metadata generation, and vector retrieval.
Supports ChromaDB with SentenceTransformers, with built-in resilient vector search fallback.
"""

import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from app.config import settings
from app.utils.logging_utils import get_logger

logger = get_logger("rag_service")

# Check ChromaDB availability
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.info("ChromaDB library not detected. Resilient vector index enabled.")


class DocumentChunk:
    """Represents a discrete semantic chunk of an educational guideline."""

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        filename: str,
        category: str,
        topic: str,
        citation_code: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.filename = filename
        self.category = category
        self.topic = topic
        self.citation_code = citation_code
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "filename": self.filename,
            "category": self.category,
            "topic": self.topic,
            "citation_code": self.citation_code,
            "content": self.content,
            "metadata": self.metadata,
        }


class ResilientVectorStore:
    """
    Lightweight, deterministic vector index using Term-Frequency Inverse-Document-Frequency
    and Cosine Similarity. Ensures instant, offline RAG retrieval without external downloads.
    """

    def __init__(self, persist_path: Path):
        self.persist_path = persist_path
        self.chunks: List[DocumentChunk] = []
        self.idf: Dict[str, float] = {}
        self.vectors: List[Dict[str, float]] = []
        self._load()

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text)]

    def _compute_vector(self, tokens: List[str]) -> Dict[str, float]:
        tf = Counter(tokens)
        vec = {}
        norm_sq = 0.0
        for token, count in tf.items():
            weight = count * self.idf.get(token, 1.0)
            vec[token] = weight
            norm_sq += weight * weight
        norm = math.sqrt(norm_sq) or 1.0
        return {k: v / norm for k, v in vec.items()}

    def index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        num_docs = len(chunks)
        df: Counter = Counter()
        doc_tokens = [self._tokenize(c.content + " " + c.topic + " " + c.citation_code) for c in chunks]

        for tokens in doc_tokens:
            for term in set(tokens):
                df[term] += 1

        self.idf = {term: math.log((num_docs + 1) / (count + 1)) + 1.0 for term, count in df.items()}
        self.vectors = [self._compute_vector(tokens) for tokens in doc_tokens]
        self._save()

    def search(self, query: str, category: Optional[str] = None, top_k: int = 4) -> List[Tuple[DocumentChunk, float]]:
        if not self.chunks:
            return []

        q_tokens = self._tokenize(query)
        q_vec = self._compute_vector(q_tokens)

        results = []
        for i, doc_vec in enumerate(self.vectors):
            chunk = self.chunks[i]
            if category and category.lower() != "all" and chunk.category.lower() != category.lower():
                continue

            # Cosine similarity (both vectors normalized)
            score = sum(val * q_vec.get(term, 0.0) for term, val in doc_vec.items())
            # Boost matches on citation code or topic
            if chunk.citation_code.lower() in query.lower():
                score += 0.5
            if chunk.topic.lower() in query.lower():
                score += 0.2

            results.append((chunk, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _save(self):
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "chunks": [c.to_dict() for c in self.chunks],
            "idf": self.idf,
        }
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if self.persist_path.exists():
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.chunks = [DocumentChunk(**item) for item in data.get("chunks", [])]
                self.idf = data.get("idf", {})
                doc_tokens = [self._tokenize(c.content + " " + c.topic + " " + c.citation_code) for c in self.chunks]
                self.vectors = [self._compute_vector(tokens) for tokens in doc_tokens]
            except Exception as e:
                logger.warning(f"Could not load vector store cache: {e}")


class RAGService:
    """Main RAG Pipeline service."""

    def __init__(self):
        self.kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
        self.chroma_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
        self.chroma_client = None
        self.collection = None

        # Setup resilient store
        fallback_cache = self.chroma_dir / "resilient_vector_cache.json"
        self.resilient_store = ResilientVectorStore(fallback_cache)

        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))
                self.collection = self.chroma_client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"Connected to persistent ChromaDB at {self.chroma_dir}")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}. Using resilient store.")
                self.chroma_client = None

        # If cache is empty and KB files exist, auto-ingest
        if len(self.resilient_store.chunks) == 0 and self.kb_dir.exists():
            self.ingest_knowledge_base()

    def _parse_citation_and_topic(self, content: str, default_name: str) -> Tuple[str, str, str]:
        """Extracts citation code, topic, and category from document header."""
        citation_code = default_name
        topic = default_name
        category = "General"

        # Check for citation pattern: e.g., KB-MEM-001
        cite_match = re.search(r"Citation Code\*\*:\s*([A-Z0-9_\-]+)", content, re.IGNORECASE)
        if cite_match:
            citation_code = cite_match.group(1).strip()
        else:
            fn_match = re.search(r"(KB-[A-Z0-9\-]+)", default_name)
            if fn_match:
                citation_code = fn_match.group(1)

        cat_match = re.search(r"Category\*\*:\s*([^\n]+)", content, re.IGNORECASE)
        if cat_match:
            category = cat_match.group(1).strip()

        topic_match = re.search(r"Topic\*\*:\s*([^\n]+)", content, re.IGNORECASE)
        if topic_match:
            topic = topic_match.group(1).strip()

        return citation_code, topic, category

    def chunk_document(self, file_path: Path) -> List[DocumentChunk]:
        """Loads and splits a knowledge base markdown document into semantic chunks."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Failed to read KB document {file_path}: {e}")
            return []

        doc_id = file_path.stem
        citation_code, topic, category = self._parse_citation_and_topic(content, doc_id)

        # Split on section headers (## or ###)
        sections = re.split(r"(?=\n##\s+)", content)
        chunks = []

        for idx, sec in enumerate(sections):
            clean_sec = sec.strip()
            if not clean_sec:
                continue

            chunk_id = f"{citation_code}_C{idx+1:02d}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                filename=file_path.name,
                category=category,
                topic=topic,
                citation_code=citation_code,
                content=clean_sec,
                metadata={
                    "source_type": "markdown",
                    "file_path": str(file_path),
                },
            )
            chunks.append(chunk)

        return chunks

    def ingest_knowledge_base(self) -> Dict[str, Any]:
        """Scans data/knowledge_base, creates chunks, and indexes them into vector stores."""
        if not self.kb_dir.exists():
            logger.warning(f"Knowledge base directory does not exist: {self.kb_dir}")
            return {"documents_ingested": 0, "chunks_created": 0, "status": "No KB files found"}

        all_chunks: List[DocumentChunk] = []
        doc_count = 0

        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith((".md", ".txt")):
                    fp = Path(root) / file
                    chunks = self.chunk_document(fp)
                    if chunks:
                        all_chunks.extend(chunks)
                        doc_count += 1

        # Index in resilient store
        self.resilient_store.index(all_chunks)

        # Index in ChromaDB if available
        if self.collection is not None and all_chunks:
            try:
                # Clear existing items
                existing_ids = self.collection.get().get("ids", [])
                if existing_ids:
                    self.collection.delete(ids=existing_ids)

                ids = [c.chunk_id for c in all_chunks]
                documents = [f"{c.topic}\n{c.content}" for c in all_chunks]
                metadatas = [
                    {
                        "document_id": c.document_id,
                        "filename": c.filename,
                        "category": c.category,
                        "topic": c.topic,
                        "citation_code": c.citation_code,
                    }
                    for c in all_chunks
                ]

                # Chroma handles default embeddings automatically
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                )
                logger.info(f"Indexed {len(all_chunks)} chunks in ChromaDB.")
            except Exception as e:
                logger.warning(f"Failed indexing to ChromaDB: {e}. Fallback index is active.")

        logger.info(f"Ingested {doc_count} documents into {len(all_chunks)} chunks.")
        return {
            "documents_ingested": doc_count,
            "chunks_created": len(all_chunks),
            "status": "Success",
        }

    def search(
        self, query: str, category: Optional[str] = None, top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Searches knowledge base chunks using query and optional category filter."""
        # 1. Try ChromaDB if available
        if self.collection is not None:
            try:
                where_filter = None
                if category and category.lower() != "all":
                    where_filter = {"category": category}

                chroma_results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_filter,
                )

                if chroma_results and chroma_results.get("ids") and chroma_results["ids"][0]:
                    output = []
                    ids = chroma_results["ids"][0]
                    docs = chroma_results["documents"][0]
                    metas = chroma_results["metadatas"][0]
                    distances = chroma_results.get("distances", [[0.0] * len(ids)])[0]

                    for cid, doc, meta, dist in zip(ids, docs, metas, distances):
                        # Convert distance to similarity score
                        score = max(0.0, 1.0 - dist)
                        output.append({
                            "chunk_id": cid,
                            "document_id": meta.get("document_id", ""),
                            "citation_code": meta.get("citation_code", ""),
                            "category": meta.get("category", ""),
                            "topic": meta.get("topic", ""),
                            "content": doc,
                            "score": round(score, 3),
                        })
                    return output
            except Exception as e:
                logger.warning(f"ChromaDB query error: {e}. Falling back to resilient store.")

        # 2. Resilient store search
        results = self.resilient_store.search(query, category=category, top_k=top_k)
        output = []
        for chunk, score in results:
            output.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "citation_code": chunk.citation_code,
                "category": chunk.category,
                "topic": chunk.topic,
                "content": chunk.content,
                "score": round(score, 3),
            })
        return output

    def get_formatted_context(self, query: str, category: Optional[str] = None, top_k: int = 4) -> str:
        """Retrieves and formats relevant guidelines into a contextual string for LLM prompting."""
        chunks = self.search(query, category=category, top_k=top_k)
        if not chunks:
            return "No matching guidelines found in local knowledge base."

        lines = []
        for c in chunks:
            lines.append(
                f"--- [CITATION: {c['citation_code']}] ({c['category']} - {c['topic']}) ---\n"
                f"{c['content']}\n"
            )
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on loaded knowledge base chunks."""
        categories = Counter(c.category for c in self.resilient_store.chunks)
        return {
            "total_chunks": len(self.resilient_store.chunks),
            "categories": dict(categories),
            "citations_available": sorted(list(set(c.citation_code for c in self.resilient_store.chunks))),
            "vector_backend": "ChromaDB" if self.collection is not None else "Resilient TF-IDF/Cosine Index",
        }


# Singleton service
rag_service = RAGService()
