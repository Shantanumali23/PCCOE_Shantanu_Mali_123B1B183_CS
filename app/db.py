"""
CodeSecure AI — Database Connection & Session Management
Initializes SQLite connection using SQLAlchemy with connection pooling and session lifecycle management.
"""

import os
from contextlib import contextmanager
from typing import Generator
from app.config import settings
from app.utils.logging_utils import get_logger

logger = get_logger("db")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker, Session

    # Ensure SQLite directory exists
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
        echo=False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    SQLALCHEMY_AVAILABLE = True

except ImportError:
    logger.warning("SQLAlchemy not installed in current environment. Using fallback mock base.")
    SQLALCHEMY_AVAILABLE = False
    Base = object
    engine = None
    SessionLocal = None


def get_db():
    """FastAPI dependency for yielding database session with automatic cleanup."""
    if not SQLALCHEMY_AVAILABLE:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for standalone scripts and background tasks."""
    if not SQLALCHEMY_AVAILABLE:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes all database tables declared in models."""
    if SQLALCHEMY_AVAILABLE and engine:
        import app.models  # Ensure models are imported
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully via SQLAlchemy.")
    else:
        logger.warning("SQLAlchemy unavailable; skipping table initialization.")
