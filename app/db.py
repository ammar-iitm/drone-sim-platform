"""Storage: SQLite (one file in data/) by default, or Postgres when DATABASE_URL is set.

SQLite keeps the trainer fully offline on a laptop. Postgres is for hosted deployments
(Vercel with Neon), where the local disk does not persist. Queries are written once, with
SQLite-style "?" placeholders; the Postgres connection translates them. Use:

    db.execute(sql, args)       -> cursor (fetchone, fetchall, iterate); rows read like dicts
    db.executemany(sql, rows)
    db.insert(sql, args)        -> the new row's id
    with db: ...                -> one transaction (commit, or roll back on error)
"""

import os
import sqlite3
from pathlib import Path

from flask import current_app, g
from werkzeug.routing import IntegerConverter

HERE = Path(__file__).parent

# Largest row id (Postgres BIGINT). Ids beyond it are simply not found, rather than errors.
MAX_ID = 2**63 - 1

# Authoritative schema migration version and required tables (Phase 4 OPS-01)
EXPECTED_SCHEMA_VERSION = 4
REQUIRED_TABLES = ("trainees", "sessions", "events", "schema_migrations", "assessment_runs")


class IdConverter(IntegerConverter):
    """URL converter for row ids: <id:session_id>. Out-of-range ids give 404."""

    def __init__(self, url_map):
        super().__init__(url_map, min=1, max=MAX_ID)


def avg1(expr):
    """AVG rounded to one decimal, returned as a float on both databases."""
    return f"CAST(ROUND(CAST(AVG({expr}) AS NUMERIC), 1) AS DOUBLE PRECISION)"


def _run_sqlite_migration_tx(conn, fn):
    """Execute a migration step within an explicit immediate SQLite transaction.

    Ensures that DDL statements (CREATE TABLE, ALTER TABLE, CREATE/DROP INDEX)
    and version recording commit together or roll back completely on failure.
    """
    has_iso = hasattr(conn, "isolation_level")
    orig_iso = getattr(conn, "isolation_level", "")
    if has_iso:
        conn.isolation_level = None
    try:
        conn.execute("BEGIN IMMEDIATE")
        fn()
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        if has_iso:
            conn.isolation_level = orig_iso


