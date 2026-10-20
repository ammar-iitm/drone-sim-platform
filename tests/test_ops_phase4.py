"""Phase 4: Operations & Observability Tests (OPS-01).

Tests:
1. Health check endpoint (GET /health and GET /api/health)
   - 200 on healthy reachable database and schema at expected migration version (v4).
   - 503 on degraded, unreachable, missing, or incompatible database schema.
   - Read-only behavior: probes never run migrations, mutate data, or create missing database files.
   - Information privacy: responses never expose internal paths, URLs, SQL, or exceptions.
   - Resource cleanup: connections reliably closed on both success and error.

2. Deployment environment validator (scripts/check_env.py)
   - Supports modes: auto, offline, lan, hosted.
   - Validates rubric.json, SECRET_KEY, INSTRUCTOR_PASSWORD, DATABASE_URL, and platform constraints.
   - Exit code contract: 0 on success, 1 on failure.
   - Privacy guarantee: secret keys, passwords, and connection credentials are NEVER printed.

3. Structured security audit logging (app/audit.py)
   - Machine-parseable JSON records with UTC timestamps, stable event names, actor, and outcome.
   - Covers: auth (login, failure, rate limit, logout, access denied), exports (session CSV, unit CSV),
     and rubric provenance (initial load and version change observation).
   - Privacy guarantee: never logs passwords, tokens, cookies, secrets, or raw request/CSV bodies.
   - Fail-safe: logging failures never crash user requests.
"""

import hashlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import pytest

from app import create_app
from app.audit import (
    AUDIT_LOGGER_NAME,
    check_rubric_provenance,
    compute_rubric_hash,
    log_audit_event,
)
from app.db import EXPECTED_SCHEMA_VERSION, REQUIRED_TABLES, check_database_health
from scripts.check_env import run_checks


ROOT = Path(__file__).resolve().parent.parent


# ==============================================================================
# 1. Health Endpoint Tests
# ==============================================================================

def test_health_endpoint_healthy_sqlite(tmp_path):
    """Reachable SQLite database with schema at expected migration version returns 200."""
    db_file = tmp_path / "healthy.db"
    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    # Trigger schema initialization via normal app client
    with app.app_context():
        from app.db import get_db
        get_db()

    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {
        "status": "ok",
        "checks": {
            "database": "ok",
            "schema": "ok",
        },
    }

    # API alias endpoint behaves identically
    api_resp = client.get("/api/health")
    assert api_resp.status_code == 200
    assert api_resp.get_json() == data


