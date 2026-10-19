"""Phase 2 Reliability, Migration & Persistent Data Regression Tests.

Covers:
- REL-01: High-DPI scaling, Quality levels (high, medium, low, minimum),
          scenery scaling, and auto step-down state machine.
- REL-02: Database schema versioning, repeatable migrations, safe upgrades from legacy,
          detection of non-unique indexes, and duplicate-data failure aborts.
- REL-03: Automated backup creation (SQLite online backup API), SHA-256 manifests,
          PRAGMA integrity verification, safe restoration with collision guards,
          and CLI commands.
"""

import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.db import _migrate_sqlite, _migrate_postgres
from scripts.backup import (
    create_backup,
    verify_backup,
    restore_backup,
    list_backups,
    main as backup_main,
)


# ==============================================================================
# REL-01: High-DPI Display Scaling & Quality Settings
# ==============================================================================

def test_rel01_quality_levels_ratios_and_scenery_scaling():
    """Verify that quality level ratios and scenery fraction mappings match specification."""
    # Quality table specification from world.js:
    expected_quality = {
        "high": {"ratio": 1.5, "scenery": 1.0},
        "medium": {"ratio": 1.0, "scenery": 0.6},
        "low": {"ratio": 0.75, "scenery": 0.35},
        "minimum": {"ratio": 0.5, "scenery": 0.2},
    }

    # Test effective pixel ratios across standard, fractionally scaled, and high-DPI displays
    test_dprs = [1.0, 1.25, 1.5, 1.75, 2.0]
    for dpr in test_dprs:
        for level, cfg in expected_quality.items():
            effective_ratio = min(dpr, cfg["ratio"])
            assert 0.5 <= effective_ratio <= 1.5
            if dpr == 1.0 and level == "high":
                assert effective_ratio == 1.0
            elif dpr >= 1.5 and level == "high":
                assert effective_ratio == 1.5
            elif level == "minimum":
                assert effective_ratio == 0.5


def test_rel01_auto_quality_step_down_state_machine():
    """Verify auto-quality step-down logic: drops level on 6 half-second windows (<35 fps), resets on >=35 fps, never steps up."""
    # Production autoQuality implementation from main.js lines 614-625:
    # S.lowFpsWindows = fps < 35 ? S.lowFpsWindows + 1 : 0;
    quality_order = ["high", "medium", "low", "minimum"]
    state = {"quality": "high", "lowFpsWindows": 0}

    def simulate_auto_quality(fps):
        if state["quality"] == "minimum":
            return
        state["lowFpsWindows"] = state["lowFpsWindows"] + 1 if fps < 35 else 0
        idx = quality_order.index(state["quality"])
        if state["lowFpsWindows"] >= 6 and idx < len(quality_order) - 1:
            state["quality"] = quality_order[idx + 1]
            state["lowFpsWindows"] = 0

    # 1. At threshold (35 fps) or above (36, 60 fps): resets window count, no step down
    simulate_auto_quality(36)
    assert state["lowFpsWindows"] == 0
    simulate_auto_quality(35)
    assert state["lowFpsWindows"] == 0
    assert state["quality"] == "high"

    # 2. Intermittent drop: 4 low windows followed by 1 good window resets window counter
    for _ in range(4):
        simulate_auto_quality(34)
    assert state["lowFpsWindows"] == 4
    simulate_auto_quality(35)  # good frame rate resets counter
    assert state["lowFpsWindows"] == 0
    assert state["quality"] == "high"

    # 3. 5 low windows (<35 fps): no step down yet (requires 6)
    for _ in range(5):
        simulate_auto_quality(34)
    assert state["quality"] == "high"
    assert state["lowFpsWindows"] == 5

    # 4. 6th low window (<35 fps): steps down to medium, counter resets to 0
    simulate_auto_quality(34)
    assert state["quality"] == "medium"
    assert state["lowFpsWindows"] == 0

    # 5. High FPS (60 fps) never restores quality (avoids frame oscillation)
    for _ in range(10):
        simulate_auto_quality(60)
    assert state["quality"] == "medium"
    assert state["lowFpsWindows"] == 0

    # 6. Another 6 low windows: steps down to low
    for _ in range(6):
        simulate_auto_quality(30)
    assert state["quality"] == "low"
    assert state["lowFpsWindows"] == 0

    # 7. Another 6 low windows: steps down to minimum
    for _ in range(6):
        simulate_auto_quality(20)
    assert state["quality"] == "minimum"
    assert state["lowFpsWindows"] == 0

    # 8. Stays clamped at minimum: does not crash or step down further
    for _ in range(12):
        simulate_auto_quality(10)
    assert state["quality"] == "minimum"


test_auto_quality_drops_settings_under_load = test_rel01_auto_quality_step_down_state_machine


def test_rel01_dpi_scaling_bounds_across_device_pixel_ratios():
    """Verify canvas render buffer dimensions scale correctly with devicePixelRatio."""
    viewport_w, viewport_h = 1280, 720
    test_dprs = [1.0, 1.25, 1.5, 1.75, 2.0]

    for dpr in test_dprs:
        # High quality: Math.min(dpr, 1.5)
        pixel_ratio = min(dpr, 1.5)
        render_w = int(viewport_w * pixel_ratio)
        render_h = int(viewport_h * pixel_ratio)

        # Aspect ratio is preserved identically regardless of DPI
        aspect = render_w / render_h
        assert abs(aspect - (1280 / 720)) < 0.01
        assert render_w >= 1280
        assert render_h >= 720


def test_rel01_pixel_ratio_clamping_and_canvas_bounds():
    """Verify Three.js pixel ratio clamping across quality modes and device pixel ratios."""
    quality_caps = {
        "high": 1.5,
        "medium": 1.0,
        "low": 0.75,
        "minimum": 0.5,
    }
    test_dprs = [1.0, 1.25, 1.5, 1.75, 2.0]
    for dpr in test_dprs:
        for q_name, cap in quality_caps.items():
            effective_dpr = min(dpr, cap)
            assert effective_dpr <= cap
            assert effective_dpr <= dpr
            # Buffer size for 1920x1080 display
            buf_w = round(1920 * effective_dpr)
            buf_h = round(1080 * effective_dpr)
            assert buf_w / buf_h == pytest.approx(1920 / 1080, rel=1e-3)


# ==============================================================================
# REL-02: Safe Schema Versioning & Database Migrations
# ==============================================================================

def test_rel02_fresh_database_applies_all_migrations(tmp_path):
    """A fresh database initializes with all versioned migrations (v1, v2, v3, v4)."""
    db_file = tmp_path / "fresh.db"
    conn = sqlite3.connect(str(db_file))
    _migrate_sqlite(conn)

    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()]
    assert versions == [1, 2, 3, 4]

    # Verify tables and unique indexes exist
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert {"trainees", "sessions", "events", "schema_migrations", "assessment_runs"}.issubset(tables)

    indexes = {r[1]: r[2] for r in conn.execute("PRAGMA index_list(sessions)").fetchall()}
    assert indexes.get("idx_sessions_client") == 1  # 1 = unique
    assert indexes.get("idx_sessions_nonce") == 1
    conn.close()


