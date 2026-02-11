"""
Migration script: Transform Multi-Agent HR Intelligence Platform to Multi-Agent HR Intelligence Platform

This script migrates the database schema from customer support categories
to HR categories while preserving existing conversation data.

Run this script ONCE after updating models.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Employee, JobApplication
from src.utils.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_database(engine):
    """Create a backup of the database before migration"""
    logger.info("Creating database backup...")

    db_url = str(engine.url)
    if "sqlite" in db_url:
        import shutil
        from datetime import datetime

        db_file = db_url.split("///")[-1]
        backup_file = f"{db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if os.path.exists(db_file):
            shutil.copy2(db_file, backup_file)
            logger.info(f"[OK] Backup created: {backup_file}")
            return backup_file
    else:
        logger.warning("[WARNING] Automatic backup only supported for SQLite. Please backup manually.")
        return None


def migrate_category_data(engine):
    """Migrate old customer support categories to HR categories"""
    logger.info("Migrating category data...")

    category_mapping = {
        "Technical": "General",
        "Billing": "Payroll",
        "Account": "General",
        "General": "General"
    }

    with engine.connect() as conn:
        # Check if conversations table exists
        inspector = inspect(engine)
        if "conversations" not in inspector.get_table_names():
            logger.info("No conversations table found - fresh database")
            return

        # Update conversation categories
        for old_cat, new_cat in category_mapping.items():
            result = conn.execute(
                text("UPDATE conversations SET category = :new_cat WHERE category = :old_cat"),
                {"new_cat": new_cat, "old_cat": old_cat}
            )
            conn.commit()
            if result.rowcount > 0:
                logger.info(f"  Migrated {result.rowcount} conversations: {old_cat} → {new_cat}")

        # Update analytics if exists
        if "analytics" in inspector.get_table_names():
            # Map old columns to new columns in analytics table
            # This is a simplification - in production you'd want more sophisticated logic
            logger.info("  Updating analytics aggregations...")
            conn.execute(
                text("""
                    UPDATE analytics
                    SET recruitment_queries = COALESCE(technical_queries, 0),
                        payroll_queries = COALESCE(billing_queries, 0),
                        benefits_queries = 0,
                        policy_queries = 0,
                        leave_management_queries = 0,
                        performance_queries = 0
                    WHERE technical_queries IS NOT NULL OR billing_queries IS NOT NULL
                """)
            )
            conn.commit()
            logger.info("  [OK] Analytics updated")


def add_hr_columns(engine):
    """Add HR-specific columns to existing tables"""
    logger.info("Adding HR columns to users table...")

    with engine.connect() as conn:
        inspector = inspect(engine)

        # Check if users table exists
        if "users" not in inspector.get_table_names():
            logger.info("No users table found - will be created fresh")
            return

        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('users')]

        # Add HR columns if they don't exist
        hr_columns = {
            'employee_id': 'VARCHAR(50)',
            'department': 'VARCHAR(100)',
            'position': 'VARCHAR(100)',
            'hire_date': 'DATETIME'
        }

        for column_name, column_type in hr_columns.items():
            if column_name not in existing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    logger.info(f"  [OK] Added column: {column_name}")
                except Exception as e:
                    logger.warning(f"  [WARNING] Could not add {column_name}: {e}")


def create_new_tables(engine):
    """Create new HR-specific tables"""
    logger.info("Creating new HR tables...")

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Create only the new tables
    tables_to_create = []

    if "employees" not in existing_tables:
        tables_to_create.append("employees")
    if "job_applications" not in existing_tables:
        tables_to_create.append("job_applications")

    if tables_to_create:
        # Create only new tables by using metadata filtering
        metadata = Base.metadata
        tables = [metadata.tables[name] for name in tables_to_create if name in metadata.tables]

        for table in tables:
            table.create(engine, checkfirst=True)
            logger.info(f"  [OK] Created table: {table.name}")
    else:
        logger.info("  All HR tables already exist")


def verify_migration(engine):
    """Verify the migration was successful"""
    logger.info("\nVerifying migration...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = ['users', 'employees', 'job_applications', 'conversations', 'analytics']
    missing_tables = [t for t in required_tables if t not in tables]

    if missing_tables:
        logger.error(f"[FAIL] Missing tables: {missing_tables}")
        return False

    logger.info("[OK] All required tables exist")

    # Verify users table has HR columns
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    hr_columns = ['employee_id', 'department', 'position', 'hire_date']
    missing_columns = [c for c in hr_columns if c not in user_columns]

    if missing_columns:
        logger.warning(f"[WARNING] Missing HR columns in users: {missing_columns}")
    else:
        logger.info("[OK] Users table has all HR columns")

    return True


def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("Multi-Agent HR Intelligence Platform - Database Migration")
    logger.info("=" * 60)

    # Get database connection
    engine = create_engine(settings.database_url)

    try:
        # Step 1: Backup
        backup_file = backup_database(engine)

        # Step 2: Add new columns to existing tables
        add_hr_columns(engine)

        # Step 3: Create new HR tables
        create_new_tables(engine)

        # Step 4: Migrate existing category data
        migrate_category_data(engine)

        # Step 5: Verify migration
        success = verify_migration(engine)

        if success:
            logger.info("\n" + "=" * 60)
            logger.info("[OK] Migration completed successfully!")
            logger.info("=" * 60)
            if backup_file:
                logger.info(f"\nBackup saved at: {backup_file}")
            logger.info("\nNext steps:")
            logger.info("1. Update knowledge base FAQs (Phase 2)")
            logger.info("2. Regenerate vector store")
            logger.info("3. Test the system with HR queries")
        else:
            logger.error("\n[FAIL] Migration completed with warnings. Please review above.")

    except Exception as e:
        logger.error(f"\n[FAIL] Migration failed: {e}")
        logger.error("Please restore from backup and check the error.")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    # Safety check
    print("\n[WARNING]  WARNING: This will modify your database schema!")
    print("Make sure you have a backup before proceeding.\n")

    response = input("Do you want to continue? (yes/no): ").strip().lower()

    if response == "yes":
        main()
    else:
        print("Migration cancelled.")