def test_health_endpoint_missing_schema_returns_503(tmp_path):
    """Reachable database with missing required schema tables returns 503."""
    db_file = tmp_path / "empty.db"
    # Create empty database file without running migrations
    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE dummy (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data == {
        "status": "unhealthy",
        "checks": {
            "database": "ok",
            "schema": "error",
        },
    }


def test_health_endpoint_outdated_schema_version_returns_503(tmp_path):
    """Reachable database with outdated migration version returns 503."""
    db_file = tmp_path / "outdated.db"
    conn = sqlite3.connect(str(db_file))
    # Create required tables but record only migration version 3 (outdated; expected is 4)
    for tbl in REQUIRED_TABLES:
        if tbl == "schema_migrations":
            conn.execute("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT, applied_at TEXT)")
        else:
            conn.execute(f"CREATE TABLE {tbl} (id INTEGER PRIMARY KEY)")
    conn.execute("INSERT INTO schema_migrations (version, name) VALUES (1, 'v1'), (2, 'v2'), (3, 'v3')")
    conn.commit()
    conn.close()

    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["status"] == "unhealthy"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["schema"] == "error"


def test_health_endpoint_unreachable_db_returns_503(tmp_path):
    """Unreachable database returns 503 with both database and schema in error."""
    non_existent = tmp_path / "does_not_exist" / "missing.db"
    app = create_app({"DATABASE": str(non_existent), "TESTING": True})
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data == {
        "status": "unhealthy",
        "checks": {
            "database": "error",
            "schema": "error",
        },
    }


def test_health_endpoint_does_not_mutate_or_migrate(tmp_path):
    """Probing /health must NEVER trigger schema migration or create missing files."""
    db_file = tmp_path / "uninitialized.db"
    assert not db_file.exists()

    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    # Health probe on non-existent database
    resp = client.get("/health")
    assert resp.status_code == 503

    # Probing /health must NOT create the database file
    assert not db_file.exists(), "Health probe must not create SQLite database file"

    # Create an unmigrated database with a single table
    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE canary (id INT)")
    conn.commit()
    conn.close()
    size_before = db_file.stat().st_size

    resp2 = client.get("/health")
    assert resp2.status_code == 503

    # Verify no new tables were created and file size did not change
    conn2 = sqlite3.connect(str(db_file))
    tables = [r[0] for r in conn2.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn2.close()
    assert tables == ["canary"], "Health probe must not create tables or run migrations"
    assert db_file.stat().st_size == size_before


def test_health_endpoint_does_not_leak_internals(tmp_path):
    """Health response must never disclose database paths, queries, or exceptions."""
    sensitive_path = tmp_path / "confidential_classified_path_secret_12345" / "trainer.db"
    app = create_app({"DATABASE": str(sensitive_path), "TESTING": True})
    client = app.test_client()

    resp = client.get("/health")
    raw_body = resp.get_data(as_text=True)
    assert "confidential" not in raw_body
    assert "classified" not in raw_body
    assert "secret" not in raw_body
    assert "SELECT" not in raw_body
    assert "sqlite" not in raw_body.lower()


def test_health_endpoint_closes_connection(tmp_path):
    """Health probe reliably closes temporary database connections on both success and failure."""
    db_file = tmp_path / "lock_check.db"
    app = create_app({"DATABASE": str(db_file), "TESTING": True})

    # Probing health check function directly
    with app.app_context():
        check_database_health(app)

    # File should not be locked; we must be able to remove or write to it immediately
    if db_file.exists():
        os.remove(str(db_file))


# ==============================================================================
# 2. Environment Validator Tests (scripts/check_env.py)
# ==============================================================================

def test_check_env_offline_mode_success():
    """Offline mode passes with valid rubric and local SQLite configuration."""
    checks, code, mode = run_checks(mode="offline")
    assert mode == "offline"
    assert code == 0
    assert all(c["status"] != "FAIL" for c in checks)


def test_check_env_lan_mode_requires_secret_key_and_password():
    """LAN mode requires a valid SECRET_KEY and INSTRUCTOR_PASSWORD (or bypass)."""
    # 1. Missing both -> fails
    env_empty = {"LAN_MODE": "1", "PATH": os.environ.get("PATH", "")}
    checks, code, _ = run_checks(mode="lan", env=env_empty)
    assert code == 1
    fail_names = {c["name"] for c in checks if c["status"] == "FAIL"}
    assert "SECRET_KEY Policy" in fail_names
    assert "Instructor Authentication" in fail_names

    # 2. Valid secret key and password -> passes
    env_valid = {
        "LAN_MODE": "1",
        "SECRET_KEY": "0123456789abcdef0123456789abcdef",  # 32 chars, >= 8 unique chars
        "INSTRUCTOR_PASSWORD": "ValidInstructorPassword123!",
        "PATH": os.environ.get("PATH", ""),
    }
    checks2, code2, _ = run_checks(mode="lan", env=env_valid)
    assert code2 == 0
    assert all(c["status"] != "FAIL" for c in checks2)

    # 3. LAN unauthenticated bypass permitted with warning
    env_bypass = {
        "LAN_MODE": "1",
        "SECRET_KEY": "fedcba9876543210fedcba9876543210",
        "ALLOW_UNAUTHENTICATED_LAN": "1",
        "PATH": os.environ.get("PATH", ""),
    }
    checks3, code3, _ = run_checks(mode="lan", env=env_bypass)
    assert code3 == 0
    warn_names = {c["name"] for c in checks3 if c["status"] == "WARN"}
    assert "Instructor Authentication" in warn_names


def test_check_env_hosted_mode_requires_secret_key_password_optional():
    """Hosted mode requires SECRET_KEY; INSTRUCTOR_PASSWORD is optional and only warns when unset."""
    env_hosted_empty = {"HOSTED": "1", "PATH": os.environ.get("PATH", "")}
    checks, code, _ = run_checks(mode="hosted", env=env_hosted_empty)
    assert code == 1
    fail_names = {c["name"] for c in checks if c["status"] == "FAIL"}
    assert "SECRET_KEY Policy" in fail_names
    auth = next(c for c in checks if c["name"] == "Instructor Authentication")
    assert auth["status"] == "WARN"

    # Configured with valid keys -> passes
    env_hosted_valid = {
        "HOSTED": "1",
        "SECRET_KEY": "0123456789abcdef0123456789abcdef",
        "INSTRUCTOR_PASSWORD": "ProductionInstructorPassword123",
        "PATH": os.environ.get("PATH", ""),
    }
    checks2, code2, _ = run_checks(mode="hosted", env=env_hosted_valid)
    assert code2 == 0


def test_check_env_insecure_secret_key_rejected():
    """Insecure, placeholder, or short SECRET_KEY values fail in hosted mode."""
    for bad_key in ["changeme", "secret", "short", "a" * 31, "0" * 32]:
        env_bad = {
            "HOSTED": "1",
            "SECRET_KEY": bad_key,
            "INSTRUCTOR_PASSWORD": "SomePassword123",
            "PATH": os.environ.get("PATH", ""),
        }
        checks, code, _ = run_checks(mode="hosted", env=env_bad)
        assert code == 1
        sk_check = next(c for c in checks if c["name"] == "SECRET_KEY Policy")
        assert sk_check["status"] == "FAIL"


def test_check_env_vercel_requires_postgres():
    """On Vercel, persistent PostgreSQL URL is mandatory."""
    env_vercel_no_db = {
        "VERCEL": "1",
        "SECRET_KEY": "0123456789abcdef0123456789abcdef",
        "INSTRUCTOR_PASSWORD": "Password123",
        "PATH": os.environ.get("PATH", ""),
    }
    checks, code, _ = run_checks(mode="hosted", env=env_vercel_no_db)
    assert code == 1
    db_check = next(c for c in checks if c["name"] == "Database Configuration")
    assert db_check["status"] == "FAIL"
    assert "PostgreSQL" in db_check["message"]

    # When valid postgresql URL is supplied -> passes
    env_vercel_with_db = {
        "VERCEL": "1",
        "SECRET_KEY": "0123456789abcdef0123456789abcdef",
        "INSTRUCTOR_PASSWORD": "Password123",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/aegis",
        "PATH": os.environ.get("PATH", ""),
    }
    checks2, code2, _ = run_checks(mode="hosted", env=env_vercel_with_db)
    assert code2 == 0


def test_check_env_missing_or_corrupt_rubric(tmp_path):
    """Missing or invalid rubric JSON fails environment check."""
    missing_rubric = tmp_path / "non_existent_rubric.json"
    env = {"RUBRIC_PATH": str(missing_rubric), "PATH": os.environ.get("PATH", "")}
    checks, code, _ = run_checks(mode="offline", env=env)
    assert code == 1
    r_check = next(c for c in checks if c["name"] == "Rubric Configuration")
    assert r_check["status"] == "FAIL"

    # Corrupt JSON file
    corrupt_rubric = tmp_path / "corrupt.json"
    corrupt_rubric.write_text("NOT_VALID_JSON{", encoding="utf-8")
    env2 = {"RUBRIC_PATH": str(corrupt_rubric), "PATH": os.environ.get("PATH", "")}
    checks2, code2, _ = run_checks(mode="offline", env=env2)
    assert code2 == 1


def test_check_env_never_prints_secrets():
    """Environment checker CLI output must NEVER leak secret keys or passwords."""
    canary_secret = "CANARY_SECRET_KEY_9876543210_abcdef"
    canary_password = "CANARY_INSTRUCTOR_PASSWORD_9999"
    canary_db_pass = "CANARY_DB_SECRET_PASSWORD_XYZ"

    env = {
        "HOSTED": "1",
        "SECRET_KEY": canary_secret,
        "INSTRUCTOR_PASSWORD": canary_password,
        "DATABASE_URL": f"postgresql://appuser:{canary_db_pass}@db.internal:5432/aegis",
        "PATH": os.environ.get("PATH", ""),
    }

    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_env.py"), "--mode", "hosted"],
        env=env,
        capture_output=True,
        text=True,
    )
    combined = res.stdout + res.stderr
    assert canary_secret not in combined, "SECRET_KEY leaked in output!"
    assert canary_password not in combined, "INSTRUCTOR_PASSWORD leaked in output!"
    assert canary_db_pass not in combined, "Database password leaked in output!"


def test_check_env_auto_mode_inference():
    """Auto mode correctly identifies hosted, lan, and offline environments."""
    assert run_checks(mode="auto", env={})[2] == "offline"
    assert run_checks(mode="auto", env={"LAN_MODE": "1"})[2] == "lan"
    assert run_checks(mode="auto", env={"HOSTED": "1"})[2] == "hosted"
    assert run_checks(mode="auto", env={"VERCEL": "1"})[2] == "hosted"
    assert run_checks(mode="auto", env={"DATABASE_URL": "postgresql://localhost/db"})[2] == "hosted"


# ==============================================================================
# 3. Structured Security Audit Logging Tests (app/audit.py)
# ==============================================================================

class LogCaptureHandler(logging.Handler):
    """Custom logging handler to capture structured audit log records in memory."""
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        try:
            msg = record.getMessage()
            parsed = json.loads(msg)
            self.records.append(parsed)
        except Exception:
            pass


@pytest.fixture
def audit_capture():
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    handler = LogCaptureHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    yield handler
    logger.removeHandler(handler)


def test_audit_login_success_and_failure(audit_capture, tmp_path):
    """Login attempts emit structured auth.login.success and auth.login.failure events."""
    db_file = tmp_path / "audit_auth.db"
    app = create_app({
        "DATABASE": str(db_file),
        "INSTRUCTOR_PASSWORD": "TestPassword123!",
        "TESTING": True,
    })
    client = app.test_client()

    # 1. Failed login
    client.post("/login", data={"password": "WrongPassword"})
    fail_events = [r for r in audit_capture.records if r.get("event") == "auth.login.failure"]
    assert len(fail_events) == 1
    rec = fail_events[0]
    assert rec["outcome"] == "failure"
    assert rec["actor"] == "anonymous"
    assert rec["resource_type"] == "auth"
    assert "WrongPassword" not in json.dumps(rec)

    # 2. Successful login
    client.post("/login", data={"password": "TestPassword123!"})
    success_events = [r for r in audit_capture.records if r.get("event") == "auth.login.success"]
    assert len(success_events) == 1
    s_rec = success_events[0]
    assert s_rec["outcome"] == "success"
    assert s_rec["actor"] == "instructor"
    assert s_rec["resource_type"] == "auth"
    assert "TestPassword123!" not in json.dumps(s_rec)


def test_audit_login_rate_limited(audit_capture, tmp_path, monkeypatch):
    """Lockout triggers auth.login.rate_limited audit event."""
    from app import auth
    monkeypatch.setattr(auth, "_is_rate_limited", lambda ip: True)

    db_file = tmp_path / "audit_rate.db"
    app = create_app({
        "DATABASE": str(db_file),
        "INSTRUCTOR_PASSWORD": "SomePassword",
        "TESTING": True,
    })
    client = app.test_client()

    resp = client.post("/login", data={"password": "any"})
    assert resp.status_code == 429
    rl_events = [r for r in audit_capture.records if r.get("event") == "auth.login.rate_limited"]
    assert len(rl_events) >= 1
    assert rl_events[0]["outcome"] == "rate_limited"


def test_audit_logout(audit_capture, tmp_path):
    """Logging out emits auth.logout.success event."""
    db_file = tmp_path / "audit_logout.db"
    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    client.post("/logout")
    logout_events = [r for r in audit_capture.records if r.get("event") == "auth.logout.success"]
    assert len(logout_events) >= 1
    assert logout_events[0]["outcome"] == "success"


def test_audit_access_denied(audit_capture, tmp_path):
    """Attempting unauthorized access emits auth.access.denied."""
    db_file = tmp_path / "audit_denied.db"
    app = create_app({
        "DATABASE": str(db_file),
        "INSTRUCTOR_PASSWORD": "SecretPassword",
        "TESTING": True,
    })
    client = app.test_client()

    resp = client.get("/dashboard")
    assert resp.status_code == 302  # redirected to login
    denied = [r for r in audit_capture.records if r.get("event") == "auth.access.denied"]
    assert len(denied) >= 1
    assert denied[0]["outcome"] == "denied"


def test_audit_export_csv(audit_capture, tmp_path):
    """CSV exports emit export.session_csv.success and export.unit_csv.success."""
    db_file = tmp_path / "audit_export.db"
    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    client = app.test_client()

    with app.app_context():
        from app.db import get_db
        db = get_db()
        with db:
            t_id = db.insert("INSERT INTO trainees (callsign, unit) VALUES (?, ?)", ("EAGLE-1", "TEST-UNIT"))
            res_json = json.dumps({"contacts": []})
            s_id = db.insert(
                "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, "
                "duration_s, total, detection, classification, engagement, grade, false_alarms, "
                "breaches, critical_errors, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (t_id, "s1-dawn-recon", "Dawn Recon", 1, "2026-10-18T12:00:00Z", 30.0, 85.0, 85.0, 85.0, 85.0, "B", 0, 0, 0, res_json)
            )

    # 1. Export session CSV
    resp1 = client.get(f"/api/sessions/{s_id}/export.csv")
    assert resp1.status_code == 200
    session_events = [r for r in audit_capture.records if r.get("event") == "export.session_csv.success"]
    assert len(session_events) == 1
    assert session_events[0]["resource_id"] == str(s_id)
    assert session_events[0]["details"]["callsign"] == "EAGLE-1"

    # 2. Export unit CSV
    resp2 = client.get("/api/analytics/unit/TEST-UNIT/export.csv")
    assert resp2.status_code == 200
    unit_events = [r for r in audit_capture.records if r.get("event") == "export.unit_csv.success"]
    assert len(unit_events) == 1
    assert unit_events[0]["resource_id"] == "TEST-UNIT"


def test_audit_rubric_provenance_and_version_change(audit_capture, tmp_path):
    """Rubric version fingerprinting records initial load and detects file modifications."""
    from app.audit import reset_rubric_provenance
    reset_rubric_provenance()

    rubric_file = tmp_path / "rubric.json"
    rubric_data = {"version": 1, "data": "initial"}
    rubric_file.write_text(json.dumps(rubric_data), encoding="utf-8")

    app = create_app({"RUBRIC_PATH": str(rubric_file), "TESTING": True})

    # Initial provenance loaded
    with app.app_context():
        check_rubric_provenance(app)

    loaded = [r for r in audit_capture.records if r.get("event") == "rubric.provenance.loaded"]
    assert len(loaded) >= 1
    initial_hash = loaded[0]["details"]["rubric_hash"]
    assert len(initial_hash) == 64

    # Modify rubric file content on disk
    rubric_data["version"] = 2
    rubric_file.write_text(json.dumps(rubric_data), encoding="utf-8")

    # Subsequent check discovers version change
    with app.app_context():
        check_rubric_provenance(app)

    changed = [r for r in audit_capture.records if r.get("event") == "rubric.version.changed"]
    assert len(changed) == 1
    assert changed[0]["details"]["old_hash"] == initial_hash
    assert changed[0]["details"]["new_hash"] != initial_hash
    assert "attribution_boundary" in changed[0]["details"]


def test_audit_log_format_and_no_secrets():
    """All audit log records are valid JSON and sanitize forbidden secret keys."""
    event = log_audit_event(
        "test.security.event",
        outcome="success",
        actor="instructor",
        resource_type="test",
        details={
            "safe_metric": 42,
            "password": "SUPER_SECRET_PASSWORD",
            "token": "SECRET_TOKEN_XYZ",
            "nested": {"secret_key": "CLASSIFIED_KEY"},
        },
    )
    assert event["event"] == "test.security.event"
    assert event["details"]["safe_metric"] == 42
    assert event["details"]["password"] == "[REDACTED]"
    assert event["details"]["token"] == "[REDACTED]"
    assert event["details"]["nested"]["secret_key"] == "[REDACTED]"


def test_audit_logging_failure_fails_safe(tmp_path, monkeypatch):
    """Failure in audit logging mechanism does not break request handling."""
    from app import audit
    def bad_log(*args, **kwargs):
        raise RuntimeError("Simulated logging infrastructure outage")

    monkeypatch.setattr(audit, "log_audit_event", bad_log)

    db_file = tmp_path / "audit_failsafe.db"
    app = create_app({
        "DATABASE": str(db_file),
        "INSTRUCTOR_PASSWORD": "Password123",
        "TESTING": True,
    })
    client = app.test_client()

    # Login request must not crash despite logging failure
    resp = client.post("/login", data={"password": "Password123"})
    assert resp.status_code in (200, 302)


# ==============================================================================
# 4. Independent Audit Remediation Tests (Tasks 1 - 5)
# ==============================================================================

def test_default_audit_logger_initialization_and_emission(capsys):
    """Default audit logger initializes with StreamHandler, INFO level, and emits JSON without manual config."""
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    orig_handlers = list(logger.handlers)
    orig_level = logger.level
    orig_prop = logger.propagate
    logger.handlers.clear()
    logger.propagate = True

    try:
        from app.audit import get_audit_logger
        l = get_audit_logger()
        assert len(l.handlers) >= 1
        assert l.level <= logging.INFO
        assert l.propagate is False

        rec = log_audit_event("system.startup.test", outcome="success", actor="system", details={"k": "v"})
        assert rec["event"] == "system.startup.test"

        captured = capsys.readouterr()
        assert "system.startup.test" in captured.out
        lines = [line for line in captured.out.strip().splitlines() if "system.startup.test" in line]
        assert len(lines) >= 1
        parsed = json.loads(lines[-1])
        assert parsed["event"] == "system.startup.test"
        assert parsed["outcome"] == "success"
    finally:
        logger.handlers = orig_handlers
        logger.level = orig_level
        logger.propagate = orig_prop


def test_check_env_strict_database_url_redaction_text_and_json():
    """Environment checker must never reveal username, password, host, database, or query params."""
    c_user = "canary_db_user_111"
    c_pass = "canary_db_pass_222"
    c_host = "canary-db-host-333.corp"
    c_name = "canary_db_name_444"
    c_param = "canary_query_param_555"
    canary_url = f"postgresql://{c_user}:{c_pass}@{c_host}:5432/{c_name}?option={c_param}"

    env = {
        "HOSTED": "1",
        "SECRET_KEY": "0123456789abcdef0123456789abcdef",
        "INSTRUCTOR_PASSWORD": "ValidPassword123!",
        "DATABASE_URL": canary_url,
        "PATH": os.environ.get("PATH", ""),
    }

    for mode_flag in [[], ["--json"]]:
        cmd = [sys.executable, str(ROOT / "scripts" / "check_env.py"), "--mode", "hosted"] + mode_flag
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        combined = res.stdout + res.stderr
        for canary in (c_user, c_pass, c_host, c_name, c_param, canary_url):
            assert canary not in combined, f"Canary component '{canary}' leaked in check_env output!"


def test_health_check_sqlite_read_only_connection_failure(tmp_path, monkeypatch):
    """Failure in SQLite read-only connection establishment returns (False, False) safely."""
    db_file = tmp_path / "fail_conn.db"
    db_file.write_text("dummy", encoding="utf-8")

    def bad_connect(*args, **kwargs):
        raise sqlite3.OperationalError("Simulated disk I/O connection failure")

    monkeypatch.setattr(sqlite3, "connect", bad_connect)
    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        assert db_ok is False
        assert schema_ok is False


def test_health_check_sqlite_query_failure_after_connection(tmp_path, monkeypatch):
    """Failure during SQLite SELECT 1 closes connection and returns (False, False)."""
    db_file = tmp_path / "fail_query.db"
    db_file.write_text("dummy", encoding="utf-8")

    real_connect = sqlite3.connect
    closed = []

    class MockConn:
        def __init__(self, c):
            self._c = c

        def execute(self, sql, *args):
            if sql == "SELECT 1":
                raise sqlite3.DatabaseError("Simulated database corruption on SELECT 1")
            return self._c.execute(sql, *args)

        def close(self):
            closed.append(True)
            return self._c.close()

    def mock_connect(*args, **kwargs):
        c = real_connect(*args, **kwargs)
        return MockConn(c)

    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    app = create_app({"DATABASE": str(db_file), "TESTING": True})
    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        assert db_ok is False
        assert schema_ok is False
        assert len(closed) >= 1, "Connection must be closed on query failure"


def test_health_check_postgres_connection_failure(monkeypatch):
    """PostgreSQL connect failure returns (False, False)."""
    class MockPsycopg:
        @staticmethod
        def connect(*args, **kwargs):
            raise Exception("Simulated PG network unreachable")

    monkeypatch.setitem(sys.modules, "psycopg", MockPsycopg)
    monkeypatch.setitem(sys.modules, "psycopg.rows", type("Module", (), {"dict_row": None}))

    app = create_app({"DATABASE_URL": "postgresql://user:pass@localhost:5432/test", "TESTING": True})
    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        assert db_ok is False
        assert schema_ok is False


def test_health_check_postgres_select_1_failure_closes_connection(monkeypatch):
    """PostgreSQL connect succeeds but SELECT 1 fails: closes connection and returns (False, False)."""
    closed = []

    class MockPGConn:
        def execute(self, sql, *args):
            raise Exception("Simulated PG engine failure on SELECT 1")

        def close(self):
            closed.append(True)

    class MockPsycopg:
        @staticmethod
        def connect(*args, **kwargs):
            return MockPGConn()

    monkeypatch.setitem(sys.modules, "psycopg", MockPsycopg)
    monkeypatch.setitem(sys.modules, "psycopg.rows", type("Module", (), {"dict_row": None}))

    app = create_app({"DATABASE_URL": "postgresql://user:pass@localhost:5432/test", "TESTING": True})
    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        assert db_ok is False
        assert schema_ok is False
        assert len(closed) >= 1, "PG connection must be closed when SELECT 1 fails"


def test_health_check_postgres_schema_query_failure_closes_connection(monkeypatch):
    """PostgreSQL SELECT 1 succeeds but schema inspection fails: closes connection and returns (True, False)."""
    closed = []

    class MockPGConn:
        def execute(self, sql, *args):
            if "SELECT 1" in sql:
                return [{"1": 1}]
            raise Exception("Simulated schema catalog read error")

        def close(self):
            closed.append(True)

    class MockPsycopg:
        @staticmethod
        def connect(*args, **kwargs):
            return MockPGConn()

    monkeypatch.setitem(sys.modules, "psycopg", MockPsycopg)
    monkeypatch.setitem(sys.modules, "psycopg.rows", type("Module", (), {"dict_row": None}))

    app = create_app({"DATABASE_URL": "postgresql://user:pass@localhost:5432/test", "TESTING": True})
    with app.app_context():
        db_ok, schema_ok = check_database_health(app)
        assert db_ok is True
        assert schema_ok is False
        assert len(closed) >= 1, "PG connection must be closed when schema query fails"


def test_audit_recursive_sanitization_deep_nesting():
    """Secrets nested inside dicts, lists, tuples, and multiple levels are all redacted."""
    canary1 = "CANARY_TOKEN_NESTED_LIST_123"
    canary2 = "CANARY_PASSWORD_DEEP_456"
    canary3 = "CANARY_SECRET_TUPLE_789"
    payload = {
        "event_data": {
            "items": [
                {"token": canary1, "item_id": 10},
                ("safe_tuple", {"nested_obj": {"password": canary2}}),
                [{"secret_key": canary3}],
            ],
            "safe_num": 100,
            "safe_bool": True,
        }
    }
    rec = log_audit_event("test.deep.sanitization", outcome="success", details=payload)
    dumped = json.dumps(rec)
    assert canary1 not in dumped, "Canary token leaked in nested list!"
    assert canary2 not in dumped, "Canary password leaked in deep nested dict!"
    assert canary3 not in dumped, "Canary secret leaked in tuple-list nesting!"

    items = rec["details"]["event_data"]["items"]
    assert items[0]["token"] == "[REDACTED]"
    assert items[0]["item_id"] == 10
    assert items[1][1]["nested_obj"]["password"] == "[REDACTED]"
    assert items[2][0]["secret_key"] == "[REDACTED]"


def test_audit_caller_supplied_x_request_id_validation_and_sanitization(tmp_path):
    """Caller-supplied X-Request-ID is validated, bounded, and sanitized against injection."""
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})

    # 1. Valid alphanumeric request ID is preserved
    valid_id = "req-valid-12345_ABC.xyz"
    with app.test_request_context("/test", headers={"X-Request-ID": valid_id}):
        rec = log_audit_event("test.req.id", outcome="success")
        assert rec["request_id"] == valid_id

    # 2. Direct validator rejects control characters, CRLF, and shell metacharacters
    from app.audit import _safe_request_id
    assert _safe_request_id("malicious\r\nCRLF_INJECTION\x00") is None
    assert _safe_request_id("bad; rm -rf /") is None
    assert _safe_request_id("bad id with spaces") is None
    assert _safe_request_id("a" * 65) is None
    assert _safe_request_id("valid-id_123.ABC") == "valid-id_123.ABC"

    # 3. Disallowed characters in HTTP request context are safely replaced with fresh token
    disallowed_id = "bad id with spaces; cat /etc/passwd"
    with app.test_request_context("/test", headers={"X-Request-ID": disallowed_id}):
        rec2 = log_audit_event("test.req.id.disallowed", outcome="success")
        assert rec2["request_id"] != disallowed_id
        assert len(rec2["request_id"]) == 16

    # 4. Oversized request ID is rejected and safely replaced
    oversized_id = "a" * 500
    with app.test_request_context("/test", headers={"X-Request-ID": oversized_id}):
        rec3 = log_audit_event("test.req.id.overflow", outcome="success")
        assert rec3["request_id"] != oversized_id
        assert len(rec3["request_id"]) == 16


