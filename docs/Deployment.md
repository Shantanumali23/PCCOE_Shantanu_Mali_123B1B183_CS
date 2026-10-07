# CodeSecure AI — Deployment Guide

## 1. Prerequisites
- **Python**: 3.11 or higher
- **RAM**: Minimum 8 GB (16 GB recommended if running 7B parameter local models)
- **Local LLM**: [Ollama](https://ollama.ai) (optional if using rule-grounded fallback mode)
- **Docker & Docker Compose**: Optional for containerized deployment

---

## 2. Local Bare-Metal Setup

### Step 1: Clone & Create Virtual Environment
```bash
git clone <repository-url>
cd CodeSecure_AI

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env if you wish to adjust default ports or model names
```

### Step 3: Install & Start Ollama (Local AI)
```bash
# 1. Start Ollama daemon in background or separate terminal:
ollama serve

# 2. Pull the recommended coding model:
ollama pull qwen2.5-coder:7b

# (Alternative lightweight model for low-spec laptops):
ollama pull qwen2.5-coder:1.5b
```

### Step 4: Initialize Database & Ingest Knowledge Base
```bash
# Initialize SQLite database
python scripts/init_db.py

# Seed demo users and projects
python scripts/seed_data.py

# Ingest and index synthetic RAG knowledge base
python scripts/ingest_kb.py
```

### Step 5: Start Backend & Frontend
In Terminal 1 (FastAPI Server):
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In Terminal 2 (Streamlit UI):
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

Access the web interface at: `http://localhost:8501`  
API Swagger documentation at: `http://localhost:8000/docs`

---

## 3. Docker Compose Deployment

To build and run all services using Docker:
```bash
docker compose up --build
```
- **Backend API**: `http://localhost:8000`
- **Frontend Dashboard**: `http://localhost:8501`

*Note: In Docker mode, the container communicates with the host machine's Ollama instance via `host.docker.internal:11434`.*
