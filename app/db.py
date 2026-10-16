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


class IdConverter(IntegerConverter):
    """URL converter for row ids: <id:session_id>. Out-of-range ids give 404."""

    def __init__(self, url_map):
        super().__init__(url_map, min=1, max=MAX_ID)


def avg1(expr):
    """AVG rounded to one decimal, returned as a float on both databases."""
    return f"CAST(ROUND(CAST(AVG({expr}) AS NUMERIC), 1) AS DOUBLE PRECISION)"


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
        with self.conn:
            self.conn.executescript((HERE / "schema.sql").read_text())

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
        """Create the tables if they are missing. One cheap check when they exist; when they
        don't, an advisory lock stops two instances starting at once from racing on CREATE."""
        if self.conn.execute("SELECT to_regclass('public.events') IS NOT NULL AS ready").fetchone()["ready"]:
            return
        with self.conn.transaction():
            self.conn.execute("SELECT pg_advisory_xact_lock(26247)")
            self.conn.execute((HERE / "schema_pg.sql").read_text())

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