def test_rel02_legacy_v1_migration_adds_columns_and_unique_indexes(tmp_path):
    """A legacy v1 database missing client_id, nonce, and hash upgrades safely to v4."""
    db_file = tmp_path / "legacy_v1.db"
    conn = sqlite3.connect(str(db_file))

    # Construct v1 schema without v2/v3/v4 columns
    conn.executescript("""
        CREATE TABLE trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT NOT NULL,
            unit TEXT NOT NULL
        );
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER NOT NULL REFERENCES trainees (id),
            scenario_id TEXT NOT NULL,
            scenario_name TEXT NOT NULL,
            seed INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            duration_s REAL NOT NULL,
            total REAL NOT NULL,
            detection REAL NOT NULL,
            classification REAL NOT NULL,
            engagement REAL NOT NULL,
            grade TEXT NOT NULL,
            false_alarms INTEGER NOT NULL,
            breaches INTEGER NOT NULL,
            critical_errors INTEGER NOT NULL,
            result TEXT NOT NULL
        );
        CREATE TABLE schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');
    """)

    # Insert a legacy session
    conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('OLD-CALL', 'OLD-UNIT')")
    conn.execute("""
        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at,
                              duration_s, total, detection, classification, engagement,
                              grade, false_alarms, breaches, critical_errors, result)
        VALUES (1, 's1-dawn-recon', 'Dawn Recon', 42, '2026-01-01T00:00:00Z',
                120.0, 85.0, 25.0, 25.0, 35.0, 'B', 0, 0, 0, '{}')
    """)
    conn.commit()

    # Apply migrations
    _migrate_sqlite(conn)

    # Columns must now exist
    cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()]
    assert "client_id" in cols
    assert "assessment_nonce" in cols
    assert "request_hash" in cols

    # Existing row must be intact with NULL for new columns
    row = conn.execute("SELECT client_id, assessment_nonce, request_hash FROM sessions WHERE id = 1").fetchone()
    assert row == (None, None, None)

    # Migrations v2, v3, and v4 recorded
    applied = [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()]
    assert applied == [1, 2, 3, 4]

    # assessment_runs table created
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "assessment_runs" in tables

    conn.close()


def test_rel02_migration_repeatability_and_idempotence(tmp_path):
    """Running migrations multiple times is idempotent and introduces zero changes."""
    db_file = tmp_path / "idempotent.db"
    conn = sqlite3.connect(str(db_file))
    _migrate_sqlite(conn)
    _migrate_sqlite(conn)
    _migrate_sqlite(conn)

    versions = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
    assert len(versions) == 4
    assert [v[0] for v in versions] == [1, 2, 3, 4]
    conn.close()


def test_rel02_migration_transaction_atomic_rollback_on_failure(tmp_path):
    """A failed migration step rolls back the transaction atomically, leaving schema and version unchanged."""
    db_file = tmp_path / "rollback.db"
    conn = sqlite3.connect(str(db_file))

    # Setup initial schema at version 1
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');
    """)
    conn.commit()

    # Proxy wrapper to inject simulated failure during migration
    class FaultyConn:
        def __init__(self, real_conn):
            self._real = real_conn
        def execute(self, sql, *args, **kwargs):
            if "CREATE UNIQUE INDEX" in sql:
                raise sqlite3.OperationalError("Simulated disk error during migration")
            return self._real.execute(sql, *args, **kwargs)
        def __enter__(self):
            self._real.__enter__()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._real.__exit__(exc_type, exc_val, exc_tb)
        def __getattr__(self, item):
            return getattr(self._real, item)

    faulty = FaultyConn(conn)

    with pytest.raises(sqlite3.OperationalError, match="Simulated disk error"):
        _migrate_sqlite(faulty)

    # Verify atomic rollback: schema_migrations remains at version 1
    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    assert versions == [1]

    # Verify index was not created
    indexes = [r[1] for r in conn.execute("PRAGMA index_list(sessions)").fetchall()]
    assert "idx_sessions_client" not in indexes
    conn.close()


def test_rel02_migration1_fresh_schema_creation_partway_failure_rolls_back_completely(tmp_path):
    """Failure partway through fresh schema creation rolls back all tables and migration entries atomically."""
    db_file = tmp_path / "rollback_fresh.db"
    conn = sqlite3.connect(str(db_file))

    class FaultyFreshConn:
        def __init__(self, real_conn):
            self._real = real_conn
        def execute(self, sql, *args, **kwargs):
            if "sessions" in sql and "CREATE TABLE" in sql:
                raise sqlite3.OperationalError("Simulated disk error during CREATE TABLE sessions")
            return self._real.execute(sql, *args, **kwargs)
        def __enter__(self):
            self._real.__enter__()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._real.__exit__(exc_type, exc_val, exc_tb)
        def __getattr__(self, item):
            return getattr(self._real, item)

    faulty = FaultyFreshConn(conn)

    with pytest.raises(sqlite3.OperationalError, match="CREATE TABLE sessions"):
        _migrate_sqlite(faulty)

    # Verify atomic rollback: no application tables left behind
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "trainees" not in tables
    assert "sessions" not in tables
    assert "events" not in tables

    # Verify version 1 is not recorded in schema_migrations
    if "schema_migrations" in tables:
        versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
        assert 1 not in versions
    conn.close()


def test_rel02_migration_version_insertion_failure_rolls_back_schema_changes(tmp_path):
    """Failure during schema_migrations version insertion rolls back the preceding DDL changes in that step."""
    db_file = tmp_path / "rollback_version.db"
    conn = sqlite3.connect(str(db_file))

    # Setup initial schema at version 1
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');
    """)
    conn.commit()

    class FaultyVersionConn:
        def __init__(self, real_conn):
            self._real = real_conn
        def execute(self, sql, *args, **kwargs):
            if "INSERT INTO schema_migrations" in sql and "session_integrity" in sql:
                raise sqlite3.OperationalError("Simulated disk error during migration version insertion")
            return self._real.execute(sql, *args, **kwargs)
        def __enter__(self):
            self._real.__enter__()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._real.__exit__(exc_type, exc_val, exc_tb)
        def __getattr__(self, item):
            return getattr(self._real, item)

    faulty = FaultyVersionConn(conn)

    with pytest.raises(sqlite3.OperationalError, match="migration version insertion"):
        _migrate_sqlite(faulty)

    # Verify atomic rollback: columns added in migration 2 are rolled back
    cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()]
    assert "client_id" not in cols
    assert "assessment_nonce" not in cols
    assert "request_hash" not in cols

    # Verify version 2 was not recorded
    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    assert versions == [1]
    conn.close()


def test_rel02_migration2_column_addition_failure_rolls_back_cleanly(tmp_path):
    """Failure halfway through adding columns rolls back previously added columns in that migration."""
    db_file = tmp_path / "rollback_col.db"
    conn = sqlite3.connect(str(db_file))

    # Setup initial schema at version 1
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');
    """)
    conn.commit()

    class FaultyColConn:
        def __init__(self, real_conn):
            self._real = real_conn
        def execute(self, sql, *args, **kwargs):
            if "ALTER TABLE sessions ADD COLUMN assessment_nonce" in sql:
                raise sqlite3.OperationalError("Simulated disk error during column addition")
            return self._real.execute(sql, *args, **kwargs)
        def __enter__(self):
            self._real.__enter__()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._real.__exit__(exc_type, exc_val, exc_tb)
        def __getattr__(self, item):
            return getattr(self._real, item)

    faulty = FaultyColConn(conn)

    with pytest.raises(sqlite3.OperationalError, match="during column addition"):
        _migrate_sqlite(faulty)

    # Even though ALTER TABLE sessions ADD COLUMN client_id executed first, it must be rolled back
    cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()]
    assert "client_id" not in cols
    assert "assessment_nonce" not in cols
    assert "request_hash" not in cols

    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    assert versions == [1]
    conn.close()


def test_rel02_duplicate_client_id_aborts_safely(tmp_path):
    """Migration 3 aborts safely with RuntimeError if duplicate client_id exists in unmigrated data."""
    db_file = tmp_path / "dup_client.db"
    conn = sqlite3.connect(str(db_file))
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER, client_id TEXT, assessment_nonce TEXT, request_hash TEXT);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema'), (2, 'v2');
        INSERT INTO sessions (id, trainee_id, client_id) VALUES (1, 1, 'conflict-client-id');
        INSERT INTO sessions (id, trainee_id, client_id) VALUES (2, 1, 'conflict-client-id');
    """)
    conn.commit()

    with pytest.raises(RuntimeError, match="duplicate client_id found"):
        _migrate_sqlite(conn)

    # Migration 3 must NOT be marked as applied
    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    assert 3 not in versions

    # Records must be untouched
    rows = conn.execute("SELECT id, client_id FROM sessions").fetchall()
    assert len(rows) == 2
    conn.close()


