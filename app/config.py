"""
CodeSecure AI — Application Configuration Module
Centralized settings management supporting .env overrides and YAML configurations.
"""

import os
from pathlib import Path
from typing import List, Optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent


def load_yaml(file_path: Path) -> dict:
    """Safely loads a YAML configuration file."""
    if file_path.exists() and YAML_AVAILABLE:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


class Settings:
    """Central configuration class for CodeSecure AI."""

    def __init__(self):
        # 1. Environment & Server
        self.APP_NAME: str = os.getenv("APP_NAME", "CodeSecure AI")
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.PORT: int = int(os.getenv("PORT", 8000))
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))

        # 2. Security & Auth
        self.SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "codesecure-academic-demo-jwt-secret-key-change-in-production"
        )
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480)
        )

        # 3. Database
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", f"sqlite:///{BASE_DIR / 'codesecure.db'}"
        )

        # 4. LLM & Ollama Configuration
        model_cfg = load_yaml(BASE_DIR / "config" / "model_config.yaml")
        self.OLLAMA_BASE_URL: str = os.getenv(
            "OLLAMA_BASE_URL", model_cfg.get("base_url", "http://localhost:11434")
        )
        self.OLLAMA_MODEL: str = os.getenv(
            "OLLAMA_MODEL", model_cfg.get("model", "qwen2.5-coder:7b")
        )
        self.LLM_PROVIDER: str = os.getenv(
            "LLM_PROVIDER", model_cfg.get("provider", "ollama")
        )
        self.LLM_TEMPERATURE: float = float(
            os.getenv("LLM_TEMPERATURE", model_cfg.get("temperature", 0.1))
        )
        self.LLM_REQUEST_TIMEOUT: int = int(
            os.getenv("LLM_REQUEST_TIMEOUT", model_cfg.get("timeout_seconds", 60))
        )
        self.ALLOW_OFFLINE_FALLBACK: bool = model_cfg.get(
            "allow_offline_fallback", True
        )

        # 5. Embedding & Vector Database
        embed_cfg = load_yaml(BASE_DIR / "config" / "embedding_config.yaml")
        vstore_cfg = load_yaml(BASE_DIR / "config" / "vector_store_config.yaml")

        self.CHROMA_PERSIST_DIRECTORY: str = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            vstore_cfg.get("persist_directory", str(BASE_DIR / "chroma_db")),
        )
        self.EMBEDDING_MODEL: str = os.getenv(
            "EMBEDDING_MODEL",
            embed_cfg.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"),
        )
        self.RAG_TOP_K: int = int(
            os.getenv("RAG_TOP_K", vstore_cfg.get("default_top_k", 4))
        )
        self.CHROMA_COLLECTION_NAME: str = vstore_cfg.get(
            "collection_name", "codesecure_kb"
        )

        # 6. File & Input Validation
        self.MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 2))
        allowed_exts = os.getenv(
            "ALLOWED_FILE_EXTENSIONS", ".c,.cpp,.h,.hpp,.cc,.cxx,.log,.txt"
        )
        self.ALLOWED_FILE_EXTENSIONS: List[str] = [
            ext.strip() for ext in allowed_exts.split(",") if ext.strip()
        ]
        self.ALLOWED_REPOSITORIES_DIR: str = os.getenv(
            "ALLOWED_REPOSITORIES_DIR", str(BASE_DIR / "repositories")
        )
        self.KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "data" / "knowledge_base"


# Singleton instance
settings = Settings()
