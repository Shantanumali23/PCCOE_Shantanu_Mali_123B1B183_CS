# ==============================================================================
# CodeSecure AI — Multi-Service Dockerfile
# Supports running both FastAPI backend and Streamlit frontend.
# ==============================================================================

FROM python:3.11-slim

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=8000 \
    STREAMLIT_PORT=8501

WORKDIR /app

# Install system utilities and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source repository
COPY . /app

# Initialize database schema and index knowledge base during build
RUN python scripts/init_db.py && \
    python scripts/seed_data.py && \
    python scripts/ingest_kb.py

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# Default command launches FastAPI backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
