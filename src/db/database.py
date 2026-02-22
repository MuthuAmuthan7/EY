"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rfp_platform.db"
)

# Create engine with appropriate pool settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # For PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator:
    """Get database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)
