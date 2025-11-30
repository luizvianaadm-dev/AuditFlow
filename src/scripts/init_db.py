from alembic.config import Config
from alembic import command
from src.scripts.seed_accounts import seed_standard_accounts
from src.scripts.seed_work_programs import seed_audit_programs
import os
import sys

def init_db():
    print("----- Starting DB Initialization -----")

    # Ensure we are in root (where alembic.ini is)
    # If this script is called from root via 'python -m src.scripts.init_db', cwd is usually root.

    # 1. Migrations
    print("Running Alembic Migrations...")
    try:
        # Assuming alembic.ini is in the root directory
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error applying migrations: {e}")
        # Proceeding with caution, or return?
        # If migration fails, seeding might fail too.
        # But let's try.

    # 2. Seeds
    print("Seeding Standard Accounts...")
    try:
        seed_standard_accounts()
    except Exception as e:
        print(f"Error seeding accounts: {e}")

    print("Seeding Work Programs...")
    try:
        seed_audit_programs()
    except Exception as e:
        print(f"Error seeding work programs: {e}")

    print("----- DB Initialization Complete -----")

if __name__ == "__main__":
    init_db()