def _migrate_sqlite(conn):
    def _create_migrations_table():
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            )
        """)
    _run_sqlite_migration_tx(conn, _create_migrations_table)

    applied = {r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    has_sessions = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='sessions'").fetchone() is not None

    if 1 not in applied:
        def _apply_v1():
            if not has_sessions:
                sql_script = (HERE / "schema.sql").read_text(encoding="utf-8")
                for statement in sql_script.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        conn.execute(stmt)
            conn.execute("INSERT OR IGNORE INTO schema_migrations (version, name) VALUES (1, 'initial_schema')")
        _run_sqlite_migration_tx(conn, _apply_v1)
        applied.add(1)

    if 2 not in applied:
        def _apply_v2():
            cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()]
            if "client_id" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN client_id TEXT")
            if "assessment_nonce" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN assessment_nonce TEXT")
            if "request_hash" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN request_hash TEXT")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")
            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (2, 'session_integrity_and_replay_protection')")
        _run_sqlite_migration_tx(conn, _apply_v2)
        applied.add(2)

    if 3 not in applied:
        def _apply_v3():
            cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()]
            if "client_id" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN client_id TEXT")
            if "assessment_nonce" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN assessment_nonce TEXT")
            if "request_hash" not in cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN request_hash TEXT")

            dup_clients = conn.execute(
                "SELECT client_id, COUNT(*) as cnt FROM sessions WHERE client_id IS NOT NULL "
                "GROUP BY client_id HAVING cnt > 1"
            ).fetchall()
            if dup_clients:
                dup_list = ", ".join(f"{r[0]} (count={r[1]})" for r in dup_clients)
                raise RuntimeError(
                    f"Migration 3 aborted: duplicate client_id found in sessions: {dup_list}. "
                    "Cannot safely enforce unique constraint without administrative remediation."
                )

            dup_nonces = conn.execute(
                "SELECT assessment_nonce, COUNT(*) as cnt FROM sessions WHERE assessment_nonce IS NOT NULL "
                "GROUP BY assessment_nonce HAVING cnt > 1"
            ).fetchall()
            if dup_nonces:
                dup_list = ", ".join(f"{r[0]} (count={r[1]})" for r in dup_nonces)
                raise RuntimeError(
                    f"Migration 3 aborted: duplicate assessment_nonce found in sessions: {dup_list}. "
                    "Cannot safely enforce unique constraint without administrative remediation."
                )

            indexes = {r[1]: r for r in conn.execute("PRAGMA index_list(sessions)").fetchall()}
            if "idx_sessions_client" in indexes:
                if not bool(indexes["idx_sessions_client"][2]):
                    conn.execute("DROP INDEX idx_sessions_client")
                    conn.execute("CREATE UNIQUE INDEX idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")
            else:
                conn.execute("CREATE UNIQUE INDEX idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")

            if "idx_sessions_nonce" in indexes:
                if not bool(indexes["idx_sessions_nonce"][2]):
                    conn.execute("DROP INDEX idx_sessions_nonce")
                    conn.execute("CREATE UNIQUE INDEX idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")
            else:
                conn.execute("CREATE UNIQUE INDEX idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")

            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (3, 'enforce_unique_client_and_nonce_indexes')")
        _run_sqlite_migration_tx(conn, _apply_v3)
        applied.add(3)

    if 4 not in applied:
        def _apply_v4():
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assessment_runs (
                    run_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    seed INTEGER NOT NULL,
                    params_hash TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assessment_runs_status ON assessment_runs (status, started_at)")
            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (4, 'assessment_runs_lifecycle')")
        _run_sqlite_migration_tx(conn, _apply_v4)
        applied.add(4)


def _migrate_postgres(conn):
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(26247)")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            )
        """)
        applied = {r["version"] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()}
        has_sessions = conn.execute("SELECT to_regclass('public.sessions') IS NOT NULL AS ready").fetchone()["ready"]

        if 1 not in applied:
            if not has_sessions:
                conn.execute((HERE / "schema_pg.sql").read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema') ON CONFLICT DO NOTHING")
            applied.add(1)

        if 2 not in applied:
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT")
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS assessment_nonce TEXT")
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS request_hash TEXT")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")
            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (2, 'session_integrity_and_replay_protection')")
            applied.add(2)

        if 3 not in applied:
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT")
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS assessment_nonce TEXT")
            conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS request_hash TEXT")

            dup_clients = conn.execute(
                "SELECT client_id, COUNT(*) AS cnt FROM sessions WHERE client_id IS NOT NULL "
                "GROUP BY client_id HAVING COUNT(*) > 1"
            ).fetchall()
            if dup_clients:
                dup_list = ", ".join(f"{r['client_id']} (count={r['cnt']})" for r in dup_clients)
                raise RuntimeError(
                    f"Migration 3 aborted: duplicate client_id found in PostgreSQL sessions: {dup_list}. "
                    "Cannot safely enforce unique constraint without administrative remediation."
                )

            dup_nonces = conn.execute(
                "SELECT assessment_nonce, COUNT(*) AS cnt FROM sessions WHERE assessment_nonce IS NOT NULL "
                "GROUP BY assessment_nonce HAVING COUNT(*) > 1"
            ).fetchall()
            if dup_nonces:
                dup_list = ", ".join(f"{r['assessment_nonce']} (count={r['cnt']})" for r in dup_nonces)
                raise RuntimeError(
                    f"Migration 3 aborted: duplicate assessment_nonce found in PostgreSQL sessions: {dup_list}. "
                    "Cannot safely enforce unique constraint without administrative remediation."
                )

            pg_indexes = {
                r["index_name"]: r["indisunique"]
                for r in conn.execute("""
                    SELECT i.relname AS index_name, ix.indisunique
                    FROM pg_class t
                    JOIN pg_index ix ON t.oid = ix.indrelid
                    JOIN pg_class i ON i.oid = ix.indexrelid
                    WHERE t.relname = 'sessions'
                """).fetchall()
            }

            if "idx_sessions_client" in pg_indexes:
                if not pg_indexes["idx_sessions_client"]:
                    conn.execute("DROP INDEX IF EXISTS idx_sessions_client")
                    conn.execute("CREATE UNIQUE INDEX idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")
            else:
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL")

            if "idx_sessions_nonce" in pg_indexes:
                if not pg_indexes["idx_sessions_nonce"]:
                    conn.execute("DROP INDEX IF EXISTS idx_sessions_nonce")
                    conn.execute("CREATE UNIQUE INDEX idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")
            else:
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL")

            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (3, 'enforce_unique_client_and_nonce_indexes')")
            applied.add(3)

        if 4 not in applied:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assessment_runs (
                    run_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    seed INTEGER NOT NULL,
                    params_hash TEXT NOT NULL,
                    started_at DOUBLE PRECISION NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assessment_runs_status ON assessment_runs (status, started_at)")
            conn.execute("INSERT INTO schema_migrations (version, name) VALUES (4, 'assessment_runs_lifecycle') ON CONFLICT DO NOTHING")
            applied.add(4)


class SQLiteDB:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")

    def execute(self, sql, args=()):
        return self.conn.execute(sql, args)

    def executemany(self, sql, rows):
        return self.conn.executemany(sql, rows)

    def insert(self, sql, args=()):
        return self.conn.execute(sql, args).lastrowid

    def init_schema(self):
        try:
            _migrate_sqlite(self.conn)
        except Exception as exc:
            raise RuntimeError(f"SQLite schema migration failed: {exc}") from exc

    def __enter__(self):
        self.conn.__enter__()
        return self

    def __exit__(self, *exc):
        return self.conn.__exit__(*exc)

    def close(self):
        self.conn.close()


class PostgresDB:
    def __init__(self, url):
        import psycopg  # only needed for hosted deployments
        from psycopg.rows import dict_row

        # Autocommit outside `with db:` blocks; prepare_threshold=None keeps the connection
        # safe behind a transaction-mode pooler such as Neon's.
        self.conn = psycopg.connect(url, autocommit=True, row_factory=dict_row, prepare_threshold=None)
        self._tx = []

    @staticmethod
    def _sql(sql):
        return sql.replace("%", "%%").replace("?", "%s")

    def execute(self, sql, args=()):
        return self.conn.execute(self._sql(sql), args)

    def executemany(self, sql, rows):
        rows = list(rows)
        if rows:
            with self.conn.cursor() as cur:
                cur.executemany(self._sql(sql), rows)

    def insert(self, sql, args=()):
        return self.conn.execute(self._sql(sql) + " RETURNING id", args).fetchone()["id"]

    def init_schema(self):
        """Create the tables if they are missing. An advisory lock stops two instances
        starting at once from racing on migrations. Fails closed on error."""
        try:
            _migrate_postgres(self.conn)
        except Exception as exc:
            raise RuntimeError(f"PostgreSQL schema migration failed: {exc}") from exc

    def __enter__(self):
        tx = self.conn.transaction()
        tx.__enter__()
        self._tx.append(tx)
        return self

    def __exit__(self, *exc):
        return self._tx.pop().__exit__(*exc)

    def close(self):
        self.conn.close()


def database_url(app):
    """The Postgres URL, read from the environment once by create_app (see app/__init__.py)."""
    return app.config.get("DATABASE_URL")


def connect(app):
    url = database_url(app)
    if url:
        return PostgresDB(url)
    if os.environ.get("VERCEL"):
        raise RuntimeError("On Vercel, set DATABASE_URL to a Postgres database (the disk does not persist)")
    return SQLiteDB(app.config["DATABASE"])


def get_db():
    if "db" not in g:
        g.db = connect(current_app)
        if not current_app.extensions.get("db_schema_ready"):
            # On first use rather than at import, which keeps a database round trip out of
            # every serverless cold start.
            g.db.init_schema()
            current_app.extensions["db_schema_ready"] = True
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def check_database_health(app=None):
    """Perform a read-only database and schema health check.

    Returns:
        tuple[bool, bool]: (database_ok, schema_ok)

    Guarantees:
    - Never mutates the database, runs migrations, or creates missing files.
    - Uses bounded query/connect timeouts (5 seconds).
    - Reliably closes connections on every exit path, including connection and query failures.
    - Strictly read-only: no fallback to writable connections.
    - Never exposes URLs, paths, SQL, or raw exceptions.
    """
    if app is None:
        from flask import current_app
        app = current_app

    url = database_url(app)
    if url:
        # PostgreSQL Health Check
        conn = None
        try:
            import psycopg
            from psycopg.rows import dict_row
            conn = psycopg.connect(url, connect_timeout=5, autocommit=True, row_factory=dict_row)
            # 1. Database reachable check
            conn.execute("SELECT 1")
            db_ok = True
        except Exception:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            return False, False

        try:
            # 2. Schema check: required tables
            rows = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ).fetchall()
            existing_tables = {r["table_name"] for r in rows}
            if not set(REQUIRED_TABLES).issubset(existing_tables):
                return True, False

            # 3. Schema check: migration version
            v_row = conn.execute("SELECT MAX(version) AS max_v FROM schema_migrations").fetchone()
            max_v = v_row["max_v"] if v_row else None
            schema_ok = (max_v == EXPECTED_SCHEMA_VERSION)
            return True, schema_ok
        except Exception:
            return True, False
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    # SQLite Health Check
    if os.environ.get("VERCEL"):
        # On Vercel without DATABASE_URL, database cannot persist
        return False, False

    db_path = app.config.get("DATABASE")
    if not db_path or not os.path.exists(db_path):
        # File missing: do not create it during health check
        return False, False

    conn = None
    try:
        uri = Path(db_path).resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5)
        conn.execute("SELECT 1")
        db_ok = True
    except Exception:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        return False, False

    try:
        # 2. Schema check: required tables
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        existing_tables = {r[0] for r in rows}
        if not set(REQUIRED_TABLES).issubset(existing_tables):
            return True, False

        # 3. Schema check: migration version
        v_row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        max_v = v_row[0] if v_row else None
        schema_ok = (max_v == EXPECTED_SCHEMA_VERSION)
        return True, schema_ok
    except Exception:
        return True, False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def init_db(app=None):
    """Explicitly initialize or migrate the database to EXPECTED_SCHEMA_VERSION.

    Suitable for deployment pre-flight migration steps, init-containers, and operational scripts.
    Never run automatically during readiness health probes.
    """
    if app is None:
        from flask import current_app
        app = current_app

    url = database_url(app)
    if url:
        db = PostgresDB(url)
    else:
        db = SQLiteDB(app.config["DATABASE"])
    try:
        db.init_schema()
    finally:
        db.close()
