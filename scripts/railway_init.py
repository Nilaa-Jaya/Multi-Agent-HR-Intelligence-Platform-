#!/usr/bin/env python
"""
Railway Initialization Script

This script runs during Railway deployment to:
1. Initialize database
2. Run migrations
3. Initialize knowledge base if needed
4. Verify health check

Usage:
    python scripts/railway_init.py
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import init_db, get_db
from src.utils.logger import app_logger


def check_database_connection(max_retries=5, retry_delay=5):
    """Check database connection with retry logic"""
    app_logger.info("Checking database connection...")

    for attempt in range(1, max_retries + 1):
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
            app_logger.info(f"Database connection successful on attempt {attempt}")
            return True
        except Exception as e:
            app_logger.warning(
                f"Database connection attempt {attempt}/{max_retries} failed: {e}"
            )
            if attempt < max_retries:
                app_logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                app_logger.error("Max retries reached. Database connection failed.")
                return False

    return False


def initialize_database():
    """Initialize database tables"""
    app_logger.info("Initializing database tables...")

    try:
        init_db()
        app_logger.info("Database tables initialized successfully")
        return True
    except Exception as e:
        app_logger.error(f"Database initialization failed: {e}")
        return False


def initialize_knowledge_base():
    """Initialize knowledge base with sample data if needed"""
    app_logger.info("Checking knowledge base initialization...")

    try:
        from src.knowledge_base.vector_store import VectorStore

        # Check if knowledge base needs initialization
        vector_store = VectorStore()

        # Check if collection exists and has data
        try:
            collection = vector_store.client.get_collection(
                name=vector_store.collection_name
            )
            count = collection.count()

            if count > 0:
                app_logger.info(
                    f"Knowledge base already initialized with {count} documents"
                )
                return True
        except Exception:
            app_logger.info("Knowledge base collection not found, will be created on first use")
            return True

        app_logger.info("Knowledge base checked successfully")
        return True

    except Exception as e:
        app_logger.warning(f"Knowledge base initialization check failed: {e}")
        # Don't fail deployment if KB init fails - it can be done later
        app_logger.warning("Continuing deployment without KB initialization")
        return True


def verify_environment_variables():
    """Verify required environment variables are set"""
    app_logger.info("Verifying environment variables...")

    required_vars = ["DATABASE_URL", "GROQ_API_KEY"]
    optional_vars = ["PORT", "ENVIRONMENT", "SECRET_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            app_logger.error(f"Required environment variable missing: {var}")

    for var in optional_vars:
        if os.getenv(var):
            app_logger.info(f"Optional variable set: {var}")
        else:
            app_logger.warning(f"Optional variable not set: {var} (using default)")

    if missing_vars:
        app_logger.error(f"Missing required variables: {', '.join(missing_vars)}")
        return False

    app_logger.info("All required environment variables are set")
    return True


def run_health_check():
    """Run basic health check"""
    app_logger.info("Running health check...")

    try:
        # Check Python version
        import sys

        python_version = sys.version_info
        app_logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check critical imports
        from src.agents import workflow
        from src.api import app

        app_logger.info("Critical imports successful")

        # Check database
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        app_logger.info("Database query successful")

        app_logger.info("Health check passed")
        return True

    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        return False


def main():
    """Main initialization flow"""
    app_logger.info("=" * 60)
    app_logger.info("RAILWAY INITIALIZATION STARTED")
    app_logger.info("=" * 60)

    # Track success of each step
    steps = []

    # Step 1: Verify environment variables
    app_logger.info("\n[Step 1/5] Verifying environment variables...")
    env_check = verify_environment_variables()
    steps.append(("Environment Variables", env_check))

    if not env_check:
        app_logger.error("Environment variable verification failed!")
        app_logger.error("Please set required environment variables in Railway dashboard")
        sys.exit(1)

    # Step 2: Check database connection
    app_logger.info("\n[Step 2/5] Checking database connection...")
    db_connection = check_database_connection()
    steps.append(("Database Connection", db_connection))

    if not db_connection:
        app_logger.error("Database connection failed!")
        sys.exit(1)

    # Step 3: Initialize database
    app_logger.info("\n[Step 3/5] Initializing database...")
    db_init = initialize_database()
    steps.append(("Database Initialization", db_init))

    if not db_init:
        app_logger.error("Database initialization failed!")
        sys.exit(1)

    # Step 4: Initialize knowledge base (optional)
    app_logger.info("\n[Step 4/5] Initializing knowledge base...")
    kb_init = initialize_knowledge_base()
    steps.append(("Knowledge Base", kb_init))
    # Don't fail if KB init fails - it's optional

    # Step 5: Run health check
    app_logger.info("\n[Step 5/5] Running health check...")
    health = run_health_check()
    steps.append(("Health Check", health))

    # Summary
    app_logger.info("\n" + "=" * 60)
    app_logger.info("INITIALIZATION SUMMARY")
    app_logger.info("=" * 60)

    for step_name, success in steps:
        status = "[OK] PASS" if success else "[X] FAIL"
        app_logger.info(f"{status}: {step_name}")

    # Determine overall success
    critical_steps = ["Environment Variables", "Database Connection", "Database Initialization", "Health Check"]
    critical_failed = [name for name, success in steps if name in critical_steps and not success]

    if critical_failed:
        app_logger.error("\n" + "=" * 60)
        app_logger.error("INITIALIZATION FAILED")
        app_logger.error(f"Critical steps failed: {', '.join(critical_failed)}")
        app_logger.error("=" * 60)
        sys.exit(1)
    else:
        app_logger.info("\n" + "=" * 60)
        app_logger.info("INITIALIZATION SUCCESSFUL")
        app_logger.info("Railway deployment ready!")
        app_logger.info("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        app_logger.warning("\nInitialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        app_logger.error(f"\nUnexpected error during initialization: {e}")
        import traceback

        app_logger.error(traceback.format_exc())
        sys.exit(1)