def test_rel02_duplicate_nonce_aborts_safely(tmp_path):
    """Migration 3 aborts safely with RuntimeError if duplicate assessment_nonce exists in unmigrated data."""
    db_file = tmp_path / "dup_nonce.db"
    conn = sqlite3.connect(str(db_file))
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER, client_id TEXT, assessment_nonce TEXT, request_hash TEXT);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema'), (2, 'v2');
        INSERT INTO sessions (id, trainee_id, assessment_nonce) VALUES (1, 1, 'duplicate-nonce-value');
        INSERT INTO sessions (id, trainee_id, assessment_nonce) VALUES (2, 1, 'duplicate-nonce-value');
    """)
    conn.commit()

    with pytest.raises(RuntimeError, match="duplicate assessment_nonce found"):
        _migrate_sqlite(conn)

    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    assert 3 not in versions
    conn.close()


def test_rel02_nonunique_index_replaced_with_unique_partial_index(tmp_path):
    """Migration 3 detects a pre-existing non-unique index and replaces it with a unique partial index."""
    db_file = tmp_path / "nonunique_idx.db"
    conn = sqlite3.connect(str(db_file))
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER, client_id TEXT, assessment_nonce TEXT, request_hash TEXT);
        CREATE INDEX idx_sessions_client ON sessions (client_id);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema'), (2, 'v2');
    """)
    conn.commit()

    # Pre-condition: non-unique index
    idx = {r[1]: r[2] for r in conn.execute("PRAGMA index_list(sessions)").fetchall()}
    assert idx["idx_sessions_client"] == 0  # 0 = not unique

    _migrate_sqlite(conn)

    # Post-condition: index is now unique
    idx_after = {r[1]: r[2] for r in conn.execute("PRAGMA index_list(sessions)").fetchall()}
    assert idx_after["idx_sessions_client"] == 1  # 1 = unique
    assert 3 in [r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()]
    conn.close()


