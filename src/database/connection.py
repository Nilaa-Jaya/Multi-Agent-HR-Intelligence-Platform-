"""
Database connection management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from src.database.models import Base
from src.utils.config import settings
from src.utils.logger import app_logger


# Create engine
if settings.database_url.startswith("sqlite"):
    # SQLite specific configuration (local development)
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug,
    )
    app_logger.info("Using SQLite database (local development)")
else:
    # PostgreSQL configuration (production/Railway)
    # Railway PostgreSQL requires SSL, add connect_args for SSL if in production
    connect_args = {}

    # Enable SSL for production PostgreSQL (Railway)
    if settings.environment == "production" or os.getenv("RAILWAY_ENVIRONMENT"):
        connect_args["sslmode"] = "require"
        app_logger.info("Using PostgreSQL with SSL (production)")
    else:
        app_logger.info("Using PostgreSQL without SSL (development)")

    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Maximum overflow connections
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.debug,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.error(f"Error initializing database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    Used as dependency in FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Get database session as context manager
    For use outside FastAPI
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def close_db():
    """Close database connection"""
    engine.dispose()
    app_logger.info("Database connection closed")