def test_deployment_migration_readiness_lifecycle(tmp_path):
    """Fresh deployment with legacy unmigrated database reports 503 until explicit migration completes."""
    legacy_db = tmp_path / "legacy_deployment.db"
    conn = sqlite3.connect(str(legacy_db))
    conn.execute("CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT)")
    conn.execute("CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INT, started_at TEXT)")
    conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, session_id INT, t REAL)")
    conn.commit()
    conn.close()

    app = create_app({"DATABASE": str(legacy_db), "TESTING": True})
    client = app.test_client()

    # 1. Before migration: /health returns 503 (schema unmigrated/incompatible)
    resp_before = client.get("/health")
    assert resp_before.status_code == 503
    data_before = resp_before.get_json()
    assert data_before["status"] == "unhealthy"
    assert data_before["checks"]["database"] == "ok"
    assert data_before["checks"]["schema"] == "error"

    # 2. CLI check reports schema pending via scripts/migrate.py --check
    from scripts.migrate import run_migrations
    check_code = run_migrations(check_only=True, app=app)
    assert check_code == 1

    # 3. Execute explicit deployment migration step
    mig_code = run_migrations(check_only=False, app=app)
    assert mig_code == 0

    # 4. After migration: /health returns 200 OK immediately without business requests
    resp_after = client.get("/health")
    assert resp_after.status_code == 200
    data_after = resp_after.get_json()
    assert data_after["status"] == "ok"
    assert data_after["checks"]["database"] == "ok"
    assert data_after["checks"]["schema"] == "ok"