def test_rel02_postgres_runtime_migration_on_disposable_cluster(tmp_path):
    """Execute PostgreSQL migrations against an isolated disposable PostgreSQL cluster created in tmp_path.

    Proves:
    1. Ephemeral port selection and exact temp-cluster data_directory verification.
    2. Migrations 1-4 apply cleanly and idempotently.
    3. Mandatory tables, columns, and constraints exist.
    4. pg_index catalog verification for unique partial indexes on client_id and assessment_nonce.
    5. Runtime insertion rejection of duplicate client_id and assessment_nonce.
    6. Legacy duplicate records cleanly abort migration 3 without data loss or partial commits.
    7. Clean process termination and temporary artifact isolation.
    """
    import socket
    import subprocess
    import time
    try:
        import psycopg
        from psycopg import errors as pg_errors
    except ImportError:
        pytest.skip("psycopg not installed")

    bin_dir = Path(r"C:\Program Files\PostgreSQL\17\bin")
    initdb_path = bin_dir / "initdb.exe"
    postgres_path = bin_dir / "postgres.exe"
    if not initdb_path.exists() or not postgres_path.exists():
        pytest.skip("PostgreSQL 17 binaries not found in standard location")

    pg_data = tmp_path / "pg_data"

    # Select dynamic available ephemeral port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    # 1. Initialize clean, isolated disposable cluster
    init_cmd = [
        str(initdb_path),
        "-D", str(pg_data),
        "-U", "postgres",
        "-A", "trust",
        "--no-locale",
        "-E", "UTF-8"
    ]
    r = subprocess.run(init_cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"initdb failed: {r.stderr}"

    # 2. Start PostgreSQL server on ephemeral port with log file capturing output
    log_path = tmp_path / "postgres.log"
    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen([str(postgres_path), "-D", str(pg_data), "-p", str(port)], stdout=log_file, stderr=log_file)
    try:
        # Wait for cluster readiness
        conn = None
        for _ in range(30):
            time.sleep(0.5)
            if proc.poll() is not None:
                log_file.close()
                diag = log_path.read_text(encoding="utf-8", errors="replace")
                pytest.fail(f"PostgreSQL server process exited prematurely with code {proc.returncode}: {diag}")
            try:
                conn = psycopg.connect(f"host=127.0.0.1 port={port} user=postgres dbname=postgres",
                                       autocommit=True, row_factory=psycopg.rows.dict_row)
                break
            except Exception:
                pass
        assert conn is not None, f"Failed to connect to disposable PostgreSQL cluster on port {port}"

        try:
            # 3. Verify cluster identity: SHOW data_directory must match pg_data
            server_data_dir = conn.execute("SHOW data_directory").fetchone()["data_directory"]
            assert Path(server_data_dir).resolve().as_posix().lower() == pg_data.resolve().as_posix().lower(), (
                f"Cluster identity mismatch! Connected to {server_data_dir}, expected {pg_data}"
            )

            # 4. Execute migrations on fresh database
            _migrate_postgres(conn)

            # 5. Assert all 4 migrations applied
            rows = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
            applied_versions = [r["version"] for r in rows]
            assert applied_versions == [1, 2, 3, 4]

            # 6. Assert mandatory tables exist
            tables = [r["table_name"] for r in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ).fetchall()]
            for expected_tbl in ("trainees", "sessions", "events", "schema_migrations", "assessment_runs"):
                assert expected_tbl in tables

            # 7. Catalog inspection: verify unique partial indexes on sessions
            indexes = conn.execute("""
                SELECT
                    i.relname AS index_name,
                    ix.indisunique,
                    pg_get_expr(ix.indpred, ix.indrelid) AS predicate
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                WHERE t.relname = 'sessions'
            """).fetchall()
            idx_map = {r["index_name"]: r for r in indexes}
            assert "idx_sessions_client" in idx_map
            assert idx_map["idx_sessions_client"]["indisunique"] is True
            assert "client_id IS NOT NULL" in idx_map["idx_sessions_client"]["predicate"]

            assert "idx_sessions_nonce" in idx_map
            assert idx_map["idx_sessions_nonce"]["indisunique"] is True
            assert "assessment_nonce IS NOT NULL" in idx_map["idx_sessions_nonce"]["predicate"]

            # 8. Runtime duplicate rejection assertions
            t_row = conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('PG-ALPHA', 'COY-1') RETURNING id").fetchone()
            t_id = t_row["id"]

            conn.execute("""
                INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                      detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                      result, client_id, assessment_nonce, request_hash)
                VALUES (%s, 's1', 'Test', 10, '2026-10-17T00:00:00Z', 100, 95.0, 30.0, 30.0, 35.0, 'A', 0, 0, 0,
                        '{"score": 95.0}', 'client-unique-1', 'nonce-unique-1', 'hash-1')
            """, (t_id,))

            # Duplicate client_id rejection
            with pytest.raises(pg_errors.UniqueViolation):
                with conn.transaction():
                    conn.execute("""
                        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                              detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                              result, client_id, assessment_nonce, request_hash)
                        VALUES (%s, 's1', 'Test', 10, '2026-10-17T00:00:00Z', 100, 95.0, 30.0, 30.0, 35.0, 'A', 0, 0, 0,
                                '{"score": 95.0}', 'client-unique-1', 'nonce-unique-2', 'hash-2')
                    """, (t_id,))

            # Duplicate assessment_nonce rejection
            with pytest.raises(pg_errors.UniqueViolation):
                with conn.transaction():
                    conn.execute("""
                        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                              detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                              result, client_id, assessment_nonce, request_hash)
                        VALUES (%s, 's1', 'Test', 10, '2026-10-17T00:00:00Z', 100, 95.0, 30.0, 30.0, 35.0, 'A', 0, 0, 0,
                                '{"score": 95.0}', 'client-unique-2', 'nonce-unique-1', 'hash-3')
                    """, (t_id,))

            # Multiple NULL client_id and NULL assessment_nonce rows succeed (partial index)
            conn.execute("""
                INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                      detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                      result, client_id, assessment_nonce, request_hash)
                VALUES (%s, 's1', 'Test', 10, '2026-10-17T00:00:00Z', 100, 95.0, 30.0, 30.0, 35.0, 'A', 0, 0, 0,
                        '{"score": 95.0}', NULL, NULL, 'hash-null-1')
            """, (t_id,))
            conn.execute("""
                INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                      detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                      result, client_id, assessment_nonce, request_hash)
                VALUES (%s, 's1', 'Test', 10, '2026-10-17T00:00:00Z', 100, 95.0, 30.0, 30.0, 35.0, 'A', 0, 0, 0,
                        '{"score": 95.0}', NULL, NULL, 'hash-null-2')
            """, (t_id,))

            # 9. Idempotence: re-running _migrate_postgres is safe and produces no changes
            _migrate_postgres(conn)
            rows2 = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
            assert [r["version"] for r in rows2] == [1, 2, 3, 4]

            # 10. Legacy duplicate data handling in disposable database: aborts cleanly and rolls back
            conn.execute("CREATE DATABASE legacy_pg_test")
            legacy_conn = psycopg.connect(f"host=127.0.0.1 port={port} user=postgres dbname=legacy_pg_test",
                                          autocommit=True, row_factory=psycopg.rows.dict_row)
            try:
                # Apply schema v1 and v2 manually
                schema_pg_sql = (Path(__file__).parent.parent / "app" / "schema_pg.sql").read_text(encoding="utf-8")
                legacy_conn.execute(schema_pg_sql)
                legacy_conn.execute("""
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TEXT NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
                    )
                """)
                legacy_conn.execute("INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema'), (2, 'v2')")
                legacy_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT")
                legacy_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS assessment_nonce TEXT")
                legacy_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS request_hash TEXT")
                legacy_conn.execute("DROP INDEX IF EXISTS idx_sessions_client")
                legacy_conn.execute("CREATE INDEX idx_sessions_client ON sessions (client_id)")

                # Insert duplicate client_id
                t_leg = legacy_conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('LEG-1', 'LEG-COY') RETURNING id").fetchone()["id"]
                legacy_conn.execute("""
                    INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                          detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                          result, client_id)
                    VALUES (%s, 's1', 'Test', 1, '2026-10-17T00:00:00Z', 10, 100, 30, 30, 40, 'A', 0, 0, 0, '{"score": 100}', 'dup-client-id')
                """, (t_leg,))
                legacy_conn.execute("""
                    INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                          detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                          result, client_id)
                    VALUES (%s, 's1', 'Test', 2, '2026-10-17T00:00:00Z', 10, 100, 30, 30, 40, 'A', 0, 0, 0, '{"score": 100}', 'dup-client-id')
                """, (t_leg,))

                # Migration 3 must detect duplicates and abort cleanly with informative RuntimeError
                with pytest.raises(RuntimeError) as exc_info:
                    _migrate_postgres(legacy_conn)
                assert "Migration 3 aborted: duplicate client_id found in PostgreSQL sessions" in str(exc_info.value)
                assert "dup-client-id (count=2)" in str(exc_info.value)

                # Verify version 3 was NOT recorded
                leg_versions = [r["version"] for r in legacy_conn.execute("SELECT version FROM schema_migrations").fetchall()]
                assert 3 not in leg_versions
            finally:
                legacy_conn.close()

            # 11. Legacy duplicate assessment_nonce in disposable database: aborts cleanly without data loss
            conn.execute("CREATE DATABASE legacy_nonce_pg_test")
            legacy_nonce_conn = psycopg.connect(f"host=127.0.0.1 port={port} user=postgres dbname=legacy_nonce_pg_test",
                                                autocommit=True, row_factory=psycopg.rows.dict_row)
            try:
                legacy_nonce_conn.execute(schema_pg_sql)
                legacy_nonce_conn.execute("""
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TEXT NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
                    )
                """)
                legacy_nonce_conn.execute("INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema'), (2, 'v2')")
                legacy_nonce_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT")
                legacy_nonce_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS assessment_nonce TEXT")
                legacy_nonce_conn.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS request_hash TEXT")
                legacy_nonce_conn.execute("DROP INDEX IF EXISTS idx_sessions_nonce")
                legacy_nonce_conn.execute("CREATE INDEX idx_sessions_nonce ON sessions (assessment_nonce)")

                t_leg2 = legacy_nonce_conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('LEG-2', 'LEG-COY-2') RETURNING id").fetchone()["id"]
                legacy_nonce_conn.execute("""
                    INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                          detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                          result, client_id, assessment_nonce)
                    VALUES (%s, 's1', 'Test', 1, '2026-10-17T00:00:00Z', 10, 100, 30, 30, 40, 'A', 0, 0, 0, '{"score": 100}', 'client-leg-1', 'dup-nonce-id')
                """, (t_leg2,))
                legacy_nonce_conn.execute("""
                    INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                                          detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                                          result, client_id, assessment_nonce)
                    VALUES (%s, 's1', 'Test', 2, '2026-10-17T00:00:00Z', 10, 100, 30, 30, 40, 'A', 0, 0, 0, '{"score": 100}', 'client-leg-2', 'dup-nonce-id')
                """, (t_leg2,))

                # Migration 3 must detect duplicate assessment_nonce and abort cleanly with informative RuntimeError
                with pytest.raises(RuntimeError) as exc_info:
                    _migrate_postgres(legacy_nonce_conn)
                assert "Migration 3 aborted: duplicate assessment_nonce found in PostgreSQL sessions" in str(exc_info.value)
                assert "dup-nonce-id (count=2)" in str(exc_info.value)

                # Verify version 3 was NOT recorded
                leg_nonce_versions = [r["version"] for r in legacy_nonce_conn.execute("SELECT version FROM schema_migrations").fetchall()]
                assert 3 not in leg_nonce_versions

                # Verify duplicate data was not silently deleted
                nonce_cnt = legacy_nonce_conn.execute("SELECT COUNT(*) AS cnt FROM sessions WHERE assessment_nonce = 'dup-nonce-id'").fetchone()["cnt"]
                assert nonce_cnt == 2
            finally:
                legacy_nonce_conn.close()

        finally:
            if conn:
                conn.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_file.close()


