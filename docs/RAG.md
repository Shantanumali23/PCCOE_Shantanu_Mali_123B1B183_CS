# CodeSecure AI — Retrieval-Augmented Generation (RAG) Architecture

## 1. Overview
The **RAG (Retrieval-Augmented Generation)** subsystem anchors AI review recommendations in an authoritative, locally hosted educational knowledge base. This eliminates hallucinations, provides concrete citations, and delivers actionable remediations grounded in embedded software engineering guidelines.

---

## 2. Ingestion & Chunking Pipeline

```text
Synthetic Knowledge Documents (data/knowledge_base/*.md)
                          ↓
               Markdown Section Parser
                          ↓
               Metadata Extraction Header
                          ↓
               Semantic Chunks (200-400 tokens)
                          ↓
     ┌────────────────────┴────────────────────┐
     ▼                                         ▼
Persistent ChromaDB               Resilient Vector Store
(Cosine Distance)                 (TF-IDF + Cosine Cache)
```

### Chunking Strategy
- Knowledge base markdown documents are split along semantic headers (`##` and `###`).
- Each chunk preserves header context and code examples.

### Chunk Metadata Schema
```json
{
  "chunk_id": "KB-MEM-001_C01",
  "document_id": "KB-MEM-001_memory_safety",
  "filename": "KB-MEM-001_memory_safety.md",
  "category": "Coding Guidelines",
  "topic": "Memory Safety",
  "citation_code": "KB-MEM-001",
  "source_type": "markdown"
}
```

---

## 3. Vector Database & Fallback Architecture
1. **Primary Vector Store — ChromaDB**:
   - Stores dense embeddings in `./chroma_db` using cosine distance space (`hnsw:space: cosine`).
   - Generates embeddings locally using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
2. **Resilient Vector Index (Built-in Fallback)**:
   - To guarantee 100% operational reliability in offline evaluation environments without external model downloads, a built-in TF-IDF / Cosine Similarity index runs natively in standard Python.
   - Preserves citation retrieval and top-K search even without ChromaDB C-extensions.

---

## 4. Citation Generation & Validation
Every AI finding produced by CodeSecure AI must provide an audit trail linking back to a retrieved guideline chunk:
```json
{
  "issue": "Potential null pointer dereference",
  "rule": "KB-MEM-001",
  "citations": ["KB-MEM-001"]
}
```
If the LLM omits a citation code, the normalization layer maps the finding to the top-scoring retrieved chunk from the current RAG context.
