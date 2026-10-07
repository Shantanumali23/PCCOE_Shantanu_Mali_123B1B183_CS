"""
CodeSecure AI — Data Seeding Script
Populates the database with initial academic demonstration users, projects, and repositories.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import get_db_context, init_db, SQLALCHEMY_AVAILABLE
from app.models import Project, Repository, User
from app.security.authentication import hash_password
from app.utils.logging_utils import get_logger

logger = get_logger("seed_data_script")

DEMO_USERS = [
    ("admin", "Admin@CodeSecure2026", "admin"),
    ("reviewer", "Reviewer@CodeSecure2026", "reviewer"),
    ("developer", "Dev@CodeSecure2026", "developer"),
    ("security_eng", "SecEng@CodeSecure2026", "security_engineer"),
]


def seed():
    logger.info("Initializing database...")
    init_db()

    if not SQLALCHEMY_AVAILABLE:
        logger.info("SQLAlchemy not available; in-memory users active.")
        return

    with get_db_context() as db:
        if not db:
            return

        # 1. Seed Users
        created_users = {}
        for username, password, role in DEMO_USERS:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                u = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(u)
                db.flush()
                created_users[username] = u
                logger.info(f"Seeded user: {username} (Role: {role})")
            else:
                created_users[username] = existing
                logger.info(f"User already exists: {username}")

        # 2. Seed Project
        admin_user = created_users.get("admin")
        if admin_user:
            proj = db.query(Project).filter(Project.name == "Automotive ECU Telemetry").first()
            if not proj:
                proj = Project(
                    name="Automotive ECU Telemetry",
                    description="Embedded sensor ingestion and CAN bus communications module",
                    owner_id=admin_user.id,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(proj)
                db.flush()
                logger.info("Seeded project: Automotive ECU Telemetry")

            # 3. Seed Repository
            repo = db.query(Repository).filter(Repository.name == "ecu-telemetry-core").first()
            if not repo and proj:
                repo = Repository(
                    project_id=proj.id,
                    name="ecu-telemetry-core",
                    path="./repositories/ecu-telemetry-core",
                    authorized_roles="developer,reviewer,security_engineer,admin",
                )
                db.add(repo)
                logger.info("Seeded repository: ecu-telemetry-core")

        db.commit()
        logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    seed()