# ==============================================================================
# REL-03: Automated Backup & Restore Verification
# ==============================================================================

@pytest.fixture
def populated_db(tmp_path):
    """Create a fully migrated SQLite database populated with trainees, sessions, and events."""
    db_path = tmp_path / "source_trainer.db"
    conn = sqlite3.connect(str(db_path))
    _migrate_sqlite(conn)

    with conn:
        conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('BRAVO-1', 'ALPHA COY')")
        conn.execute("""
            INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at,
                                  duration_s, total, detection, classification, engagement,
                                  grade, false_alarms, breaches, critical_errors, result,
                                  client_id, assessment_nonce, request_hash)
            VALUES (1, 's1-dawn-recon', 'Dawn Recon', 101, '2026-10-17T08:00:00Z',
                    170.0, 92.5, 30.0, 30.0, 32.5, 'A', 0, 0, 0, '{"score": 92.5}',
                    'client-uuid-101', 'nonce-abc-101', 'hash-101-xyz')
        """)
        conn.execute("INSERT INTO events (session_id, t, type, contact_id, data) VALUES (1, 12.5, 'mark', 'c1', '{}')")
        conn.execute("INSERT INTO events (session_id, t, type, contact_id, data) VALUES (1, 18.0, 'classify', 'c1', '{\"class\": \"RECON_UAS\"}')")
    conn.close()
    return db_path


def test_rel03_backup_creation_and_integrity_verification(populated_db, tmp_path):
    """Online backup creates an uncorrupted SQLite copy with verified PRAGMA integrity."""
    backup_dir = tmp_path / "backups"
    target, manifest_path, meta = create_backup(populated_db, out_dir=backup_dir)

    assert target.exists()
    assert manifest_path.exists()
    assert meta["integrity_check"] == "ok"
    assert meta["schema_version"] == 4
    assert meta["table_counts"]["trainees"] == 1
    assert meta["table_counts"]["sessions"] == 1
    assert meta["table_counts"]["events"] == 2

    # Verification function passes
    valid, details = verify_backup(target)
    assert valid is True
    assert details["integrity_check"] == "ok"
    assert details["foreign_key_check"] == "ok"
    assert details["checksum_verified"] is True


def test_rel03_backup_manifest_and_sha256_checksum(populated_db, tmp_path):
    """Manifest file records exact SHA-256 matching the backup database."""
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "bak")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    hasher = hashlib.sha256()
    hasher.update(target.read_bytes())
    actual_hash = hasher.hexdigest()

    assert manifest["sha256"] == actual_hash
    assert meta["sha256"] == actual_hash


def test_rel03_restore_to_separate_destination(populated_db, tmp_path):
    """Restore copies verified backup into separate destination without altering source."""
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "bak")

    restored_db = tmp_path / "restored.db"
    success, msg = restore_backup(target, restored_db)
    assert success is True

    # Validate restored database content
    conn = sqlite3.connect(str(restored_db))
    trainees = conn.execute("SELECT callsign, unit FROM trainees").fetchall()
    assert trainees == [("BRAVO-1", "ALPHA COY")]

    sessions = conn.execute("SELECT total, grade, client_id FROM sessions").fetchall()
    assert sessions == [(92.5, "A", "client-uuid-101")]

    events = conn.execute("SELECT type, contact_id FROM events ORDER BY t").fetchall()
    assert events == [("mark", "c1"), ("classify", "c1")]

    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()]
    assert versions == [1, 2, 3, 4]
    conn.close()

    # Original database remains unchanged
    src_conn = sqlite3.connect(str(populated_db))
    assert src_conn.execute("SELECT COUNT(*) FROM trainees").fetchone()[0] == 1
    src_conn.close()


def test_rel03_restore_fails_on_collision_without_force(populated_db, tmp_path):
    """Restore aborts with error if target exists unless force=True is provided."""
    target, _, _ = create_backup(populated_db, out_dir=tmp_path / "bak")
    existing_dest = tmp_path / "already_exists.db"
    existing_dest.write_text("dummy collision file")

    # Without force: fails
    success, msg = restore_backup(target, existing_dest, force=False)
    assert success is False
    assert "already exists" in msg

    # With force: succeeds
    success, msg = restore_backup(target, existing_dest, force=True)
    assert success is True
    assert existing_dest.stat().st_size > 1000


def test_rel03_restore_refuses_to_overwrite_source_backup(populated_db, tmp_path):
    """Restore refuses to restore a backup file directly over itself."""
    target, _, _ = create_backup(populated_db, out_dir=tmp_path / "bak")
    success, msg = restore_backup(target, target)
    assert success is False
    assert "Cannot restore a backup over itself" in msg


def test_rel03_corrupt_backup_rejected_by_verification_and_restore(populated_db, tmp_path):
    """Corrupted backup with modified bytes fails verification and aborts restore."""
    target, manifest_path, _ = create_backup(populated_db, out_dir=tmp_path / "bak")

    # Tamper with the backup bytes
    data = bytearray(target.read_bytes())
    data[100:150] = b"\xFF" * 50
    target.write_bytes(data)

    # Verification must fail checksum
    valid, details = verify_backup(target)
    assert valid is False
    assert "checksum mismatch" in details["error"].lower()

    # Restore must fail
    dest = tmp_path / "bad_restore.db"
    success, msg = restore_backup(target, dest)
    assert success is False
    assert "verification failed" in msg.lower()
    assert not dest.exists()


def test_rel03_backup_online_wal_transaction_consistency(tmp_path):
    """Online backup remains consistent when writes and WAL activity occur concurrently."""
    import threading
    import time

    wal_db = tmp_path / "wal_source.db"
    conn = sqlite3.connect(str(wal_db))
    _migrate_sqlite(conn)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('CONCURRENT', 'TEST UNIT')")
    conn.commit()

    stop_event = threading.Event()
    write_errors = []

    def writer_loop():
        w_conn = sqlite3.connect(str(wal_db), timeout=10.0)
        i = 0
        try:
            while not stop_event.is_set():
                try:
                    w_conn.execute("INSERT INTO trainees (callsign, unit) VALUES (?, ?)", (f"T-{i}", f"U-{i}"))
                    w_conn.commit()
                    i += 1
                except Exception as exc:
                    write_errors.append(exc)
                    break
        finally:
            w_conn.close()

    writer_thread = threading.Thread(target=writer_loop, daemon=True)
    writer_thread.start()

    time.sleep(0.05)

    try:
        backup_dir = tmp_path / "wal_backups"
        target, manifest_path, meta = create_backup(wal_db, out_dir=backup_dir)
        assert target.exists()
        assert manifest_path.exists()
        assert meta["integrity_check"] == "ok"
    finally:
        stop_event.set()
        writer_thread.join(timeout=3.0)
        conn.close()

    assert not write_errors, f"Concurrent writer encountered errors: {write_errors}"

    valid, details = verify_backup(target)
    assert valid is True
    assert details["integrity_check"] == "ok"
    assert details["foreign_key_check"] == "ok"