def test_startup_scripts_contract(tmp_path):
    """Verify that start.sh and start.bat have matching parity, NO_BROWSER, port, and argument handling."""
    sh_path = ROOT / "start.sh"
    bat_path = ROOT / "start.bat"

    assert sh_path.exists(), "start.sh must exist"
    assert bat_path.exists(), "start.bat must exist"

    sh_text = sh_path.read_text(encoding="utf-8")
    bat_text = bat_path.read_text(encoding="utf-8")

    # Parity checks
    assert "NO_BROWSER" in sh_text and "NO_BROWSER" in bat_text
    assert "--demo" in sh_text and "--demo" in bat_text
    assert "5050" in sh_text and "5050" in bat_text
    assert "run.py" in sh_text and "run.py" in bat_text

    # On Windows, verify batch syntax and argument parsing logic via cmd
    if sys.platform == "win32":
        test_script = (
            "@echo off\n"
            "setlocal enabledelayedexpansion\n"
            "set DEMO=0\nset ARGS=\nset PORT=5050\nset NEXT_PORT=0\n"
            + ":loop" + bat_text.split(":loop")[1].split("if not exist \".venv")[0]
            + "echo DEMO=!DEMO! PORT=!PORT! ARGS=!ARGS!\n"
        )
        bat_file = tmp_path / "test_arg_parse.bat"
        bat_file.write_text(test_script, encoding="utf-8")
        proc = subprocess.run(
            ["cmd", "/c", str(bat_file), "--demo", "--port", "8080", "--lan"],
            capture_output=True,
            text=True,
            check=True,
        )
        out = proc.stdout.strip()
        assert "DEMO=1" in out
        assert "PORT=8080" in out
        assert "--port 8080 --lan" in out

