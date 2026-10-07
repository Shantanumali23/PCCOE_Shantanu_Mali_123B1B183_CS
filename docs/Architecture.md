# CodeSecure AI — System Architecture

## 1. Executive Summary
**CodeSecure AI** is a privacy-preserving AI-assisted static code review and debugging platform built for **Tata Technologies Tech Pulse FY-26 Capstone Project (CS4 — Secure Code Debugging and Review)**. It integrates local Large Language Models (LLMs via Ollama) with Retrieval-Augmented Generation (RAG) and layered cybersecurity controls to evaluate C/C++ source code, compiler diagnostics, and runtime traces without transmitting proprietary code to third-party cloud AI vendors.

---

## 2. Architectural Blueprint

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                              │
│                    Streamlit Multi-Page UI                             │
│  - Dashboard  - Code Review  - Log Analysis  - Disposition  - RAG/Eval │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST or Direct Service
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Application Gateway                             │
│                           FastAPI REST API                             │
│  - Route Guards  - Bearer Token Verification  - Rate & Size Limiting   │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│          Security Perimeter          │  │       Data Governance        │
│  - Input Validation (Extensions/Size)│  │ SQLite Database (SQLAlchemy) │
│  - Path Traversal Defense            │  │  - Users & Roles (RBAC)      │
│  - Prompt Injection Classifier       │  │  - Projects & Repositories   │
│  - Untrusted Data Containerization   │  │  - Review Sessions & Findings│
│  - Tamper-Evident Audit Logger       │  │  - Citations & Status Logs   │
└───────────────────┬──────────────────┘  └──────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Semantic Retrieval Engine                        │
│                         RAG Knowledge Base                             │
│  - Markdown Chunking & Metadata (Topic, Category, Citation ID)         │
│  - Vector Store: ChromaDB / Resilient Vector Index                     │
│  - Top-K Similarity Search with Cosine Scoring                         │
└───────────────────┬────────────────────────────────────────────────────┘
                    │ Augmented Prompt (System Directives + RAG Guidelines)
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Local Inference Engine                           │
│                      Ollama (Qwen2.5-Coder)                            │
│  - Host-Isolated Execution                                             │
│  - Structured JSON Output Generation                                   │
│  - Resilient Fallback Engine for Offline CI/CD and Demo Stability      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Pipelines

### 3.1 Code Review Pipeline
1. **Submission**: User supplies C/C++ source code via UI or API.
2. **Input Validation**: Sanitizes filename, validates `.c`/`.cpp`/`.h` extension, ensures size < 2 MB, rejects binary content.
3. **Prompt Injection Defense**: Evaluates code and comments for instruction-hijacking patterns. Encloses code inside `<UNTRUSTED_CODE_DATA>` boundaries.
4. **RAG Context Retrieval**: Queries ChromaDB / vector store using code snippets and review type. Extracts top-K relevant guidelines.
5. **Prompt Assembly**: Formulates strict system instructions with epistemic separation (Evidence vs. Interpretation vs. Root Cause vs. Recommendation).
6. **Local LLM Execution**: Invokes Ollama model at `http://localhost:11434`.
7. **JSON Normalization**: Extracts and validates findings against Pydantic schema (`StructuredFindingItem`).
8. **Persistence & Audit**: Stores review session, findings, and citations in SQLite; logs audit event.

### 3.2 Log Analysis Pipeline
1. **Input Ingestion**: Ingests compiler diagnostic logs (GCC/Clang), static analysis outputs (Cppcheck), or runtime traces (AddressSanitizer/Valgrind).
2. **Defect Extraction**: Identifies file, line, error code, and diagnostic message.
3. **Guideline Association**: Correlates error signatures with RAG educational rules (e.g., `-Wnull-dereference` -> `KB-MEM-001`).
4. **Structured Output**: Emits structured issue report with recommended remediation steps.

---

## 4. Key Subsystems
- **`app.security`**: Enforces zero-trust input handling, password cryptography (PBKDF2-HMAC-SHA256), and path isolation.
- **`app.services.rag_service`**: Manages chunking, metadata indexing, and similarity retrieval.
- **`app.services.llm_service`**: Interfaces with local Ollama instance with resilient offline reviewer fallback.
- **`app.services.evaluation_service`**: Executes empirical testing against ground truth test cases.
