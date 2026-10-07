# CodeSecure AI — Privacy-Preserving Secure Code Debugging and Review using Local LLM and RAG

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg)](https://ollama.ai)

> **Academic Capstone Project**  
> **Institution**: Tata Technologies Tech Pulse FY-26 AI/ML Capstone Project  
> **Case Study**: **CS4 — Secure Code Debugging and Review**  
> **Domain**: Cybersecurity, DevSecOps, Embedded Systems, Applied GenAI / RAG

---

## 1. Problem Statement
Safety-critical and embedded software development (e.g. automotive ECUs, avionics, industrial controllers) enforces rigorous defensive coding and MISRA-oriented guidelines. Modern cloud-based AI code assistants present critical risks:
- **Intellectual Property Exfiltration**: Proprietary C/C++ source code transmitted over external networks to public LLM APIs.
- **Unverified Hallucinations**: Plausible-sounding recommendations that violate safety standards or introduce memory corruption.
- **Prompt Injection Vulnerabilities**: Malicious instructions concealed inside repository files, comments, or diagnostic logs.
- **Lack of Auditability**: Absence of human-in-the-loop disposition tracking and tamper-evident compliance logs.

**CodeSecure AI** solves this dilemma by deploying a **host-isolated, privacy-preserving review platform** powered by local LLMs (Ollama) and local Retrieval-Augmented Generation (RAG) anchored in synthetic educational guidelines.

---

## 2. Core Features
- **Local/Private LLM Execution**: Runs entirely on `localhost` using Ollama (`qwen2.5-coder:7b`). Source code never leaves the host.
- **RAG-Grounded Guidance**: Links findings directly to verified educational guidelines with transparent citation codes (`KB-MEM-001`, `KB-SEC-001`, etc.).
- **MISRA-Oriented Educational Guidance**: Identifies potential deviations in type safety, defensive flow, and pointer arithmetic without false claims of official certification.
- **Structured Findings Schema**: Emits machine-readable findings containing Observed Evidence, Root Cause Hypotheses, and Defensive Recommendations.
- **Prompt Injection Defense**: Defense-in-depth sanitization, regex threat classification, and `<UNTRUSTED_CODE_DATA>` boundaries.
- **Compiler & Runtime Log Diagnosis**: Diagnoses GCC/Clang warnings, Cppcheck static findings, AddressSanitizer, and Valgrind memory leaks.
- **Human-in-the-Loop Disposition**: Granular state management (`Open`, `Confirmed`, `Rejected`, `Fixed`, `Needs Review`) with reviewer commentary.
- **Role-Based Access Control (RBAC)**: Developer, Reviewer, Security Engineer, and Administrator roles with PBKDF2 password hashing.
- **Tamper-Evident Audit Logging**: Comprehensive tracking of all security events without leaking source code or credentials.
- **Empirical Evaluation Pipeline**: Automated benchmarking calculating Precision, Recall, F1-Score, and Latency against ground-truth test cases.

---

## 3. Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                     │
│  Dashboard | Code Review | Log Analysis | Disposition  │
│  RAG Knowledge Base | Evaluation | Security Audit Logs │
└───────────────────────────┬────────────────────────────┘
                            │ REST API / Local Service
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Gateway                      │
│  - JWT Bearer Authentication                           │
│  - Role-Based Access Control (RBAC)                    │
│  - Input Size & Extension Guardrails                   │
│  - Path Traversal & Injection Defenses                 │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
                ▼                        ▼
     ┌──────────────────────┐ ┌──────────────────────┐
     │  SQLite / SQLAlchemy │ │   RAG Vector Store   │
     │  - Users & Roles     │ │  - ChromaDB / TF-IDF │
     │  - Projects & Repos  │ │  - 62 Semantic Chunks│
     │  - Findings & Audits │ │  - 13 Guideline Rules│
     └──────────────────────┘ └──────────┬───────────┘
                                         │ RAG Context
                                         ▼
                             ┌───────────────────────┐
                             │   Local LLM Engine    │
                             │  Ollama / Qwen-Coder  │
                             │ (Host Isolated: 11434)│
                             └───────────────────────┘
```

---

## 4. Technology Stack
- **Backend API**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite
- **Frontend UI**: Streamlit
- **Local LLM**: Ollama (`qwen2.5-coder:7b` / `qwen2.5-coder:1.5b`)
- **Vector Database**: ChromaDB (with built-in Resilient Cosine Similarity Vector Index)
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Testing**: pytest / unittest
- **Containerization**: Docker, Docker Compose

---

## 5. Project Structure

```text
Tata/
├── app/
│   ├── main.py                     # FastAPI application & route registration
│   ├── config.py                   # Central configuration & environment loader
│   ├── db.py                       # SQLAlchemy database engine & session pool
│   ├── models.py                   # ORM models (Users, Projects, Findings, Audits)
│   ├── schemas.py                  # Pydantic schemas for structured JSON output
│   ├── api/                        # REST API endpoint routers
│   ├── services/                   # Business logic (LLM, RAG, Review, Evaluation)
│   ├── security/                   # Crypto, RBAC, Prompt Injection, Path Security
│   └── utils/                      # Sanitizing logger, JSON extractor, file utilities
├── frontend/
│   ├── streamlit_app.py            # Streamlit multi-page UI application
│   └── pages/                      # Modular navigation pages
├── data/
│   ├── code_samples/               # 21 synthetic C/C++ test cases (vulnerable & safe)
│   ├── compiler_logs/              # GCC & Clang diagnostic logs
│   ├── static_analysis/            # Cppcheck reports
│   ├── runtime_logs/               # Valgrind & AddressSanitizer crash traces
│   ├── knowledge_base/             # Synthetic educational RAG guidelines
│   └── ground_truth/               # Ground truth dataset JSON
├── prompts/                        # System & task prompts with untrusted boundaries
├── config/                         # YAML configs (model, embeddings, vector store)
├── scripts/                        # Management scripts (init_db, seed, ingest, eval)
├── tests/                          # Automated unit and integration test suite
├── evaluation/                     # Evaluation dataset, runner, and persisted metrics
├── docs/                           # Architecture, Security, RAG, Threat Model, Demo Guide
├── Dockerfile                      # Production container image definition
├── docker-compose.yml              # Multi-container service orchestration
├── requirements.txt                # Production Python dependencies
└── README.md                       # Comprehensive project documentation
```

---

## 6. Installation & Local Setup

### Step 1: Clone and Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
cp .env.example .env
```

### Step 3: Setup Local Ollama LLM
1. Install Ollama from [ollama.ai](https://ollama.ai).
2. Start the daemon:
   ```bash
   ollama serve
   ```
3. Pull the recommended local coding model:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
   *(For lower-spec hardware, use `ollama pull qwen2.5-coder:1.5b`)*

### Step 4: Database Initialization & Knowledge Base Ingestion
```bash
# 1. Initialize SQLite database schema
python scripts/init_db.py

# 2. Seed default users, projects, and repositories
python scripts/seed_data.py

# 3. Ingest knowledge base into local vector store
python scripts/ingest_kb.py
```

### Step 5: Start Backend and Frontend
In Terminal 1 (FastAPI Backend):
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In Terminal 2 (Streamlit UI):
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

- Web Interface: `http://localhost:8501`
- Swagger API Docs: `http://localhost:8000/docs`

---

## 7. Running Tests & Evaluation

### Run Test Suite
```bash
# Comprehensive test runner (works with pytest or standard unittest)
python scripts/run_tests.py
```

### Run Evaluation Pipeline
```bash
python scripts/run_evaluation.py
```

---

## 8. Docker Deployment
```bash
docker compose up --build
```
- Access Frontend: `http://localhost:8501`
- Access Backend API: `http://localhost:8000`

---

## 9. Preset Academic Demo Accounts
| Username | Password | Role | Permissions |
|---|---|---|---|
| `developer` | `Dev@CodeSecure2026` | Developer | Submit reviews, view own findings |
| `reviewer` | `Reviewer@CodeSecure2026` | Reviewer | Update finding status & comments |
| `security_eng` | `SecEng@CodeSecure2026` | Security Engineer | Inspect audit logs, security reviews |
| `admin` | `Admin@CodeSecure2026` | Administrator | Full administrative control |

---

## 10. Responsible AI & Disclaimers
1. **AI-Assisted Human Oversight**: CodeSecure AI is an AI-assisted static analysis tool designed to augment software engineers. It is **NOT** an autonomous code approval system.
2. **Not Certified MISRA Compliance**: Educational guidance provided by this system does not replace certified tools or constitute formal certification.
3. **Host Isolation**: All source code remains strictly local by default.

---

## 11. License
Licensed under the [MIT License](LICENSE).
