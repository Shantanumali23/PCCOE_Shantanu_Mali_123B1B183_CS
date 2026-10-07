"""
CodeSecure AI — Database Models (SQLAlchemy ORM)
Declares schema for Users, Projects, Repositories, Review Sessions, Findings, Citations, and Audit Logs.
"""

from datetime import datetime, timezone
from app.db import Base, SQLALCHEMY_AVAILABLE

if SQLALCHEMY_AVAILABLE:
    from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
    from sqlalchemy.orm import relationship

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        username = Column(String(64), unique=True, index=True, nullable=False)
        password_hash = Column(String(256), nullable=False)
        role = Column(String(32), default="developer", nullable=False)  # developer, reviewer, security_engineer, admin
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

        # Relationships
        projects = relationship("Project", back_populates="owner")
        reviews = relationship("ReviewSession", back_populates="user")
        audit_logs = relationship("AuditLog", back_populates="user")

    class Project(Base):
        __tablename__ = "projects"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        name = Column(String(128), nullable=False)
        description = Column(Text, nullable=True)
        owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

        # Relationships
        owner = relationship("User", back_populates="projects")
        repositories = relationship("Repository", back_populates="project", cascade="all, delete-orphan")

    class Repository(Base):
        __tablename__ = "repositories"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
        name = Column(String(128), nullable=False)
        path = Column(String(512), nullable=False)
        authorized_roles = Column(String(256), default="developer,reviewer,security_engineer,admin")

        # Relationships
        project = relationship("Project", back_populates="repositories")
        reviews = relationship("ReviewSession", back_populates="repository")

    class ReviewSession(Base):
        __tablename__ = "review_sessions"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
        review_type = Column(String(64), nullable=False)  # Security Review, MISRA-Oriented Review, Code Explanation, etc.
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        status = Column(String(32), default="Completed")  # Completed, Failed, In Progress

        # Relationships
        user = relationship("User", back_populates="reviews")
        repository = relationship("Repository", back_populates="reviews")
        findings = relationship("Finding", back_populates="review_session", cascade="all, delete-orphan")

    class Finding(Base):
        __tablename__ = "findings"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        review_session_id = Column(Integer, ForeignKey("review_sessions.id"), nullable=False)
        finding_code = Column(String(32), index=True, nullable=False)  # e.g., F001, CS-MEM-01
        severity = Column(String(32), nullable=False)  # Critical, High, Medium, Low, Informational
        category = Column(String(64), nullable=False)  # Memory Safety, Buffer Safety, etc.
        file = Column(String(256), nullable=False)
        function = Column(String(128), nullable=True)
        line = Column(Integer, nullable=True)
        issue = Column(Text, nullable=False)
        evidence = Column(Text, nullable=True)
        root_cause = Column(Text, nullable=True)
        recommendation = Column(Text, nullable=False)
        rule = Column(String(64), nullable=True)  # Associated guideline code
        confidence = Column(Float, default=0.85)
        status = Column(String(32), default="Open")  # Open, Confirmed, Rejected, Fixed, Needs Review
        reviewer_comment = Column(Text, nullable=True)
        updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

        # Relationships
        review_session = relationship("ReviewSession", back_populates="findings")
        citations = relationship("Citation", back_populates="finding", cascade="all, delete-orphan")

    class Citation(Base):
        __tablename__ = "citations"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
        document_id = Column(String(128), nullable=False)
        chunk_id = Column(String(64), nullable=False)
        citation_code = Column(String(64), nullable=False)  # e.g., KB-MEM-001

        # Relationships
        finding = relationship("Finding", back_populates="citations")

    class AuditLog(Base):
        __tablename__ = "audit_logs"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
        username = Column(String(64), nullable=True)
        action = Column(String(64), nullable=False)  # LOGIN, CODE_REVIEW, DISPOSITION_UPDATE, PROMPT_INJECTION_DETECTED
        resource = Column(String(256), nullable=False)
        timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        status = Column(String(32), default="SUCCESS")
        details = Column(Text, nullable=True)

        # Relationships
        user = relationship("User", back_populates="audit_logs")

else:
    # Dummy mock classes if SQLAlchemy is not installed
    class User: pass
    class Project: pass
    class Repository: pass
    class ReviewSession: pass
    class Finding: pass
    class Citation: pass
    class AuditLog: pass
