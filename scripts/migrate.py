#!/usr/bin/env python3
"""AEGIS Database Migration CLI (Phase 4 OPS-01).

Applies all pending database migrations up to EXPECTED_SCHEMA_VERSION.
Enables pre-deployment migration steps in container entrypoints, CI/CD, and orchestrators
before the application serves traffic or responds to readiness probes.

Usage:
    python scripts/migrate.py [--check]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.db import EXPECTED_SCHEMA_VERSION, check_database_health, init_db


def run_migrations(check_only=False, app=None):
    """Execute or verify database migrations.

    Returns:
        int: 0 on success, 1 on failure.
    """
    if app is None:
        app = create_app()

    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        if check_only:
            if db_ok and schema_ok:
                print(f"Database schema is up to date (version {EXPECTED_SCHEMA_VERSION}).")
                return 0
            else:
                print(f"Database schema is not up to date (expected version {EXPECTED_SCHEMA_VERSION}).")
                return 1

        print("Applying pending database migrations...")
        init_db(app)
        db_ok, schema_ok = check_database_health(app)
        if db_ok and schema_ok:
            print(f"Migrations applied successfully. Database is at schema version {EXPECTED_SCHEMA_VERSION}.")
            return 0
        else:
            print("ERROR: Migrations executed but database schema is still not ready.")
            return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="AEGIS Database Migration CLI")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check migration status without applying changes (exit 0 if up to date, 1 if pending)",
    )
    args = parser.parse_args(argv)
    return run_migrations(check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