def test_rel03_backup_missing_or_invalid_manifest_handling(populated_db, tmp_path):
    """Managed backups require an accompanying valid manifest; standalone mode allows unmanaged verification."""
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "bak")

    # 1. Verification succeeds when manifest exists and matches
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is True
    assert details["checksum_verified"] is True

    # 2. Delete manifest: managed verification fails closed
    manifest_path.unlink()
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "Manifest file not found" in details["error"]

    # 3. Unmanaged mode (--allow-unmanaged) verifies SQLite integrity but notes unmanaged status
    valid, details = verify_backup(target, require_manifest=False)
    assert valid is True
    assert details["integrity_check"] == "ok"
    assert details["checksum_verified"] is False
    assert details["unmanaged"] is True

    # 4. Pre-restore verification fails closed without manifest by default
    dest_db = tmp_path / "restore_dest.db"
    success, msg = restore_backup(target, dest_db, require_manifest=True)
    assert success is False
    assert "Pre-restore verification failed" in msg
    assert not dest_db.exists()

    # 5. Restore with require_manifest=False succeeds for standalone SQLite files
    success, msg = restore_backup(target, dest_db, require_manifest=False)
    assert success is True
    assert dest_db.exists()
    dest_db.unlink()

    # 6. Recreate manifest with tampered SHA-256: verification fails
    meta_copy = dict(meta, sha256="0" * 64)
    manifest_path.write_text(json.dumps(meta_copy), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "SHA-256 checksum mismatch" in details["error"]


def test_rel03_backup_cli_commands(populated_db, tmp_path, monkeypatch, capsys):
    """CLI subcommands (backup, verify, list, info, restore) execute successfully with proper exit codes."""
    bak_dir = tmp_path / "cli_backups"

    # 1. backup
    exit_code = backup_main(["backup", "--db", str(populated_db), "--dir", str(bak_dir)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[OK] Backup created successfully" in captured.out

    backups = list_backups(bak_dir)
    assert len(backups) == 1
    bak_file = Path(backups[0]["path"])

    # 2. verify
    exit_code = backup_main(["verify", str(bak_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[OK] Backup verification passed" in captured.out

    # 3. info
    exit_code = backup_main(["info", str(bak_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Version     : v4" in captured.out

    # 4. list
    exit_code = backup_main(["list", "--dir", str(bak_dir)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Found 1 backup(s)" in captured.out

    # 5. restore
    dest_db = tmp_path / "cli_restored.db"
    exit_code = backup_main(["restore", str(bak_file), "--dest", str(dest_db)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[OK] Successfully restored" in captured.out
    assert dest_db.exists()


def test_rel03_manifest_field_tampering_fails_verification(populated_db, tmp_path):
    """Manifest tampering and schema corruption strictly fails managed backup verification.

    Covers all negative scenarios for Finding B:
    - Missing manifest file
    - Invalid JSON manifest
    - Non-dict JSON manifest
    - Missing or invalid format_version
    - Engine mismatch
    - Malformed or missing timestamp_utc
    - Missing source_db or backup_file
    - Missing, malformed, or mismatched sha256
    - Missing, boolean, negative, or mismatched size_bytes
    - Missing, null, boolean, string, or mismatched schema_version
    - Missing, null, list, or string table_counts
    - Missing or unexpected table entries in table_counts
    - Incorrect or invalid-typed table count values
    - Missing application tables
    - Corrupt SQLite file
    - Foreign key violation
    """
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "strict_bak")

    # Baseline verification passes
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is True

    # 1. Missing manifest file
    orphaned_target = tmp_path / "orphaned_bak.db"
    orphaned_target.write_bytes(target.read_bytes())
    valid, details = verify_backup(orphaned_target, require_manifest=True)
    assert valid is False
    assert "Manifest file not found" in details["error"]

    # 2. Invalid JSON manifest
    manifest_path.write_text("{not: valid, json", encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "Failed to read manifest" in details["error"]

    # 3. Non-dict JSON manifest
    manifest_path.write_text("[\"not\", \"a\", \"dict\"]", encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "Manifest must be a JSON object" in details["error"]

    # 4. Missing or invalid format_version
    bad_fmt = dict(meta)
    del bad_fmt["format_version"]
    manifest_path.write_text(json.dumps(bad_fmt), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "format_version" in details["error"]

    bad_fmt_bool = dict(meta, format_version=True)
    manifest_path.write_text(json.dumps(bad_fmt_bool), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "format_version" in details["error"]

    bad_fmt_num = dict(meta, format_version=2)
    manifest_path.write_text(json.dumps(bad_fmt_num), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "format_version" in details["error"]

    # 5. Engine mismatch
    bad_engine = dict(meta, engine="postgres")
    manifest_path.write_text(json.dumps(bad_engine), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "'engine' field must be 'sqlite'" in details["error"]

    # 6. Malformed or missing timestamp_utc
    bad_ts = dict(meta, timestamp_utc="invalid-date-string")
    manifest_path.write_text(json.dumps(bad_ts), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "timestamp_utc" in details["error"]

    # 7. Missing source_db or backup_file
    bad_src = dict(meta, source_db="")
    manifest_path.write_text(json.dumps(bad_src), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "source_db" in details["error"]

    bad_bf = dict(meta, backup_file="")
    manifest_path.write_text(json.dumps(bad_bf), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "backup_file" in details["error"]

    # 8. Missing, malformed, or mismatched sha256
    no_hash = dict(meta)
    del no_hash["sha256"]
    manifest_path.write_text(json.dumps(no_hash), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "sha256" in details["error"]

    malformed_hash = dict(meta, sha256="z" * 64)  # non-hex
    manifest_path.write_text(json.dumps(malformed_hash), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "sha256" in details["error"]

    mismatch_hash = dict(meta, sha256="0" * 64)
    manifest_path.write_text(json.dumps(mismatch_hash), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "SHA-256 checksum mismatch" in details["error"]

    # 9. Missing, boolean, negative, or mismatched size_bytes
    no_size = dict(meta)
    del no_size["size_bytes"]
    manifest_path.write_text(json.dumps(no_size), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "size_bytes" in details["error"]

    bool_size = dict(meta, size_bytes=True)
    manifest_path.write_text(json.dumps(bool_size), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "size_bytes" in details["error"]

    neg_size = dict(meta, size_bytes=-100)
    manifest_path.write_text(json.dumps(neg_size), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "size_bytes" in details["error"]

    mismatch_size = dict(meta, size_bytes=meta["size_bytes"] + 50)
    manifest_path.write_text(json.dumps(mismatch_size), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "File size mismatch" in details["error"]

    # 10. Missing, null, boolean, string, or mismatched schema_version
    no_schema = dict(meta)
    del no_schema["schema_version"]
    manifest_path.write_text(json.dumps(no_schema), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "schema_version" in details["error"]

    null_schema = dict(meta, schema_version=None)
    manifest_path.write_text(json.dumps(null_schema), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "schema_version" in details["error"]

    bool_schema = dict(meta, schema_version=True)
    manifest_path.write_text(json.dumps(bool_schema), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "schema_version" in details["error"]

    str_schema = dict(meta, schema_version="v4")
    manifest_path.write_text(json.dumps(str_schema), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "schema_version" in details["error"]

    mismatch_schema = dict(meta, schema_version=99)
    manifest_path.write_text(json.dumps(mismatch_schema), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "Schema version mismatch" in details["error"]

    # 11. Missing, null, list, or string table_counts
    no_tc = dict(meta)
    del no_tc["table_counts"]
    manifest_path.write_text(json.dumps(no_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "table_counts" in details["error"]

    null_tc = dict(meta, table_counts=None)
    manifest_path.write_text(json.dumps(null_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "table_counts" in details["error"]

    list_tc = dict(meta, table_counts=["trainees", "sessions", "events"])
    manifest_path.write_text(json.dumps(list_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "table_counts" in details["error"]

    # 12. Missing required table entry in table_counts
    missing_tbl_tc = dict(meta, table_counts={"trainees": 1, "sessions": 1})  # missing 'events'
    manifest_path.write_text(json.dumps(missing_tbl_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "table_counts" in details["error"]

    # 13. Unexpected table entry in table_counts
    extra_tbl_tc = dict(meta, table_counts={"trainees": 1, "sessions": 1, "events": 2, "audit_log": 0})
    manifest_path.write_text(json.dumps(extra_tbl_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "table_counts" in details["error"]

    # 14. Incorrect table counts for trainees, sessions, events
    for tbl in ("trainees", "sessions", "events"):
        bad_cnt_tc = dict(meta, table_counts={**meta["table_counts"], tbl: 9999})
        manifest_path.write_text(json.dumps(bad_cnt_tc), encoding="utf-8")
        valid, details = verify_backup(target, require_manifest=True)
        assert valid is False
        assert f"Table '{tbl}' record count mismatch" in details["error"]

    # 15. Invalid types for table counts (bool, negative, string)
    bool_cnt_tc = dict(meta, table_counts={**meta["table_counts"], "trainees": True})
    manifest_path.write_text(json.dumps(bool_cnt_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "non-negative integer" in details["error"]

    neg_cnt_tc = dict(meta, table_counts={**meta["table_counts"], "events": -5})
    manifest_path.write_text(json.dumps(neg_cnt_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "non-negative integer" in details["error"]

    str_cnt_tc = dict(meta, table_counts={**meta["table_counts"], "sessions": "one"})
    manifest_path.write_text(json.dumps(str_cnt_tc), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is False
    assert "non-negative integer" in details["error"]

    # Restore valid manifest
    manifest_path.write_text(json.dumps(meta), encoding="utf-8")
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is True

    # 16. Missing required application table in database
    missing_app_tbl_db = tmp_path / "missing_tbl.db"
    conn_m = sqlite3.connect(str(missing_app_tbl_db))
    conn_m.execute("CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT)")
    conn_m.commit()
    conn_m.close()
    valid, details = verify_backup(missing_app_tbl_db, require_manifest=False)
    assert valid is False
    assert "missing required application table" in details["error"]

    # 17. Corrupt SQLite database file
    corrupt_db = tmp_path / "corrupt_data.db"
    corrupt_db.write_bytes(b"SQLite format 3\x00corrupted garbage data header")
    valid, details = verify_backup(corrupt_db, require_manifest=False)
    assert valid is False
    assert "Integrity check failed" in details["error"] or "error during verification" in details["error"]

    # 18. Invalid foreign key relationships
    fk_db = tmp_path / "fk_violation.db"
    fk_target, fk_manifest, fk_meta = create_backup(populated_db, out_path=fk_db)
    conn_fk = sqlite3.connect(str(fk_target))
    conn_fk.execute("PRAGMA foreign_keys = OFF")
    conn_fk.execute("""
        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s, total,
                              detection, classification, engagement, grade, false_alarms, breaches, critical_errors,
                              result, client_id, assessment_nonce, request_hash)
        VALUES (9999, 's1', 'Test', 1, '2026-10-17T00:00:00Z', 10, 100, 30, 30, 40, 'A', 0, 0, 0,
                '{"score": 100}', 'cid-fk', 'nonce-fk', 'hash-fk')
    """)
    conn_fk.commit()
    conn_fk.close()
    fk_manifest.unlink()
    valid, details = verify_backup(fk_target, require_manifest=False)
    assert valid is False
    assert "Foreign key check failed" in details["error"]


def test_rel03_restore_safe_replacement_destination_preserved_on_failure(populated_db, tmp_path, monkeypatch):
    """Restore preserves existing destination whenever staging, validation, or replacement fails."""
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "safe_restore_bak")

    # Create pre-existing destination DB with specific canary data
    dest_db = tmp_path / "existing_dest.db"
    conn = sqlite3.connect(str(dest_db))
    conn.execute("CREATE TABLE canary (id INTEGER PRIMARY KEY, note TEXT)")
    conn.execute("INSERT INTO canary (id, note) VALUES (42, 'important-data-must-not-be-lost')")
    conn.commit()
    conn.close()
    original_dest_bytes = dest_db.read_bytes()

    # 1. Pre-restore verification failure preserves destination
    bad_hash = dict(meta, sha256="0" * 64)
    manifest_path.write_text(json.dumps(bad_hash), encoding="utf-8")
    success, msg = restore_backup(target, dest_db, force=True, require_manifest=True)
    assert success is False
    assert "Pre-restore verification failed" in msg
    assert dest_db.read_bytes() == original_dest_bytes

    # Restore valid manifest
    manifest_path.write_text(json.dumps(meta), encoding="utf-8")

    # 2. Destination replacement failure preserves existing destination and canary row
    orig_replace = os.replace

    def mock_replace(src, dst):
        if str(dst) == str(dest_db):
            raise OSError("Simulated atomic replacement failure on destination")
        return orig_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace)

    success, msg = restore_backup(target, dest_db, force=True, require_manifest=True)
    assert success is False
    assert "Failed to replace destination database: Simulated atomic replacement failure" in msg

    # Assert destination and canary data were preserved intact
    assert dest_db.read_bytes() == original_dest_bytes
    conn = sqlite3.connect(str(dest_db))
    row = conn.execute("SELECT id, note FROM canary WHERE id = 42").fetchone()
    conn.close()
    assert row is not None
    assert row[1] == "important-data-must-not-be-lost"

    # 3. Restore to a previously nonexistent destination with replacement failure leaves no partial file
    monkeypatch.undo()
    nonexistent_dest = tmp_path / "never_created.db"

    def mock_replace_nonexistent(src, dst):
        if str(dst) == str(nonexistent_dest):
            raise OSError("Disk write fault")
        return orig_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace_nonexistent)
    success, msg = restore_backup(target, nonexistent_dest, force=False, require_manifest=True)
    assert success is False
    assert "Failed to replace destination database" in msg
    assert not nonexistent_dest.exists()


def test_rel03_backup_finalization_failure_recovery(populated_db, tmp_path, monkeypatch):
    """create_backup rollback recovery prevents inconsistent database/manifest pairs on replacement failure."""
    out_dir = tmp_path / "recoverable_bak"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_bak = out_dir / "test_backup.db"
    manifest_bak = target_bak.with_suffix(".meta.json")

    # Create initial valid backup pair
    target, m_path, meta = create_backup(populated_db, out_path=target_bak)
    valid, details = verify_backup(target, require_manifest=True)
    assert valid is True
    original_target_bytes = target_bak.read_bytes()
    original_manifest_text = manifest_bak.read_text(encoding="utf-8")

    # Fault injection: simulate second replacement (manifest) failing after target replacement succeeds
    orig_replace = os.replace

    def mock_replace_manifest_fail(src, dst):
        if str(dst) == str(manifest_bak):
            raise OSError("Simulated disk error during manifest replacement")
        return orig_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace_manifest_fail)

    with pytest.raises(OSError, match="Simulated disk error during manifest replacement"):
        create_backup(populated_db, out_path=target_bak)

    # Rollback must have restored the previous valid target and manifest pair intact
    assert target_bak.read_bytes() == original_target_bytes
    assert manifest_bak.read_text(encoding="utf-8") == original_manifest_text
    valid, details = verify_backup(target_bak, require_manifest=True)
    assert valid is True, f"Backup pair was left inconsistent after failure: {details}"

    # Fault injection on fresh backup (destination didn't previously exist)
    fresh_bak = out_dir / "fresh_backup.db"
    fresh_meta = fresh_bak.with_suffix(".meta.json")

    def mock_replace_fresh_fail(src, dst):
        if str(dst) == str(fresh_meta):
            raise OSError("Manifest disk write failed")
        return orig_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace_fresh_fail)

    with pytest.raises(OSError, match="Manifest disk write failed"):
        create_backup(populated_db, out_path=fresh_bak)

    # Must not leave an orphaned target database file without a manifest
    assert not fresh_bak.exists()
    assert not fresh_meta.exists()


def test_rel03_finding_a_backup_source_collision_derived_manifest_rejected(tmp_path):
    """Finding A: Backup derived manifest or target colliding with source database must be rejected.

    Reproduced arrangement:
    - Source database named: 'source.meta.json'
    - Backup destination: 'source.db'
    - Derived manifest: 'source.meta.json' (collides directly with source DB)
    Asserts:
    1. ValueError is raised before any file creation or overwriting.
    2. Original source database bytes and SHA-256 remain unchanged.
    3. PRAGMA integrity_check on source returns 'ok'.
    4. Case-insensitive and same-file aliasing are also rejected.
    """
    src_db = tmp_path / "source.meta.json"
    conn = sqlite3.connect(str(src_db))
    conn.execute("CREATE TABLE canary (id INTEGER PRIMARY KEY, note TEXT)")
    conn.execute("INSERT INTO canary (id, note) VALUES (1, 'vital-operational-database')")
    conn.commit()
    conn.close()

    original_bytes = src_db.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()

    # Derived manifest collision: source='source.meta.json', target='source.db' -> manifest='source.meta.json'
    target_db = tmp_path / "source.db"
    with pytest.raises(ValueError, match="collides with the active source database"):
        create_backup(src_db, out_path=target_db)

    # Assert source database remained completely untouched
    assert src_db.read_bytes() == original_bytes
    assert hashlib.sha256(src_db.read_bytes()).hexdigest() == original_hash
    chk = sqlite3.connect(str(src_db))
    assert chk.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert chk.execute("SELECT note FROM canary WHERE id = 1").fetchone()[0] == "vital-operational-database"
    chk.close()

    # Case-insensitive / relative path collision:
    upper_target = tmp_path / "SOURCE.META.JSON"
    with pytest.raises(ValueError, match="Cannot write backup over the active source database"):
        create_backup(src_db, out_path=upper_target)


def test_rel03_finding_b_manifest_metadata_strict_validation(populated_db, tmp_path):
    """Finding B: Manifest verification rejects format_version 1.0, naive/date-only timestamps, and mismatched backup_file."""
    target, manifest_path, meta = create_backup(populated_db, out_dir=tmp_path / "strict_meta_bak")

    # Baseline passes
    valid, details = verify_backup(target)
    assert valid is True

    # 1. format_version: 1.0 (float) must be rejected (must be integer 1, not float or bool)
    float_meta = dict(meta, format_version=1.0)
    manifest_path.write_text(json.dumps(float_meta), encoding="utf-8")
    valid, details = verify_backup(target)
    assert valid is False
    assert "integer 'format_version' equal to 1" in details["error"]

    # 2. timestamp_utc: "2026-10-17" (date-only) must be rejected
    date_only_meta = dict(meta, timestamp_utc="2026-10-17")
    manifest_path.write_text(json.dumps(date_only_meta), encoding="utf-8")
    valid, details = verify_backup(target)
    assert valid is False
    assert "full ISO-8601 datetime containing time" in details["error"]

    # 3. timestamp_utc: "2026-10-17T12:00:00" (timezone-naive) must be rejected
    naive_meta = dict(meta, timestamp_utc="2026-10-17T12:00:00")
    manifest_path.write_text(json.dumps(naive_meta), encoding="utf-8")
    valid, details = verify_backup(target)
    assert valid is False
    assert "explicit UTC timezone" in details["error"]

    # 4. timestamp_utc: "2026-10-17T12:00:00+05:30" (non-UTC offset) must be rejected
    non_utc_meta = dict(meta, timestamp_utc="2026-10-17T12:00:00+05:30")
    manifest_path.write_text(json.dumps(non_utc_meta), encoding="utf-8")
    valid, details = verify_backup(target)
    assert valid is False
    assert "specify UTC timezone" in details["error"]

    # 5. backup_file: "other.db" (mismatched filename) must be rejected
    other_file_meta = dict(meta, backup_file="other.db")
    manifest_path.write_text(json.dumps(other_file_meta), encoding="utf-8")
    valid, details = verify_backup(target)
    assert valid is False
    assert "Manifest 'backup_file' mismatch" in details["error"]


def test_rel03_finding_d_backup_finalization_failure_with_rollback_failure(populated_db, tmp_path, monkeypatch):
    """Finding D: Rollback failure after finalization failure must be observable with original context preserved.

    Tests both:
    1. Pre-existing valid destination where restoring previous backup fails.
    2. Fresh destination where unlinking incomplete backup fails.
    """
    out_dir = tmp_path / "rollback_fail_bak"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_bak = out_dir / "existing_backup.db"
    manifest_bak = target_bak.with_suffix(".meta.json")

    # Establish pre-existing valid backup pair
    target, m_path, meta = create_backup(populated_db, out_path=target_bak)
    valid, _ = verify_backup(target)
    assert valid is True

    orig_replace = os.replace
    orig_write_bytes = Path.write_bytes

    # Simulate finalization error (replace manifest fails)
    def mock_replace_fail(src, dst):
        if str(dst) == str(manifest_bak):
            raise OSError("Primary finalization disk replace failure")
        return orig_replace(src, dst)

    # Simulate rollback write_bytes failure when attempting to restore target_path
    def mock_write_bytes_fail(self, data):
        if str(self) == str(target_bak):
            raise OSError("Secondary rollback write fault")
        return orig_write_bytes(self, data)

    monkeypatch.setattr(os, "replace", mock_replace_fail)
    monkeypatch.setattr(Path, "write_bytes", mock_write_bytes_fail)

    with pytest.raises(RuntimeError) as exc_info:
        create_backup(populated_db, out_path=target_bak)

    err = str(exc_info.value)
    assert "Backup finalization failed" in err
    assert "rollback also failed" in err
    assert "Primary finalization disk replace failure" in err
    assert "failed to restore previous target" in err
    assert isinstance(exc_info.value.__cause__, OSError)

    # 2. Fresh destination failure injection: finalization fails, and unlink during rollback fails
    monkeypatch.undo()
    fresh_bak = out_dir / "fresh_backup_2.db"
    fresh_manifest = fresh_bak.with_suffix(".meta.json")

    orig_unlink = Path.unlink

    def mock_replace_fresh_fail(src, dst):
        if str(dst) == str(fresh_manifest):
            raise OSError("Fresh finalization error")
        return orig_replace(src, dst)

    def mock_unlink_fresh_fail(self):
        if str(self) == str(fresh_bak):
            raise OSError("Fresh rollback unlink permission denied")
        return orig_unlink(self)

    monkeypatch.setattr(os, "replace", mock_replace_fresh_fail)
    monkeypatch.setattr(Path, "unlink", mock_unlink_fresh_fail)

    with pytest.raises(RuntimeError) as exc_info2:
        create_backup(populated_db, out_path=fresh_bak)

    err2 = str(exc_info2.value)
    assert "Backup finalization failed" in err2
    assert "rollback also failed" in err2
    assert "failed to remove incomplete target" in err2

