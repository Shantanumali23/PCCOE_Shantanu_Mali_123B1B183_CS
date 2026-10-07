"""
CodeSecure AI — Database Initialization Script
Initializes SQLite database tables and foreign keys.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import init_db
from app.utils.logging_utils import get_logger

logger = get_logger("init_db_script")

if __name__ == "__main__":
    logger.info("Initializing CodeSecure AI database...")
    init_db()
    logger.info("Database schema initialized successfully.")
