"""
Simple database initialization script for E2E testing
Creates all tables without any prompts
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from src.database.models import Base
from src.utils.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with all tables"""
    logger.info("Initializing database...")

    # Create engine
    engine = create_engine(settings.database_url)

    # Create all tables
    Base.metadata.create_all(engine)

    logger.info("[OK] All database tables created successfully!")
    logger.info(f"Database location: {settings.database_url}")

    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    logger.info(f"Created tables: {', '.join(tables)}")


if __name__ == "__main__":
    init_database()
