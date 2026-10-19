"""Tests for Phase 1: Security and Assessment Integrity.

Covers:
- R-01 / SEC-01: Assessment token lifecycle, hosted enforcement, offline compatibility
- R-02 / SEC-03: Single-use replay protection, transactional uniqueness, idempotency
- R-03: Token binding to exact scenario ID, seed, and parameters
- R-04 / R-05: Hosted fail-closed secret configuration and HTTPS cookie handling
- R-06: Event chronology, prior-mark requirement, and state machine validation
- R-07: Timing validation, early-exit detection, and breach preservation
- R-08: Public write rate limiting and login abuse throttling
- R-09: Safe, observable, and fail-closed database migrations
- R-10: CSV formula injection neutralization with numeric preservation and security headers
"""

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
import pytest

from app import create_app, geometry, scenario as scen, validate_hosted_secret_key
from app.api import (
    _canonical_json,
    _check_write_rate_limit,
    _generate_session_token,
    _params_hash,
    _sanitize_csv_cell,
    _verify_session_token,
    _WRITE_ATTEMPTS,
    MAX_WRITE_TRACKED_IPS,
)
from app.auth import get_client_ip, _FAILED_ATTEMPTS, MAX_TRACKED_IPS
from app.db import SQLiteDB, get_db
from app.scoring import validate_events
from run import build_app_config, parse_args
from test_api import first_hostile, post_session


@pytest.fixture
def test_db(tmp_path):
    return str(tmp_path / "sec_test.db")


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    _WRITE_ATTEMPTS.clear()
    _FAILED_ATTEMPTS.clear()
    yield
    _WRITE_ATTEMPTS.clear()
    _FAILED_ATTEMPTS.clear()


# ---------------------------------------------------------------- R-04 / R-05: Hosted configuration

def test_hosted_fails_closed_when_password_missing(test_db):
    """When HOSTED is true and INSTRUCTOR_PASSWORD is not set, protected routes fail closed (503)."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "INSTRUCTOR_PASSWORD": None,
    })
    c = app.test_client()

    for path in ("/api/trainees", "/api/sessions", "/api/analytics/unit/1%20TRG%20BN"):
        r = c.get(path)
        assert r.status_code == 503, f"{path} should return 503 in misconfigured hosted mode"
        assert "hosted security configuration missing" in r.get_json()["error"]

    r = c.get("/dashboard")
    assert r.status_code == 503
    assert "Hosted deployment requires INSTRUCTOR_PASSWORD" in r.get_data(as_text=True)

    for path in ("/mission", "/sim", "/help", "/api/scenarios", "/api/rubric"):
        assert c.get(path).status_code == 200, f"{path} should be open"


def test_hosted_requires_login_when_password_configured(test_db):
    """When HOSTED is true and INSTRUCTOR_PASSWORD is set, protected routes require login (401 / redirect)."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r = c.get("/api/sessions")
    assert r.status_code == 401
    assert r.get_json()["error"] == "instructor login required"

    r = c.get("/dashboard")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_hosted_refuses_to_start_without_secret_key(test_db):
    """In production hosted mode, a missing or default SECRET_KEY fails startup immediately."""
    with pytest.raises(RuntimeError) as exc_info:
        create_app({
            "DATABASE": test_db,
            "TESTING": False,
            "HOSTED": True,
            "SECRET_KEY": None,
        })
    assert "High-entropy SECRET_KEY must be explicitly configured" in str(exc_info.value)


# ---------------------------------------------------------------- R-08: Login & Write Abuse Controls

def test_login_rate_limiting(test_db):
    """After consecutive failed attempts from the same IP, login returns 429."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    for _ in range(5):
        r = c.post("/login", data={"password": "wrong-password"})
        assert r.status_code in (401, 429)

    r = c.post("/login", data={"password": "wrong-password"})
    assert r.status_code == 429
    assert "Too many failed login attempts" in r.get_data(as_text=True)


# ---------------------------------------------------------------- R-10: CSV Sanitization

def test_csv_formula_injection_sanitization(test_db):
    """Callsigns and units starting with =, +, -, @, \\t are neutralized with a prepended single quote."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "INSTRUCTOR_PASSWORD": None,
    })
    c = app.test_client()

    bad_callsign = "=CMD|' /C CALC'!A0"
    bad_unit = "+SUM(A1:A10)"
    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]

    res = post_session(c, events, callsign=bad_callsign, unit=bad_unit)
    assert res.status_code == 201
    sid = res.get_json()["session_id"]

    r_sess = c.get(f"/api/sessions/{sid}/export.csv")
    assert r_sess.status_code == 200
    csv_text = r_sess.get_data(as_text=True)
    assert f"'{bad_callsign}" in csv_text
    assert f"'{bad_unit}" in csv_text

    # Verify pure negative numbers are preserved and not corrupted
    assert _sanitize_csv_cell(-12.5) == -12.5
    assert _sanitize_csv_cell("-12.5") == "-12.5"
    assert _sanitize_csv_cell("=1+1") == "'=1+1"


# ---------------------------------------------------------------- R-01: Token Lifecycle & Hosted Enforcement

def test_assessment_token_mandatory_in_hosted_mode(test_db):
    """In hosted mode, submitting a session without assessment_token is rejected with 403."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "test-key-12345",
        "INSTRUCTOR_PASSWORD": "alpha-pass",
    })
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    body = {
        "callsign": "BRAVO",
        "unit": "2 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": events,
        "ended_t": 150.0,
    }

    # Missing token -> 403 Forbidden
    r_no_token = c.post("/api/sessions", json=body)
    assert r_no_token.status_code == 403
    assert "assessment_token is required in hosted mode" in r_no_token.get_json()["error"]

    # Valid token obtained from /api/session/start -> 201 Created
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    token = r_start.get_json()["assessment_token"]
    assert token is not None

    # Wait or simulate reasonable elapsed time so timing check doesn't flag fast-forward
    conn = sqlite3.connect(test_db)
    conn.execute("UPDATE assessment_runs SET started_at = ? WHERE run_id = ?", (time.time() - 30.0, r_start.get_json()["run_id"]))
    conn.commit()
    conn.close()

    r_with_token = c.post("/api/sessions", json=dict(body, assessment_token=token))
    assert r_with_token.status_code == 201


def test_offline_mode_preserves_optional_token(test_db):
    """In offline workstation mode, tokens are optional and sessions submit without friction."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": False,
        "INSTRUCTOR_PASSWORD": None,
    })
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    r = c.post("/api/sessions", json={
        "callsign": "OFFLINE",
        "unit": "SOLO",
        "scenario_id": "s1-dawn-recon",
        "events": events,
    })
    assert r.status_code == 201


# ---------------------------------------------------------------- R-03: Seed & Scenario Parameter Binding

def test_token_seed_mismatch_rejected(test_db):
    """A token issued for one seed is rejected when submitted against a different seed."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "SECRET_KEY": "test-key-seed-binding",
    })
    c = app.test_client()

    with app.app_context():
        # Issue token for seed 999
        token_seed_999 = _generate_session_token("s1-dawn-recon", 999)

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]

    # Submit against standard scenario (seed 0)
    r = c.post("/api/sessions", json={
        "callsign": "CHARLIE",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token_seed_999,
        "events": events,
    })
    assert r.status_code == 403
    assert "invalid or expired assessment_token" in r.get_json()["error"]


def test_token_scenario_id_mismatch_rejected(test_db):
    """A token issued for s1-dawn-recon is rejected when submitted for s2-night-loiter."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "SECRET_KEY": "test-key-id-binding",
    })
    c = app.test_client()

    with app.app_context():
        token_s1 = _generate_session_token("s1-dawn-recon", 0)

    r = c.post("/api/sessions", json={
        "callsign": "DELTA",
        "unit": "1 TRG",
        "scenario_id": "s2-night-loiter",
        "assessment_token": token_s1,
        "events": [],
    })
    assert r.status_code == 403
    assert "invalid or expired assessment_token" in r.get_json()["error"]


# ---------------------------------------------------------------- R-02: Single-Use Replay Protection & Idempotency

def test_token_single_use_replay_protection(test_db):
    """A token can only be consumed once; reuse with a different client_id is rejected with 409."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "SECRET_KEY": "test-key-replay-prot",
    })
    c = app.test_client()

    sc_res = c.get("/api/scenario?id=s1-dawn-recon&token=1")
    token = sc_res.get_json()["assessment_token"]

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]

    body1 = {
        "callsign": "ECHO",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "client_id": "client-uuid-001",
        "assessment_token": token,
        "events": events,
    }

    # First submission succeeds (201)
    r1 = c.post("/api/sessions", json=body1)
    assert r1.status_code == 201
    sid1 = r1.get_json()["session_id"]

    # Replay with same client_id and exact payload returns 200 idempotent original session
    r2 = c.post("/api/sessions", json=body1)
    assert r2.status_code == 200
    assert r2.get_json()["session_id"] == sid1

    # Conflict: Replay with same client_id but altered payload is rejected (409)
    body_conflict = dict(body1, events=[])
    r_conf = c.post("/api/sessions", json=body_conflict)
    assert r_conf.status_code == 409
    assert "client_id conflict" in r_conf.get_json()["error"]

    # Replay: Attempt to consume the same token with a different client_id is rejected (409)
    body_replay = dict(body1, client_id="client-uuid-002")
    r_replay = c.post("/api/sessions", json=body_replay)
    assert r_replay.status_code == 409
    assert "assessment_token has already been consumed" in r_replay.get_json()["error"]


# ---------------------------------------------------------------- R-06: Event Chronology & State Machine

def test_classification_before_mark_rejected(test_db):
    """A classify event on an unmarked contact violates the state machine and is rejected."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    # Trainee classifies contact without marking it first
    bad_events = [
        {"t": c_hostile["spawn_t"] + 2, "type": "classify", "contact_id": c_hostile["id"], "data": {"class": "RECON_UAS"}}
    ]

    r = c.post("/api/sessions", json={
        "callsign": "FOXTROT",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": bad_events,
    })
    assert r.status_code == 400
    assert "occurred before contact was marked" in r.get_json()["error"]


def test_action_before_spawn_rejected(test_db):
    """Events occurring before a contact spawns are rejected."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    # Contact spawns at spawn_t; attempt classification before spawn
    bad_events = [
        {"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}},
        {"t": c_hostile["spawn_t"] - 5.0, "type": "classify", "contact_id": c_hostile["id"], "data": {"class": "RECON_UAS"}}
    ]

    r = c.post("/api/sessions", json={
        "callsign": "GOLF",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": bad_events,
    })
    assert r.status_code == 400
    assert "occurred before spawn" in r.get_json()["error"]


# ---------------------------------------------------------------- R-07: Timing Bounds & Early Exit Semantics

def test_manipulated_ended_t_bounds(test_db):
    """Malicious or invalid ended_t bounds are rejected with 400."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    c = app.test_client()

    # Negative ended_t
    r_neg = c.post("/api/sessions", json={
        "callsign": "HOTEL",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": [],
        "ended_t": -10,
    })
    assert r_neg.status_code == 400

    # Impossibly large ended_t
    r_big = c.post("/api/sessions", json={
        "callsign": "HOTEL",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": [],
        "ended_t": 999999,
    })
    assert r_big.status_code == 400


def test_early_exit_marked_interrupted(test_db):
    """A session ended significantly before duration_s is marked as interrupted."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    c = app.test_client()

    r = c.post("/api/sessions", json={
        "callsign": "INDIA",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": [],
        "ended_t": 20.0,
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["session_status"] == "interrupted"


# ---------------------------------------------------------------- R-09: Safe, Observable Migrations

def test_migrations_create_version_table_and_indexes(test_db):
    """Database initialization runs migrations in order and creates schema_migrations."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    with app.app_context():
        db = get_db()
        # Verify schema_migrations table exists and has versions 1, 2, 3, and 4
        rows = db.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
        assert len(rows) == 4
        assert rows[0]["version"] == 1
        assert rows[1]["version"] == 2
        assert rows[2]["version"] == 3
        assert rows[3]["version"] == 4

        # Verify unique partial indexes exist and are verified unique in SQLite pragma
        idx_info = {r[1]: r for r in db.execute("PRAGMA index_list(sessions)").fetchall()}
        assert "idx_sessions_client" in idx_info and idx_info["idx_sessions_client"][2] == 1
        assert "idx_sessions_nonce" in idx_info and idx_info["idx_sessions_nonce"][2] == 1


def test_security_headers_present(test_db):
    """Responses contain required security headers."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
    })
    c = app.test_client()

    for path in ("/mission", "/api/rubric", "/help"):
        r = c.get(path)
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
        assert r.headers.get("X-Frame-Options") == "DENY"
        assert r.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "default-src 'self'" in r.headers.get("Content-Security-Policy", "")


def test_token_tampered_signature_rejected(test_db):
    """An assessment token with a tampered signature is rejected."""
    app = create_app({"DATABASE": test_db, "TESTING": True, "SECRET_KEY": "sig-test-key"})
    c = app.test_client()
    with app.app_context():
        valid_token = _generate_session_token("s1-dawn-recon", 0)
    parts = valid_token.split(":")
    parts[-1] = "0" * len(parts[-1])
    tampered_token = ":".join(parts)

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    r = c.post("/api/sessions", json={
        "callsign": "TAMPER",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": tampered_token,
        "events": events,
    })
    assert r.status_code == 403
    assert "invalid or expired assessment_token" in r.get_json()["error"]


def test_token_expired_rejected(test_db):
    """An assessment token with a timestamp older than 86400s is rejected."""
    app = create_app({"DATABASE": test_db, "TESTING": True, "SECRET_KEY": "exp-test-key"})
    c = app.test_client()
    secret = b"exp-test-key"
    old_ts = int(time.time()) - 90000
    nonce = "abc123def456"
    msg = f"s1-dawn-recon:0:none:{old_ts}:{nonce}"
    sig = hmac.new(secret, msg.encode(), hashlib.sha256).hexdigest()
    expired_token = f"{msg}:{sig}"

    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    r = c.post("/api/sessions", json={
        "callsign": "EXPIRED",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": expired_token,
        "events": events,
    })
    assert r.status_code == 403
    assert "invalid or expired assessment_token" in r.get_json()["error"]


def test_token_parameter_mismatch_rejected(test_db):
    """A token issued with specific parameters is rejected when parameters change,
    with scenario identity and seed held strictly constant."""
    app = create_app({"DATABASE": test_db, "TESTING": True, "SECRET_KEY": "param-test-key"})
    c = app.test_client()

    # Case 1: Procedural scenario where scenario ID ("proc-42-d1") and seed (42) are identical,
    # but a non-id parameter (terrain) differs ("rural" vs "urban").
    scen_rural = scen.get_scenario("proc-42-d1", {"seed": 42, "difficulty": 1, "terrain": "rural"})
    scen_urban = scen.get_scenario("proc-42-d1", {"seed": 42, "difficulty": 1, "terrain": "urban"})
    assert scen_rural["id"] == scen_urban["id"] == "proc-42-d1"
    assert scen_rural["seed"] == scen_urban["seed"] == 42
    assert scen_rural["params"] != scen_urban["params"]

    with app.app_context():
        # Token issued for rural parameters
        token_rural = _generate_session_token("proc-42-d1", 42, scen_rural["params"])

    # Submitting with urban parameters: scenario ID and seed match, but parameter mismatch triggers rejection
    r = c.post("/api/sessions", json={
        "callsign": "PARAM-TEST",
        "unit": "1 TRG",
        "scenario_id": "proc-42-d1",
        "params": {"seed": 42, "difficulty": 1, "terrain": "urban"},
        "assessment_token": token_rural,
        "events": [],
    })
    assert r.status_code == 403
    assert "invalid or expired assessment_token" in r.get_json()["error"]

    # Case 2: Wildcard "none" elimination test:
    # A token generated with params=None (hash "none") is rejected when submitted for a parameterized scenario
    with app.app_context():
        token_no_params = _generate_session_token("proc-42-d1", 42, None)
        valid, _ = _verify_session_token(token_no_params, "proc-42-d1", 42, scen_rural["params"])
        assert valid is False  # In defective code, this returned True due to "none" wildcard!

    r_none = c.post("/api/sessions", json={
        "callsign": "PARAM-NONE",
        "unit": "1 TRG",
        "scenario_id": "proc-42-d1",
        "params": {"seed": 42, "difficulty": 1, "terrain": "rural"},
        "assessment_token": token_no_params,
        "events": [],
    })
    assert r_none.status_code == 403
    assert "invalid or expired assessment_token" in r_none.get_json()["error"]

    # Case 3: Token issued with params rejected when submitted for unparameterized scenario
    with app.app_context():
        valid_rev, _ = _verify_session_token(token_rural, "proc-42-d1", 42, None)
        assert valid_rev is False

    # Case 4: Correctly matching parameters accepted
    with app.app_context():
        valid_ok, nonce_ok = _verify_session_token(token_rural, "proc-42-d1", 42, scen_rural["params"])
        assert valid_ok is True and nonce_ok is not None


def test_unknown_contact_event_rejected(test_db):
    """Events referencing a contact not present in the scenario are rejected."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    bad_events = [
        {"t": 10.0, "type": "classify", "contact_id": "phantom-drone-999", "data": {"class": "RECON_UAS"}}
    ]
    r = c.post("/api/sessions", json={
        "callsign": "PHANTOM",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": bad_events,
    })
    assert r.status_code == 400
    assert "needs a contact_id from this scenario" in r.get_json()["error"]


def test_response_without_mark_rejected(test_db):
    """An engagement response event on an unmarked contact is rejected."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    bad_events = [
        {"t": c_hostile["spawn_t"] + 5, "type": "respond", "contact_id": c_hostile["id"], "data": {"response": "JAM"}}
    ]
    r = c.post("/api/sessions", json={
        "callsign": "UNMARKED-RESP",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": bad_events,
    })
    assert r.status_code == 400
    assert "occurred before contact was marked" in r.get_json()["error"]


def test_lan_mode_policy_enforcement(test_db):
    """In LAN mode without instructor password, protected routes fail closed with 503."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "LAN_MODE": True,
        "INSTRUCTOR_PASSWORD": None,
    })
    c = app.test_client()
    r = c.get("/dashboard")
    assert r.status_code == 503
    assert "Hosted deployment requires INSTRUCTOR_PASSWORD" in r.get_data(as_text=True)


def test_https_resolved_secure_cookies_and_hsts(test_db):
    """When configured with HTTPS, cookies have Secure attribute and HSTS header is present."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "https-test-secret-key-1234",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
        "HTTPS_PROXIED": "true",
    })
    c = app.test_client()
    r = c.get("/api/rubric")
    assert r.status_code == 200
    assert "Strict-Transport-Security" in r.headers
    assert "max-age=" in r.headers["Strict-Transport-Security"]


def test_write_rate_limiting_hosted(test_db):
    """Hosted write rate limiter limits rapid creation of sessions or trainees."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "rate-limit-secret-key-1234",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    for _ in range(60):
        c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    r_exceeded = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_exceeded.status_code == 429
    assert "rate limit exceeded" in r_exceeded.get_json()["error"]


def test_csv_comprehensive_edge_cases():
    """_sanitize_csv_cell comprehensively protects against formula execution while preserving numbers."""
    assert _sanitize_csv_cell("=1+1") == "'=1+1"
    assert _sanitize_csv_cell("+1+1") == "'+1+1"
    assert _sanitize_csv_cell("@SUM(A1)") == "'@SUM(A1)"
    assert _sanitize_csv_cell("\t=CMD") == "'\t=CMD"
    assert _sanitize_csv_cell("\r=CMD") == "'\r=CMD"
    assert _sanitize_csv_cell("  =2+2") == "'  =2+2"
    assert _sanitize_csv_cell("  -3*4") == "'  -3*4"
    assert _sanitize_csv_cell(0) == 0
    assert _sanitize_csv_cell(42) == 42
    assert _sanitize_csv_cell(-15) == -15
    assert _sanitize_csv_cell("-15") == "-15"
    assert _sanitize_csv_cell("-15.75") == "-15.75"
    assert _sanitize_csv_cell("  -15.75") == "  -15.75"
    assert _sanitize_csv_cell("") == ""
    assert _sanitize_csv_cell("ALPHA") == "ALPHA"
    assert _sanitize_csv_cell("1 TRG BN") == "1 TRG BN"
    assert _sanitize_csv_cell("ड्रोन सिम्युलेटर") == "ड्रोन सिम्युलेटर"


def test_events_after_ended_t_rejected(test_db):
    """Events occurring after the accepted session end time are rejected with 400."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    c_hostile = first_hostile("s1-dawn-recon")
    # Session ends at 20.0s, mark is at 10.0s, but classify event is at 25.0s (> 20.0 + 2.0 tolerance)
    events = [
        {"t": c_hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": c_hostile["id"], "data": {}},
        {"t": 25.0, "type": "classify", "contact_id": c_hostile["id"], "data": {"class": "RECON_UAS"}}
    ]
    r = c.post("/api/sessions", json={
        "callsign": "LATE-EV",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "ended_t": 20.0,
        "events": events,
    })
    assert r.status_code == 400
    assert "t must be a number between 0 and" in r.get_json()["error"]


def test_contact_lifecycle_chronology_enforced(test_db):
    """Actions submitted after a contact has departed are rejected."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    scen_data = scen.get_scenario("s1-dawn-recon")
    c_target = scen_data["contacts"][0]
    cid = c_target["id"]
    spawn_t = c_target["spawn_t"]
    end_t = geometry.end_time(c_target)

    # 1. Action after contact end time
    late_events = [
        {"t": spawn_t + 1.0, "type": "mark", "contact_id": cid, "data": {}},
        {"t": end_t + 5.0, "type": "classify", "contact_id": cid, "data": {"class": "RECON_UAS"}},
    ]
    r_late = c.post("/api/sessions", json={
        "callsign": "CHRONO-LATE",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": late_events,
    })
    assert r_late.status_code == 400
    assert "occurred after contact left area" in r_late.get_json()["error"]

    # 2. Response after contact end time
    late_resp = [
        {"t": spawn_t + 1.0, "type": "mark", "contact_id": cid, "data": {}},
        {"t": end_t + 5.0, "type": "respond", "contact_id": cid, "data": {"response": "JAM"}},
    ]
    r_resp_late = c.post("/api/sessions", json={
        "callsign": "CHRONO-RESP-LATE",
        "unit": "1 TRG",
        "scenario_id": "s1-dawn-recon",
        "events": late_resp,
    })
    assert r_resp_late.status_code == 400
    assert "occurred after contact left area" in r_resp_late.get_json()["error"]


def test_adversarial_early_exit_cannot_evade_breach(test_db):
    """An adversarial early exit cannot evade breach penalties for inbound threats,
    and sets grade INCOMPLETE."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    # Hostile drone in s2-night-loiter spawns at 12s and breaches the inner ring at ~110s
    # Trainee marks at t=15, does not neutralize, and attempts early exit at t=30s
    c_hostile = first_hostile("s2-night-loiter")
    events = [{"t": c_hostile["spawn_t"] + 3.0, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]

    r_early = c.post("/api/sessions", json={
        "callsign": "EVADER",
        "unit": "1 TRG",
        "scenario_id": "s2-night-loiter",
        "ended_t": 30.0,
        "events": events,
    })
    assert r_early.status_code == 201
    data = r_early.get_json()

    assert data["session_status"] == "interrupted"
    assert data["grade"] == "INCOMPLETE"
    assert data["penalties"]["inbound_unresolved"] >= 1
    assert data["penalties"]["inbound_unresolved_points"] >= 10


def test_legacy_database_migration_with_nonunique_index(tmp_path):
    """A legacy SQLite database with a non-unique index and applied v1/v2 migrations
    is safely upgraded by migration 3 to enforce unique constraints without data loss."""
    legacy_db_path = str(tmp_path / "legacy_trainer.db")
    conn = sqlite3.connect(legacy_db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Set up legacy schema without later columns
    conn.executescript("""
        CREATE TABLE trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT NOT NULL,
            unit TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
            UNIQUE (callsign, unit)
        );
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER NOT NULL REFERENCES trainees (id),
            scenario_id TEXT NOT NULL,
            scenario_name TEXT NOT NULL,
            seed INTEGER NOT NULL,
            params TEXT,
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
            result TEXT NOT NULL,
            client_id TEXT,
            assessment_nonce TEXT,
            request_hash TEXT
        );
        CREATE TABLE schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        -- Simulate legacy NON-UNIQUE index on client_id
        CREATE INDEX idx_sessions_client ON sessions (client_id);
        INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');
        INSERT INTO schema_migrations (version, name) VALUES (2, 'session_integrity_and_replay_protection');
    """)

    # Insert existing legitimate trainee and session records
    conn.execute("INSERT INTO trainees (callsign, unit) VALUES ('VETERAN', '10 PARA')")
    trainee_id = conn.execute("SELECT id FROM trainees WHERE callsign = 'VETERAN'").fetchone()[0]
    conn.execute("""
        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                              total, detection, classification, engagement, grade, false_alarms,
                              breaches, critical_errors, result, client_id, assessment_nonce, request_hash)
        VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '2026-01-01T00:00:00Z', 120.0,
                85.0, 80.0, 90.0, 85.0, 'B', 0, 0, 0, '{}', 'legacy-client-uuid-001', 'legacy-nonce-001', 'hash1')
    """, (trainee_id,))
    conn.commit()
    conn.close()

    # Now run SQLiteDB.init_schema() which triggers migration 3
    db = SQLiteDB(legacy_db_path)
    db.init_schema()

    # Verify migrations 3 and 4 were applied
    rows = db.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
    assert [r[0] for r in rows] == [1, 2, 3, 4]

    # Inspect PRAGMA index_list to verify both indexes are actually UNIQUE (column 2 == 1)
    indexes = {r[1]: r for r in db.execute("PRAGMA index_list(sessions)").fetchall()}
    assert "idx_sessions_client" in indexes
    assert indexes["idx_sessions_client"][2] == 1  # 1 means UNIQUE
    assert "idx_sessions_nonce" in indexes
    assert indexes["idx_sessions_nonce"][2] == 1  # 1 means UNIQUE

    # Verify existing trainee and session records are intact
    saved_sess = db.execute("SELECT * FROM sessions WHERE client_id = 'legacy-client-uuid-001'").fetchone()
    assert saved_sess is not None
    assert saved_sess["total"] == 85.0

    # Verify duplicate client_id cannot be inserted
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("""
            INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                                  total, detection, classification, engagement, grade, false_alarms,
                                  breaches, critical_errors, result, client_id, assessment_nonce)
            VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '2026-01-01T01:00:00Z', 120.0,
                    90.0, 90.0, 90.0, 90.0, 'A', 0, 0, 0, '{}', 'legacy-client-uuid-001', 'nonce-new-002')
        """, (trainee_id,))

    # Verify duplicate assessment_nonce cannot be inserted
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("""
            INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                                  total, detection, classification, engagement, grade, false_alarms,
                                  breaches, critical_errors, result, client_id, assessment_nonce)
            VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '2026-01-01T01:00:00Z', 120.0,
                    90.0, 90.0, 90.0, 90.0, 'A', 0, 0, 0, '{}', 'client-new-002', 'legacy-nonce-001')
        """, (trainee_id,))

    # Verify multiple NULL client_id and assessment_nonce values remain permissible
    db.execute("""
        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                              total, detection, classification, engagement, grade, false_alarms,
                              breaches, critical_errors, result, client_id, assessment_nonce)
        VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '2026-01-01T02:00:00Z', 120.0,
                90.0, 90.0, 90.0, 90.0, 'A', 0, 0, 0, '{}', NULL, NULL)
    """, (trainee_id,))
    db.execute("""
        INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                              total, detection, classification, engagement, grade, false_alarms,
                              breaches, critical_errors, result, client_id, assessment_nonce)
        VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '2026-01-01T03:00:00Z', 120.0,
                90.0, 90.0, 90.0, 90.0, 'A', 0, 0, 0, '{}', NULL, NULL)
    """, (trainee_id,))
    db.close()


def test_legacy_database_migration_with_duplicate_records_aborts_safely(tmp_path):
    """If existing duplicate records prevent uniqueness, migration 3 aborts with an
    actionable RuntimeError without deleting or modifying records."""
    dup_db_path = str(tmp_path / "dup_trainer.db")
    conn = sqlite3.connect(dup_db_path)
    conn.executescript("""
        CREATE TABLE trainees (id INTEGER PRIMARY KEY, callsign TEXT, unit TEXT);
        CREATE TABLE sessions (id INTEGER PRIMARY KEY, trainee_id INTEGER, scenario_id TEXT,
                               scenario_name TEXT, seed INTEGER, started_at TEXT, duration_s REAL,
                               total REAL, detection REAL, classification REAL, engagement REAL,
                               grade TEXT, false_alarms INTEGER, breaches INTEGER,
                               critical_errors INTEGER, result TEXT, client_id TEXT, assessment_nonce TEXT,
                               request_hash TEXT);
        CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT, applied_at TEXT);
        INSERT INTO schema_migrations VALUES (1, 'initial_schema', '2026-01-01');
        INSERT INTO schema_migrations VALUES (2, 'session_integrity_and_replay_protection', '2026-01-01');
        INSERT INTO trainees VALUES (1, 'PILOT', '1 TRG');
        -- Two sessions sharing the same client_id
        INSERT INTO sessions (id, trainee_id, scenario_id, scenario_name, seed, started_at, duration_s,
                              total, detection, classification, engagement, grade, false_alarms,
                              breaches, critical_errors, result, client_id)
        VALUES (1, 1, 's1', 'S1', 0, '2026-01-01', 120, 80, 80, 80, 80, 'B', 0, 0, 0, '{}', 'shared-client-id'),
               (2, 1, 's1', 'S1', 0, '2026-01-01', 120, 85, 85, 85, 85, 'B', 0, 0, 0, '{}', 'shared-client-id');
    """)
    conn.commit()
    conn.close()

    db = SQLiteDB(dup_db_path)
    with pytest.raises(RuntimeError) as exc_info:
        db.init_schema()

    assert "duplicate client_id found in sessions" in str(exc_info.value)

    # Verify records were NOT corrupted or deleted
    conn2 = sqlite3.connect(dup_db_path)
    count = conn2.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    conn2.close()
    assert count == 2


def test_run_py_cli_and_lan_opt_in_configuration(test_db):
    """Command-line options in run.py correctly configure offline, LAN, and unauthenticated LAN modes,
    propagating credentials and validating signing keys."""
    strong_key = "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90"

    # 1. Default workstation mode
    args_default = parse_args([])
    assert args_default.lan is False
    assert args_default.port == 5050
    cfg_default = build_app_config(args_default, env={})
    assert cfg_default == {}

    # 2. --lan without password or opt-in raises ValueError
    args_lan_locked = parse_args(["--lan"])
    with pytest.raises(ValueError) as exc_info:
        build_app_config(args_lan_locked, env={})
    assert "SECURITY ERROR: --lan exposes AEGIS" in str(exc_info.value)

    # 3. --lan with instructor password but no SECRET_KEY raises ValueError
    args_lan_pass = parse_args(["--lan", "--port", "5055"])
    with pytest.raises(ValueError) as exc_info:
        build_app_config(args_lan_pass, env={"INSTRUCTOR_PASSWORD": "alpha-pass-123"})
    assert "A strong SECRET_KEY must be configured" in str(exc_info.value)

    # 4. --lan with weak/placeholder SECRET_KEY raises ValueError
    with pytest.raises(ValueError) as exc_info:
        build_app_config(args_lan_pass, env={
            "INSTRUCTOR_PASSWORD": "alpha-pass-123",
            "SECRET_KEY": "changeme",
        })
    assert "Invalid SECRET_KEY for LAN deployment" in str(exc_info.value)

    # 5. --lan with valid instructor password and strong SECRET_KEY
    cfg_lan_pass = build_app_config(args_lan_pass, env={
        "INSTRUCTOR_PASSWORD": "alpha-pass-123",
        "SECRET_KEY": strong_key,
    })
    assert cfg_lan_pass["LAN_MODE"] is True
    assert cfg_lan_pass["INSTRUCTOR_PASSWORD"] == "alpha-pass-123"
    assert cfg_lan_pass["SECRET_KEY"] == strong_key

    # 6. Verify live app construction and protected route flow using the generated LAN config
    lan_app = create_app(dict(cfg_lan_pass, DATABASE=test_db, TESTING=True))
    c_lan = lan_app.test_client()

    # Unauthenticated access to /api/sessions rejected with 401
    r_unauth = c_lan.get("/api/sessions")
    assert r_unauth.status_code == 401

    # Login with configured password succeeds and allows access
    r_login = c_lan.post("/login", data={"password": "alpha-pass-123"})
    assert r_login.status_code == 302
    r_auth = c_lan.get("/api/sessions")
    assert r_auth.status_code == 200

    # 7. --lan with explicit unauthenticated LAN opt-in requires strong SECRET_KEY
    args_lan_open = parse_args(["--lan", "--allow-unauthenticated-lan"])
    with pytest.raises(ValueError) as exc_info:
        build_app_config(args_lan_open, env={})
    assert "A strong SECRET_KEY must be configured" in str(exc_info.value)

    cfg_lan_open = build_app_config(args_lan_open, env={"SECRET_KEY": strong_key})
    assert cfg_lan_open == {"LAN_MODE": True, "ALLOW_UNAUTHENTICATED_LAN": True, "SECRET_KEY": strong_key}

    # 8. Verify unauthenticated LAN does not override HOSTED security
    hosted_lan_app = create_app({
        "TESTING": True,
        "HOSTED": True,
        "LAN_MODE": True,
        "ALLOW_UNAUTHENTICATED_LAN": True,
        "INSTRUCTOR_PASSWORD": None,
    })
    c = hosted_lan_app.test_client()
    assert c.get("/api/sessions").status_code == 503


# ---------------------------------------------------------------- Phase 1.1: Assessment Idempotency & Deterministic Fingerprinting

def test_idempotent_retry_returns_original_session(test_db):
    """An identical retry with the same client_id returns the original saved session (200 OK)."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    hostile = first_hostile("s1-dawn-recon")
    events = [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ]
    payload = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "client_id": "client-uuid-001",
        "events": events,
        "ended_t": 120.0,
    }

    # Initial submission -> 201 Created
    r1 = c.post("/api/sessions", json=payload)
    assert r1.status_code == 201
    s1 = r1.get_json()

    # Identical retry -> 200 OK, same session_id and score
    r2 = c.post("/api/sessions", json=payload)
    assert r2.status_code == 200
    s2 = r2.get_json()
    assert s2["session_id"] == s1["session_id"]
    assert s2["total"] == s1["total"]


def test_client_id_reuse_with_changed_events_rejected(test_db):
    """Submitting with the same client_id but altered events is rejected with 409 Conflict."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    hostile = first_hostile("s1-dawn-recon")
    events1 = [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
    ]
    payload1 = {
        "callsign": "BRAVO-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "client_id": "client-uuid-002",
        "events": events1,
        "ended_t": 120.0,
    }
    r1 = c.post("/api/sessions", json=payload1)
    assert r1.status_code == 201

    # Altered events with same client_id -> 409 Conflict
    events2 = [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ]
    payload2 = dict(payload1, events=events2)
    r2 = c.post("/api/sessions", json=payload2)
    assert r2.status_code == 409
    assert "client_id conflict: payload does not match existing session" in r2.get_json()["error"]


def test_client_id_reuse_with_changed_parameters_rejected(test_db):
    """Submitting with the same client_id and events but different scenario parameters is rejected with 409."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    payload1 = {
        "callsign": "CHARLIE-1",
        "unit": "1 TRG BN",
        "scenario_id": "procedural",
        "params": {"seed": 100, "difficulty": 1, "terrain": "rural"},
        "client_id": "client-uuid-003",
        "events": [],
        "ended_t": 180.0,
    }
    r1 = c.post("/api/sessions", json=payload1)
    assert r1.status_code == 201

    # Same client_id and events, but changed difficulty and terrain -> 409 Conflict
    payload2 = {
        "callsign": "CHARLIE-1",
        "unit": "1 TRG BN",
        "scenario_id": "procedural",
        "params": {"seed": 100, "difficulty": 2, "terrain": "urban"},
        "client_id": "client-uuid-003",
        "events": [],
        "ended_t": 180.0,
    }
    r2 = c.post("/api/sessions", json=payload2)
    assert r2.status_code == 409
    assert "client_id conflict: payload does not match existing session" in r2.get_json()["error"]


def test_idempotent_retry_with_parameter_key_order_variation(test_db):
    """Parameter dictionaries with different key insertion order yield identical canonical fingerprint."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    p1 = {"difficulty": 1, "terrain": "rural", "seed": 77}
    p2 = {"seed": 77, "terrain": "rural", "difficulty": 1}

    payload1 = {
        "callsign": "DELTA-1",
        "unit": "1 TRG BN",
        "scenario_id": "procedural",
        "params": p1,
        "client_id": "client-uuid-004",
        "events": [],
        "ended_t": 180.0,
    }
    r1 = c.post("/api/sessions", json=payload1)
    assert r1.status_code == 201

    payload2 = dict(payload1, params=p2)
    r2 = c.post("/api/sessions", json=payload2)
    assert r2.status_code == 200
    assert r2.get_json()["session_id"] == r1.get_json()["session_id"]


# ---------------------------------------------------------------- Phase 1.1: /api/session/start Token Compatibility

def test_session_start_scripted_token_submission_integration(test_db):
    """Token issued by /api/session/start for scripted scenario succeeds upon hosted submission."""
    secret = "a-very-secure-hosted-secret-key-32-chars-long"
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": secret,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # 1. Start session
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    start_data = r_start.get_json()
    assert start_data["scenario_id"] == "s1-dawn-recon"
    assert "assessment_token" in start_data

    # 2. Submit session with issued token
    hostile = first_hostile("s1-dawn-recon")
    events = [{"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}}]
    r_submit = c.post("/api/sessions", json={
        "callsign": "ECHO-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": start_data["assessment_token"],
        "client_id": "client-uuid-start-1",
        "events": events,
        "ended_t": 120.0,
    })
    assert r_submit.status_code == 201


def test_session_start_procedural_partial_params_integration(test_db):
    """Token issued by /api/session/start for procedural scenario with partial params succeeds upon hosted submission."""
    secret = "a-very-secure-hosted-secret-key-32-chars-long"
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": secret,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # 1. Start procedural session with partial parameters
    r_start = c.post("/api/session/start", json={
        "scenario_id": "procedural",
        "seed": 42,
        "params": {"difficulty": 3, "terrain": "urban"},
    })
    assert r_start.status_code == 201
    start_data = r_start.get_json()
    assert start_data["scenario_id"] == "proc-42-d3"
    assert start_data["seed"] == 42
    assert start_data["params"]["terrain"] == "urban"
    assert "assessment_token" in start_data

    # 2. Submit session using the resolved scenario_id, canonical params, and token
    r_submit = c.post("/api/sessions", json={
        "callsign": "FOXTROT-1",
        "unit": "1 TRG BN",
        "scenario_id": start_data["scenario_id"],
        "params": start_data["params"],
        "assessment_token": start_data["assessment_token"],
        "client_id": "client-uuid-start-2",
        "events": [],
        "ended_t": 240.0,
    })
    assert r_submit.status_code == 201


def test_session_start_tampered_params_rejected_on_submit(test_db):
    """Tampering with parameters after token issuance from /api/session/start is rejected (403)."""
    secret = "a-very-secure-hosted-secret-key-32-chars-long"
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": secret,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={
        "scenario_id": "procedural",
        "seed": 42,
        "params": {"difficulty": 3, "terrain": "urban"},
    })
    start_data = r_start.get_json()

    # Tampering: change difficulty from 3 to 1
    tampered_params = dict(start_data["params"], difficulty=1)
    r_submit = c.post("/api/sessions", json={
        "callsign": "GOLF-1",
        "unit": "1 TRG BN",
        "scenario_id": start_data["scenario_id"],
        "params": tampered_params,
        "assessment_token": start_data["assessment_token"],
        "client_id": "client-uuid-start-3",
        "events": [],
        "ended_t": 240.0,
    })
    assert r_submit.status_code == 403
    assert "invalid or expired assessment_token" in r_submit.get_json()["error"]


# ---------------------------------------------------------------- Phase 1.1: Hosted Secret Key Policy

def test_hosted_secret_key_policy_enforcement(test_db):
    """Enforces rejection of missing, known-default, short, or low-diversity secret keys in hosted mode."""
    # 1. Missing secret key in hosted mode
    with pytest.raises(RuntimeError) as exc_info:
        create_app({
            "DATABASE": test_db,
            "TESTING": False,
            "HOSTED": True,
            "SECRET_KEY": None,
        })
    assert "High-entropy SECRET_KEY must be explicitly configured" in str(exc_info.value)

    # 2. Known default secret key
    with pytest.raises(RuntimeError) as exc_info:
        create_app({
            "DATABASE": test_db,
            "TESTING": False,
            "HOSTED": True,
            "SECRET_KEY": "aegis-offline-workstation-local-secret",
        })
    assert "Insecure or known-default SECRET_KEY" in str(exc_info.value)

    # 3. Known placeholder keys (dev, changeme, password)
    for placeholder in ("dev", "changeme", "password", "secret"):
        with pytest.raises(RuntimeError) as exc_info:
            create_app({
                "DATABASE": test_db,
                "TESTING": False,
                "HOSTED": True,
                "SECRET_KEY": placeholder,
            })
        assert "Insecure or known-default SECRET_KEY" in str(exc_info.value) or "too short" in str(exc_info.value)

    # 4. Short key (< 32 characters)
    with pytest.raises(RuntimeError) as exc_info:
        create_app({
            "DATABASE": test_db,
            "TESTING": False,
            "HOSTED": True,
            "SECRET_KEY": "too-short-key-12345",
        })
    assert "too short" in str(exc_info.value)

    # 5. Low-diversity repetitive key
    with pytest.raises(RuntimeError) as exc_info:
        create_app({
            "DATABASE": test_db,
            "TESTING": False,
            "HOSTED": True,
            "SECRET_KEY": "a" * 32,
        })
    assert "too few unique characters" in str(exc_info.value)

    # 6. Suitably generated 32+ character hex key succeeds
    good_key = secrets.token_hex(32)
    app = create_app({
        "DATABASE": test_db,
        "TESTING": False,
        "HOSTED": True,
        "SECRET_KEY": good_key,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    assert app.config["SECRET_KEY"] == good_key

    # 7. Offline workstation mode succeeds with default
    offline_app = create_app({
        "DATABASE": test_db,
        "TESTING": False,
        "HOSTED": False,
        "SECRET_KEY": None,
    })
    assert offline_app.config["SECRET_KEY"] == "aegis-offline-workstation-local-secret"


# ---------------------------------------------------------------- Phase 1.1: Analytics Incomplete Session Exclusion

def test_analytics_excludes_incomplete_assessments_from_qualifying_performance(test_db):
    """Incomplete/interrupted attempts remain visible in session logs but are excluded from qualifying averages and series."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    hostile = first_hostile("s1-dawn-recon")

    # Session 1: completed, normal finish, good score (~100)
    r1 = post_session(c, [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
        {"t": hostile["spawn_t"] + 7.0, "type": "respond", "contact_id": hostile["id"], "data": {"response": "JAM"}},
    ], callsign="VIPER-X", unit="DELTA COY")
    assert r1.status_code == 201

    # Session 2: adversarial early exit at t=25s -> grade INCOMPLETE, low score (~20)
    r2 = post_session(c, [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
    ], callsign="VIPER-X", unit="DELTA COY", ended_t=25.0)
    assert r2.status_code == 201

    # Session 3: completed, normal finish, score 60
    r3 = post_session(c, [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ], callsign="VIPER-X", unit="DELTA COY")
    assert r3.status_code == 201

    trainees = c.get("/api/trainees?unit=delta coy").get_json()
    vx = next(t for t in trainees if t["callsign"] == "VIPER-X")
    assert vx["attempts"] == 3
    assert vx["completed"] == 2
    assert vx["incomplete"] == 1

    # Fetch trainee analytics
    a = c.get(f"/api/analytics/trainee/{vx['id']}").get_json()
    assert a["attempts"] == 3
    assert a["completed"] == 2
    assert a["incomplete"] == 1
    assert len(a["sessions"]) == 3  # all 3 visible in session history

    s1_score = a["sessions"][0]["total"]
    s2_score = a["sessions"][1]["total"]
    s3_score = a["sessions"][2]["total"]
    assert a["sessions"][1]["grade"] == "INCOMPLETE"

    # Qualifying average must be mean of Session 1 and Session 3, NOT diluted by Session 2
    expected_qualifying_avg = round((s1_score + s3_score) / 2.0, 1)
    assert a["averages"]["total"] == expected_qualifying_avg

    # Series total must preserve index alignment with None for the incomplete attempt
    assert a["series"]["total"][0] == s1_score
    assert a["series"]["total"][1] is None
    assert a["series"]["total"][2] == s3_score

    # Rolling total must compute across completed sessions
    assert a["rolling"]["total"][0] == s1_score
    assert a["rolling"]["total"][1] is None
    assert a["rolling"]["total"][2] == expected_qualifying_avg

    # Change total must be difference between latest and first completed session
    assert a["change"]["total"] == round(s3_score - s1_score, 1)

    # Unit analytics must also exclude Session 2 from unit qualifying averages
    u = c.get("/api/analytics/unit/delta coy").get_json()
    assert u["attempts"] == 3
    assert u["completed"] == 2
    assert u["incomplete"] == 1
    assert u["averages"]["total"] == expected_qualifying_avg


def test_unit_analytics_weakest_trainees_excludes_incomplete_only_trainees(test_db):
    """A trainee who only has incomplete sessions is not ranked in weakest trainees."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    hostile = first_hostile("s1-dawn-recon")

    # Trainee 1 (HAWK-INCOMPLETE): Only an interrupted attempt
    post_session(c, [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
    ], callsign="HAWK-INCOMPLETE", unit="OMEGA COY", ended_t=20.0)

    # Trainee 2 (VIPER-COMPLETED): One completed session with score 60
    r = post_session(c, [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ], callsign="VIPER-COMPLETED", unit="OMEGA COY")
    assert r.status_code == 201

    u = c.get("/api/analytics/unit/omega coy").get_json()
    ranked_callsigns = [t["callsign"] for t in u["weakest_trainees"]]
    assert "VIPER-COMPLETED" in ranked_callsigns
    assert "HAWK-INCOMPLETE" not in ranked_callsigns


# ---------------------------------------------------------------- Phase 1.1: Rate Limiter & Proxy Resolution

def test_client_ip_proxy_resolution_trusted_vs_untrusted(test_db):
    """Client IP is only extracted from X-Forwarded-For when remote_addr is in TRUSTED_PROXIES."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "TRUSTED_PROXIES": ["10.0.0.1", "127.0.0.1"],
    })

    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"},
                                  headers={"X-Forwarded-For": "203.0.113.195, 10.0.0.1"}):
        assert get_client_ip() == "203.0.113.195"

    # Untrusted proxy remote_addr -> X-Forwarded-For ignored
    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "198.51.100.5"},
                                  headers={"X-Forwarded-For": "203.0.113.195"}):
        assert get_client_ip() == "198.51.100.5"

    # No trusted proxies configured -> always returns remote_addr
    app_no_proxies = create_app({"DATABASE": test_db, "TESTING": True})
    with app_no_proxies.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"},
                                            headers={"X-Forwarded-For": "203.0.113.195"}):
        assert get_client_ip() == "127.0.0.1"


def test_rate_limiter_memory_bounded_active_and_stale_eviction():
    """Rate limiter enforces memory bounds: evicts stale entries and prunes oldest entries on capacity overflow."""
    now = time.time()
    _WRITE_ATTEMPTS.clear()

    # Populate dummy entries to capacity
    for i in range(MAX_WRITE_TRACKED_IPS):
        _WRITE_ATTEMPTS[f"10.0.{i // 256}.{i % 256}"] = [now - 10.0]

    assert len(_WRITE_ATTEMPTS) == MAX_WRITE_TRACKED_IPS

    # Add one more IP; capacity enforcement must kick in and keep size <= MAX_WRITE_TRACKED_IPS
    _check_write_rate_limit("192.168.1.100")
    assert len(_WRITE_ATTEMPTS) <= MAX_WRITE_TRACKED_IPS
    assert "192.168.1.100" in _WRITE_ATTEMPTS

    # Test stale eviction
    _WRITE_ATTEMPTS["stale-ip"] = [now - 70.0]  # window is 60s
    _check_write_rate_limit("fresh-ip")
    # stale-ip must be evicted
    assert "stale-ip" not in _WRITE_ATTEMPTS

    _WRITE_ATTEMPTS.clear()


# ---------------------------------------------------------------- Phase 1.1: Real Cookie Attributes & HSTS

def test_cookie_attributes_under_https_and_http(test_db):
    """Verifies that a real successful login sets Secure, HttpOnly, and SameSite=Lax on HTTPS, and omits Secure on HTTP."""
    secret = "a-very-secure-hosted-secret-key-32-chars-long"

    # 1. HTTPS configuration
    app_https = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": secret,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
        "HTTPS_PROXIED": "true",
    })
    c_https = app_https.test_client()
    r_login_https = c_https.post("/login", data={"password": "alpha-secure-pass"})
    assert r_login_https.status_code == 302

    # Check Set-Cookie on HTTPS
    set_cookie_https = r_login_https.headers.get("Set-Cookie", "")
    assert "HttpOnly" in set_cookie_https
    assert "Secure" in set_cookie_https
    assert "SameSite=Lax" in set_cookie_https
    assert "Strict-Transport-Security" in r_login_https.headers

    # 2. Ordinary local HTTP configuration
    app_http = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": False,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c_http = app_http.test_client()
    r_login_http = c_http.post("/login", data={"password": "alpha-secure-pass"})
    assert r_login_http.status_code == 302

    set_cookie_http = r_login_http.headers.get("Set-Cookie", "")
    assert "HttpOnly" in set_cookie_http
    assert "SameSite=Lax" in set_cookie_http
    assert "Secure" not in set_cookie_http
    assert "Strict-Transport-Security" not in r_login_http.headers


# ---------------------------------------------------------------- Phase 1.1: Legacy Idempotency & Concurrency Recovery Hardening

def test_legacy_session_with_null_or_empty_request_hash_fails_closed(test_db):
    """Submissions matching an existing legacy row whose request_hash is NULL or empty string
    fail closed with 409 Conflict instead of returning the unverified legacy row."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    with app.app_context():
        get_db()
    c = app.test_client()

    # 1. Insert a legacy row with NULL request_hash
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("INSERT INTO trainees (callsign, unit) VALUES ('LEGACY-1', 'LEGACY UNIT')")
    trainee_id = cur.lastrowid
    cur.execute(
        "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
        "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result, client_id, assessment_nonce, request_hash) "
        "VALUES (?, 's1-dawn-recon', 'Dawn Recon', 1, '{}', '2026-01-01T00:00:00Z', 120.0, 95.0, 95.0, 95.0, 95.0, 'EXCELLENT', 0, 0, 0, ?, 'legacy-client-null', NULL, NULL)",
        (trainee_id, json.dumps({"ended_t": 120.0, "total": 95.0, "stages": {"detection": 95.0, "classification": 95.0, "engagement": 95.0}, "penalties": {"false_alarms": 0, "breaches": 0, "critical_errors": 0}, "grade": "EXCELLENT", "contacts": []}))
    )
    # 2. Insert a legacy row with empty string request_hash
    cur.execute(
        "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
        "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result, client_id, assessment_nonce, request_hash) "
        "VALUES (?, 's1-dawn-recon', 'Dawn Recon', 1, '{}', '2026-01-01T00:00:00Z', 120.0, 80.0, 80.0, 80.0, 80.0, 'QUALIFIED', 0, 0, 0, ?, 'legacy-client-empty', NULL, '')",
        (trainee_id, json.dumps({"ended_t": 120.0, "total": 80.0, "stages": {"detection": 80.0, "classification": 80.0, "engagement": 80.0}, "penalties": {"false_alarms": 0, "breaches": 0, "critical_errors": 0}, "grade": "QUALIFIED", "contacts": []}))
    )
    conn.commit()
    conn.close()

    # Reusing client_id against row with NULL request_hash must return 409 Conflict
    r_null = c.post("/api/sessions", json={
        "callsign": "LEGACY-1",
        "unit": "LEGACY UNIT",
        "scenario_id": "s1-dawn-recon",
        "client_id": "legacy-client-null",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_null.status_code == 409
    assert "client_id conflict: payload does not match existing session" in r_null.get_json()["error"]

    # Reusing client_id against row with empty string request_hash must return 409 Conflict
    r_empty = c.post("/api/sessions", json={
        "callsign": "LEGACY-1",
        "unit": "LEGACY UNIT",
        "scenario_id": "s1-dawn-recon",
        "client_id": "legacy-client-empty",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_empty.status_code == 409
    assert "client_id conflict: payload does not match existing session" in r_empty.get_json()["error"]


def test_idempotent_retry_rejects_altered_scenario_or_seed(test_db):
    """Reusing client_id with altered scenario_id or seed fails closed with 409 Conflict."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()

    payload1 = {
        "callsign": "GOLF-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "client_id": "client-golf-01",
        "events": [],
        "ended_t": 120.0,
    }
    r1 = c.post("/api/sessions", json=payload1)
    assert r1.status_code == 201

    # Alter scenario_id
    payload_diff_scen = dict(payload1, scenario_id="s2-night-loiter")
    r_diff_scen = c.post("/api/sessions", json=payload_diff_scen)
    assert r_diff_scen.status_code == 409

    # For procedural, alter seed
    payload_proc1 = {
        "callsign": "HOTEL-1",
        "unit": "1 TRG BN",
        "scenario_id": "procedural",
        "params": {"seed": 100},
        "client_id": "client-hotel-01",
        "events": [],
        "ended_t": 180.0,
    }
    r_proc1 = c.post("/api/sessions", json=payload_proc1)
    assert r_proc1.status_code == 201

    payload_proc2 = dict(payload_proc1, params={"seed": 200})
    r_proc2 = c.post("/api/sessions", json=payload_proc2)
    assert r_proc2.status_code == 409


# ---------------------------------------------------------------- Phase 1.1: Multi-Hop Reverse Proxy & IP Address Validation

def test_reverse_proxy_multi_hop_traversal_and_malformed_ip(test_db):
    """Validates right-to-left reverse proxy traversal, spoofing resistance, and malformed IP handling."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "TRUSTED_PROXIES": "10.0.0.1, 10.0.0.2",
    })

    # 1. Multi-hop chain: attacker (198.51.100.2) -> Proxy 1 (10.0.0.2) -> Proxy 2 (10.0.0.1) -> App
    # Attacker sent a fake X-Forwarded-For: 1.1.1.1
    # Proxy 1 appended 198.51.100.2
    # Proxy 2 appended 10.0.0.2
    # Header: "1.1.1.1, 198.51.100.2, 10.0.0.2", REMOTE_ADDR: "10.0.0.1"
    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "10.0.0.1"},
                                  headers={"X-Forwarded-For": "1.1.1.1, 198.51.100.2, 10.0.0.2"}):
        assert get_client_ip() == "198.51.100.2"

    # 2. Malformed IP in forwarding header stops traversal safely and does not trust spoofed entries
    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "10.0.0.1"},
                                  headers={"X-Forwarded-For": "1.1.1.1, not-a-valid-ip, 10.0.0.2"}):
        assert get_client_ip() == "10.0.0.2"

    # 3. Direct untrusted peer with forged header is never parsed through X-Forwarded-For
    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "198.51.100.55"},
                                  headers={"X-Forwarded-For": "8.8.8.8, 10.0.0.2"}):
        assert get_client_ip() == "198.51.100.55"


def test_trusted_proxies_environment_variable_propagation(monkeypatch, test_db):
    """TRUSTED_PROXIES configured in os.environ is properly loaded into app.config by create_app()."""
    monkeypatch.setenv("TRUSTED_PROXIES", "172.16.0.1, 172.16.0.2")
    app = create_app()
    assert app.config["TRUSTED_PROXIES"] == "172.16.0.1, 172.16.0.2"


# ---------------------------------------------------------------- Phase 1.1: Rate Limiter Strict Bounding & Eviction

def test_login_rate_limiter_memory_bounded_active_and_stale_eviction():
    """Auth failed-login limiter strictly enforces capacity bound and protects current caller during eviction."""
    from app.auth import _FAILED_ATTEMPTS, MAX_TRACKED_IPS, _record_failed
    now = time.time()
    _FAILED_ATTEMPTS.clear()

    # Fill to capacity
    for i in range(MAX_TRACKED_IPS):
        _FAILED_ATTEMPTS[f"10.1.{i // 256}.{i % 256}"] = [now - 10.0]

    assert len(_FAILED_ATTEMPTS) == MAX_TRACKED_IPS

    # Record failure for a new caller
    _record_failed("192.168.10.5")
    assert len(_FAILED_ATTEMPTS) <= MAX_TRACKED_IPS
    assert "192.168.10.5" in _FAILED_ATTEMPTS

    # Verify stale pruning
    _FAILED_ATTEMPTS["stale-auth-ip"] = [now - 90.0]  # window is 60s
    _record_failed("fresh-auth-ip")
    assert "stale-auth-ip" not in _FAILED_ATTEMPTS
    assert "fresh-auth-ip" in _FAILED_ATTEMPTS

    _FAILED_ATTEMPTS.clear()


# ---------------------------------------------------------------- Phase 1.1: Assessment Timing & Completion Integrity

def test_assessment_timing_integrity_and_completion_enforcement(test_db):
    """Verifies that missing ended_t, forged fast completion, and invalid timestamps are properly handled."""
    secret = "a-very-secure-hosted-secret-key-32-chars-long"
    app_hosted = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": secret,
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c_hosted = app_hosted.test_client()

    # 1. Hosted submission without assessment token -> 403
    r_no_token = c_hosted.post("/api/sessions", json={
        "callsign": "TIME-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_no_token.status_code == 403

    # Obtain valid token
    r_token = c_hosted.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_token.get_json()["assessment_token"]

    # 2. Hosted submission with missing ended_t -> 400
    r_no_ended = c_hosted.post("/api/sessions", json={
        "callsign": "TIME-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "events": [],
    })
    assert r_no_ended.status_code == 400
    assert "ended_t is required in hosted mode" in r_no_ended.get_json()["error"]

    # 3. Hosted submission with impossible timing (claims ended_t=120s when submitted immediately)
    # Token was issued just now; minimum physical time at 16x is (120/16)-2 = 5.5s
    r_fast = c_hosted.post("/api/sessions", json={
        "callsign": "TIME-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "time-client-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_fast.status_code == 201
    data_fast = r_fast.get_json()
    assert data_fast["session_status"] == "unverified"
    assert data_fast["grade"] == "INCOMPLETE"

    # 4. Offline submission with early ended_t -> 201 with grade INCOMPLETE
    app_offline = create_app({"DATABASE": test_db, "TESTING": True})
    c_off = app_offline.test_client()
    r_off = c_off.post("/api/sessions", json={
        "callsign": "OFFLINE-TIME",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "ended_t": 30.0,
        "events": [],
    })
    assert r_off.status_code == 201
    data_off = r_off.get_json()
    assert data_off["session_status"] == "interrupted"
    assert data_off["grade"] == "INCOMPLETE"

    # 5. Event after session end rejected with 400
    hostile = first_hostile("s1-dawn-recon")
    r_late_event = c_off.post("/api/sessions", json={
        "callsign": "LATE-EV",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "ended_t": 30.0,
        "events": [{"t": 35.0, "type": "mark", "contact_id": hostile["id"], "data": {}}],
    })
    assert r_late_event.status_code == 400

    # 6. Event after scenario duration rejected with 400
    r_post_duration = c_off.post("/api/sessions", json={
        "callsign": "POST-DUR",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "ended_t": 150.0,
        "events": [{"t": 155.0, "type": "mark", "contact_id": hostile["id"], "data": {}}],
    })
    assert r_post_duration.status_code == 400


# ---------------------------------------------------------------- Phase 1.1: Analytics Separation of Completed vs Incomplete

def test_analytics_mean_detection_time_and_confusion_matrix_exclude_incomplete(test_db):
    """Mean detection time and confusion matrix only calculate from completed qualifying sessions."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()
    hostile = first_hostile("s1-dawn-recon")

    # Session 1: completed session with 1 detection at t=10.0 (spawn_t=0 -> dt=10s) and classification RECON_UAS
    r1 = post_session(c, [
        {"t": hostile["spawn_t"] + 10.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 12.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ], callsign="EVAL-TRAINEE", unit="ANALYTICS COY")
    assert r1.status_code == 201

    # Session 2: early exit / incomplete session with early mark at t=2.0 (spawn_t=0 -> dt=2s)
    r2 = post_session(c, [
        {"t": hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
    ], callsign="EVAL-TRAINEE", unit="ANALYTICS COY", ended_t=20.0)
    assert r2.status_code == 201

    # Fetch trainee analytics
    conn = sqlite3.connect(test_db)
    trainee_row = conn.execute("SELECT id FROM trainees WHERE callsign = 'EVAL-TRAINEE'").fetchone()
    conn.close()
    t_id = trainee_row[0]
    data = c.get(f"/api/analytics/trainee/{t_id}").get_json()

    assert data["attempts"] == 2
    assert data["completed"] == 1
    assert data["incomplete"] == 1

    # Mean detection time must be exactly 10.0s (from Session 1), NOT (10 + 2)/2 = 6.0s
    assert data["mean_time_to_detect_s"] == 10.0

    # In Session 2, the contact was not classified before early abort. It must NOT count as NOT_CLASSIFIED in the matrix.
    # Confusion matrix must only reflect the 1 classification from Session 1.
    matrix = data["confusion"]["counts"]
    assert matrix[hostile["true_class"]]["RECON_UAS"] == 1
    assert matrix[hostile["true_class"]]["NOT_CLASSIFIED"] == 0


def test_session_end_tolerance_boundary_exact_checks(test_db):
    """Session end tolerance is exactly 0.5s: 20.49s and 20.50s pass, 20.51s fails with 400."""
    app = create_app({"DATABASE": test_db, "TESTING": True})
    c = app.test_client()
    hostile = first_hostile("s1-dawn-recon")

    # 1. Event at ended_t + 0.49s (20.49s) -> Accepted
    r1 = post_session(c, [
        {"t": hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": 20.49, "type": "sensor", "data": {"mode": "nv"}}
    ], callsign="TOL-TEST-1", unit="TOL COY", ended_t=20.0, client_id="cid-tol-049")
    assert r1.status_code == 201

    # 2. Event at ended_t + 0.50s (20.50s) -> Accepted
    r2 = post_session(c, [
        {"t": hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": 20.50, "type": "sensor", "data": {"mode": "nv"}}
    ], callsign="TOL-TEST-2", unit="TOL COY", ended_t=20.0, client_id="cid-tol-050")
    assert r2.status_code == 201

    # 3. Event at ended_t + 0.51s (20.51s) -> Rejected (400)
    r3 = post_session(c, [
        {"t": hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": 20.51, "type": "sensor", "data": {"mode": "nv"}}
    ], callsign="TOL-TEST-3", unit="TOL COY", ended_t=20.0, client_id="cid-tol-051")
    assert r3.status_code == 400
    assert "t must be a number between 0 and 20.5" in r3.get_json()["error"]


def test_https_proxied_environment_variable_propagation(monkeypatch, test_db):
    """HTTPS_PROXIED environment variable is loaded into Flask config and enables SESSION_COOKIE_SECURE."""
    monkeypatch.setenv("HTTPS_PROXIED", "true")
    app = create_app({"DATABASE": test_db, "TESTING": True})
    assert app.config.get("HTTPS_PROXIED") is True
    assert app.config.get("SESSION_COOKIE_SECURE") is True


# ==============================================================================
# Phase 1 & 1.1: Section 4.2 Authoritative Token Lifecycle and Concurrency Tests
# ==============================================================================

def test_token_lifecycle_issued_before_start_and_later_submitted_caught_by_timing(test_db):
    """Authoritative server-side start time prevents evasion: loading briefing early and submitting fast is caught.

    Proves:
    1. Browsing scenario briefing earlier does not authorize an assessment run.
    2. Assessment run started_at is authoritatively recorded by the server at /api/session/start.
    3. An immediate submission claiming full exercise duration violates the speedup check and is graded INCOMPLETE.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # 1. Trainee browses scenario list and scenario briefing
    r_sc = c.get("/api/scenario?id=s1-dawn-recon")
    assert r_sc.status_code == 200

    # 2. Trainee starts exercise via /api/session/start
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    start_data = r_start.get_json()
    token = start_data["assessment_token"]

    # 3. Submit immediately claiming ended_t=150s (physical elapsed is < 1s, min_physical is 7.375s)
    # The server calculates elapsed from authoritative assessment_runs.started_at, catching fast submission.
    r_submit = c.post("/api/sessions", json={
        "callsign": "TIMING-TEST",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-timing-01",
        "events": [],
        "ended_t": 150.0,
    })
    assert r_submit.status_code == 201
    data = r_submit.get_json()
    assert data["session_status"] == "unverified"
    assert data["grade"] == "INCOMPLETE"


def test_token_lifecycle_timing_boundary_and_trust_boundary_contract(test_db, monkeypatch):
    """Verify timing boundary values and test the explicit trust boundary of unproctored assessment.

    Formula: min_physical = max(0.0, (ended_t / 16.0) - 2.0)
    - Boundary 1: ended_t = 30.0s (<= 32.0s) -> min_physical == 0.0s (immediate submission allowed).
    - Boundary 2: ended_t = 48.0s -> min_physical == 1.0s:
        * elapsed = 0.95s (< 1.0s threshold) -> unverified (INCOMPLETE)
        * elapsed = 1.00s (== 1.0s exact boundary) -> verified
        * elapsed = 1.05s (> 1.0s above threshold) -> verified
    - Boundary 3: ended_t = 120.0s -> min_physical == 5.5s:
        * elapsed = 5.45s (< 5.5s) -> unverified
        * elapsed = 5.50s (== 5.5s) -> verified
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    fake_clock = [10000.0]

    def mock_time():
        return fake_clock[0]

    monkeypatch.setattr(time, "time", mock_time)

    # Boundary 1: ended_t = 30.0s -> min_physical = 0.0s -> immediate submission allowed
    fake_clock[0] = 10000.0
    r_start1 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token1 = r_start1.get_json()["assessment_token"]
    r_sub1 = c.post("/api/sessions", json={
        "callsign": "BOUND-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token1,
        "client_id": "cid-bound-01",
        "events": [],
        "ended_t": 30.0,
    })
    assert r_sub1.status_code == 201
    assert r_sub1.get_json()["session_status"] != "unverified"

    # Boundary 2: ended_t = 48.0s -> min_physical = 1.0s
    # Case 2a: elapsed = 0.95s (< 1.0s threshold) -> unverified
    fake_clock[0] = 20000.0
    r_start2a = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2a = r_start2a.get_json()["assessment_token"]
    fake_clock[0] = 20000.0 + 0.95
    r_sub2a = c.post("/api/sessions", json={
        "callsign": "BOUND-2A",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token2a,
        "client_id": "cid-bound-02a",
        "events": [],
        "ended_t": 48.0,
    })
    assert r_sub2a.status_code == 201
    assert r_sub2a.get_json()["session_status"] == "unverified"
    assert r_sub2a.get_json()["grade"] == "INCOMPLETE"

    # Case 2b: elapsed = 1.00s (exactly at boundary threshold) -> verified
    fake_clock[0] = 30000.0
    r_start2b = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2b = r_start2b.get_json()["assessment_token"]
    fake_clock[0] = 30000.0 + 1.00
    r_sub2b = c.post("/api/sessions", json={
        "callsign": "BOUND-2B",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token2b,
        "client_id": "cid-bound-02b",
        "events": [],
        "ended_t": 48.0,
    })
    assert r_sub2b.status_code == 201
    assert r_sub2b.get_json()["session_status"] != "unverified"

    # Case 2c: elapsed = 1.05s (above threshold) -> verified
    fake_clock[0] = 40000.0
    r_start2c = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2c = r_start2c.get_json()["assessment_token"]
    fake_clock[0] = 40000.0 + 1.05
    r_sub2c = c.post("/api/sessions", json={
        "callsign": "BOUND-2C",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token2c,
        "client_id": "cid-bound-02c",
        "events": [],
        "ended_t": 48.0,
    })
    assert r_sub2c.status_code == 201
    assert r_sub2c.get_json()["session_status"] != "unverified"

    # Boundary 3: ended_t = 120.0s -> min_physical = 5.5s
    # Case 3a: elapsed = 5.45s (< 5.5s) -> unverified
    fake_clock[0] = 50000.0
    r_start3a = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token3a = r_start3a.get_json()["assessment_token"]
    fake_clock[0] = 50000.0 + 5.45
    r_sub3a = c.post("/api/sessions", json={
        "callsign": "BOUND-3A",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token3a,
        "client_id": "cid-bound-03a",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_sub3a.status_code == 201
    assert r_sub3a.get_json()["session_status"] == "unverified"

    # Case 3b: elapsed = 5.50s (== 5.5s) -> verified
    fake_clock[0] = 60000.0
    r_start3b = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token3b = r_start3b.get_json()["assessment_token"]
    fake_clock[0] = 60000.0 + 5.50
    r_sub3b = c.post("/api/sessions", json={
        "callsign": "BOUND-3B",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token3b,
        "client_id": "cid-bound-03b",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_sub3b.status_code == 201
    assert r_sub3b.get_json()["session_status"] != "unverified"


def test_token_lifecycle_fabricated_fast_completion(test_db):
    """Fabricated fast completion marks session_status as unverified and grade as INCOMPLETE."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    r_submit = c.post("/api/sessions", json={
        "callsign": "FAST-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-fast-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_submit.status_code == 201
    data = r_submit.get_json()
    assert data["session_status"] == "unverified"
    assert data["grade"] == "INCOMPLETE"
    assert "unverified" in data["grade_label"].lower()


def test_token_lifecycle_submission_without_authorized_start_rejected(test_db):
    """Attempting submission without an authorized start via /api/session/start is rejected with 403."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # Obtain a token from GET /api/scenario?token=1 (which is unstarted in assessment_runs)
    sc_res = c.get("/api/scenario?id=s1-dawn-recon&token=1")
    token = sc_res.get_json().get("assessment_token")
    assert token is not None

    r_submit = c.post("/api/sessions", json={
        "callsign": "NOSTART-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-nostart-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_submit.status_code == 403
    assert "unauthorized or unstarted assessment run" in r_submit.get_json()["error"]


def test_token_lifecycle_reuse_after_consumption_rejected(test_db):
    """Attempting reuse of an assessment token after consumption is rejected with 409."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    # First submission succeeds (201)
    r1 = c.post("/api/sessions", json={
        "callsign": "REUSE-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-reuse-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r1.status_code == 201

    # Second submission with new client_id and same token fails with 409
    r2 = c.post("/api/sessions", json={
        "callsign": "REUSE-2",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-reuse-02",
        "events": [],
        "ended_t": 120.0,
    })
    assert r2.status_code == 409
    assert "already been consumed" in r2.get_json()["error"]


def test_token_lifecycle_altered_scenario_seed_parameters_rejected(test_db):
    """Altering scenario identity, seed, or parameters after token issuance is rejected with 403."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    # 1. Alter scenario_id
    r_alt_id = c.post("/api/sessions", json={
        "callsign": "ALT-1",
        "unit": "1 TRG BN",
        "scenario_id": "s2-night-loiter",
        "assessment_token": token,
        "client_id": "cid-alt-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_alt_id.status_code == 403

    # 2. Alter parameters
    r_start_p = c.post("/api/session/start", json={
        "scenario_id": "procedural",
        "seed": 99,
        "params": {"difficulty": 2, "terrain": "rural"},
    })
    token_p = r_start_p.get_json()["assessment_token"]
    sc_id_p = r_start_p.get_json()["scenario_id"]
    params_p = r_start_p.get_json()["params"]

    altered_p = dict(params_p, difficulty=4)
    r_alt_p = c.post("/api/sessions", json={
        "callsign": "ALT-2",
        "unit": "1 TRG BN",
        "scenario_id": sc_id_p,
        "params": altered_p,
        "assessment_token": token_p,
        "client_id": "cid-alt-02",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_alt_p.status_code == 403


def test_token_lifecycle_concurrent_duplicate_submissions_safe(test_db):
    """Concurrent duplicate submissions of the same assessment token are handled safely (exactly one 201, one 409)."""
    import concurrent.futures

    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })

    c_start = app.test_client()
    r_start = c_start.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    def submit_attempt(cid):
        client = app.test_client()
        return client.post("/api/sessions", json={
            "callsign": "CONC-TRAINEE",
            "unit": "1 TRG BN",
            "scenario_id": "s1-dawn-recon",
            "assessment_token": token,
            "client_id": cid,
            "events": [],
            "ended_t": 120.0,
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(submit_attempt, "cid-conc-01")
        f2 = executor.submit(submit_attempt, "cid-conc-02")
        r1 = f1.result()
        r2 = f2.result()

    statuses = sorted([r1.status_code, r2.status_code])
    assert statuses == [201, 409], f"Expected [201, 409] but got {statuses}"


def test_token_lifecycle_interrupted_and_incomplete_grading(test_db):
    """Interrupted and early-exit assessments grade as INCOMPLETE without server error."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    # Abort at t=10.0s (less than 60% of duration)
    r = c.post("/api/sessions", json={
        "callsign": "EARLY-EXIT",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-early-01",
        "events": [],
        "ended_t": 10.0,
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["grade"] == "INCOMPLETE"
    assert data["total"] == 0


def test_token_lifecycle_invalid_submission_rolls_back_no_partial_records(test_db):
    """An invalid submission rolls back the transaction, leaving no partial records in sessions or events."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]
    run_id = r_start.get_json()["run_id"]

    # Invalid event: contact_id does not exist in s1-dawn-recon
    r = c.post("/api/sessions", json={
        "callsign": "INVALID-PAYLOAD",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-invalid-01",
        "events": [{"t": 10.0, "type": "classify", "contact_id": "C_NONEXISTENT", "data": {"class": "RECON_UAS"}}],
        "ended_t": 120.0,
    })
    assert r.status_code == 400

    # Verify no partial rows in database (trainees, sessions, events) and run remains active
    conn = sqlite3.connect(test_db)
    t_cnt = conn.execute("SELECT COUNT(*) FROM trainees WHERE callsign = 'INVALID-PAYLOAD'").fetchone()[0]
    s_cnt = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id = 'cid-invalid-01'").fetchone()[0]
    e_cnt = conn.execute("SELECT COUNT(*) FROM events WHERE contact_id = 'C_NONEXISTENT'").fetchone()[0]
    run_status = conn.execute("SELECT status FROM assessment_runs WHERE run_id = ?", (run_id,)).fetchone()[0]
    conn.close()

    assert t_cnt == 0
    assert s_cnt == 0
    assert e_cnt == 0
    assert run_status == "active"


def test_finding_a_rejected_submissions_create_no_database_side_effects(test_db, monkeypatch):
    """Rejected hosted submissions never create trainee records, sessions, or events.

    Covers all negative scenarios for Finding A:
    1. Missing hosted token -> rejected, 0 mutations.
    2. Invalid or fabricated token signature -> rejected, 0 mutations.
    3. Valid token signature but unstarted run -> rejected, 0 mutations.
    4. Scenario or parameter mismatch -> rejected, 0 mutations.
    5. Invalid event chronology -> rejected, 0 mutations.
    6. Database insertion failure partway through transaction -> rolled back completely,
       leaving 0 trainees, 0 sessions, 0 events, and assessment_runs status remains 'active'.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()
    with app.app_context():
        from app.db import get_db
        get_db()

    conn = sqlite3.connect(test_db)
    initial_trainees = conn.execute("SELECT COUNT(*) FROM trainees").fetchone()[0]
    initial_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    initial_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()

    # 1. Missing hosted token
    r1 = c.post("/api/sessions", json={
        "callsign": "REJECT-NO-TOKEN",
        "unit": "REJECT COY",
        "scenario_id": "s1-dawn-recon",
        "client_id": "cid-rej-1",
        "events": [],
        "ended_t": 120.0,
    })
    assert r1.status_code == 403

    # 2. Fabricated / invalid signature token
    r2 = c.post("/api/sessions", json={
        "callsign": "REJECT-BAD-TOKEN",
        "unit": "REJECT COY",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": "fabricated.token.here",
        "client_id": "cid-rej-2",
        "events": [],
        "ended_t": 120.0,
    })
    assert r2.status_code == 403

    # 3. Valid token signature but unstarted (no assessment_runs record)
    sc_res = c.get("/api/scenario?id=s1-dawn-recon&token=1")
    unregistered_token = sc_res.get_json()["assessment_token"]
    r3 = c.post("/api/sessions", json={
        "callsign": "REJECT-UNSTARTED",
        "unit": "REJECT COY",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": unregistered_token,
        "client_id": "cid-rej-3",
        "events": [],
        "ended_t": 120.0,
    })
    assert r3.status_code == 403

    # 4. Scenario or parameter mismatch
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    valid_token = r_start.get_json()["assessment_token"]
    run_id = r_start.get_json()["run_id"]
    r4 = c.post("/api/sessions", json={
        "callsign": "REJECT-MISMATCH",
        "unit": "REJECT COY",
        "scenario_id": "s2-night-loiter",
        "assessment_token": valid_token,
        "client_id": "cid-rej-4",
        "events": [],
        "ended_t": 120.0,
    })
    assert r4.status_code == 403

    # 5. Invalid event chronology (classify before mark)
    hostile = first_hostile("s1-dawn-recon")
    r5 = c.post("/api/sessions", json={
        "callsign": "REJECT-CHRONOLOGY",
        "unit": "REJECT COY",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": valid_token,
        "client_id": "cid-rej-5",
        "events": [{"t": hostile["spawn_t"] + 5.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}}],
        "ended_t": 120.0,
    })
    assert r5.status_code == 400

    # 6. Database insertion failure partway through transaction: verify full rollback
    from app.db import SQLiteDB
    orig_executemany = SQLiteDB.executemany

    def fail_executemany(self, sql, rows):
        raise sqlite3.OperationalError("Simulated disk failure during event insertion")

    monkeypatch.setattr(SQLiteDB, "executemany", fail_executemany)
    r6 = c.post("/api/sessions", json={
        "callsign": "REJECT-DB-FAIL",
        "unit": "REJECT COY",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": valid_token,
        "client_id": "cid-rej-6",
        "events": [{"t": hostile["spawn_t"] + 2.0, "type": "mark", "contact_id": hostile["id"], "data": {}}],
        "ended_t": 120.0,
    })
    assert r6.status_code == 500
    monkeypatch.undo()

    # Verify zero database mutations occurred across all 6 rejections!
    conn = sqlite3.connect(test_db)
    final_trainees = conn.execute("SELECT COUNT(*) FROM trainees").fetchone()[0]
    final_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    final_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    run_status = conn.execute("SELECT status FROM assessment_runs WHERE run_id = ?", (run_id,)).fetchone()[0]
    conn.close()

    assert final_trainees == initial_trainees
    assert final_sessions == initial_sessions
    assert final_events == initial_events
    # The assessment run remains active because the failed submission rolled back completely!
    assert run_status == "active"


# ---------------------------------------------------------------- Hosted Idempotency & Lost-Response Recovery

def test_hosted_idempotent_retry_returns_original_session(test_db):
    """Hosted assessment: a lost-response retry with identical payload and token returns 200 OK with original result."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # 1. Authorize assessment run
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    token = r_start.get_json()["assessment_token"]
    run_id = r_start.get_json()["run_id"]

    hostile = first_hostile("s1-dawn-recon")
    events = [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}},
    ]
    payload = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "client-hosted-retry-001",
        "events": events,
        "ended_t": 120.0,
    }

    # 2. Initial submission succeeds -> 201 Created
    r1 = c.post("/api/sessions", json=payload)
    assert r1.status_code == 201
    s1 = r1.get_json()

    # Verify run is marked consumed
    conn = sqlite3.connect(test_db)
    run_status = conn.execute("SELECT status FROM assessment_runs WHERE run_id = ?", (run_id,)).fetchone()[0]
    session_count_1 = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id = ?", (payload["client_id"],)).fetchone()[0]
    conn.close()
    assert run_status == "consumed"
    assert session_count_1 == 1

    # 3. Client lost HTTP response and retries the exact same submission
    r2 = c.post("/api/sessions", json=payload)
    assert r2.status_code == 200
    s2 = r2.get_json()

    # Verify exact match with original result
    assert s2["session_id"] == s1["session_id"]
    assert s2["started_at"] == s1["started_at"]
    assert s2["total"] == s1["total"]
    assert s2["grade"] == s1["grade"]

    # Verify no duplicate session or events were created
    conn = sqlite3.connect(test_db)
    session_count_2 = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id = ?", (payload["client_id"],)).fetchone()[0]
    total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    run_status_after = conn.execute("SELECT status FROM assessment_runs WHERE run_id = ?", (run_id,)).fetchone()[0]
    conn.close()

    assert session_count_2 == 1
    assert total_sessions == 1
    assert run_status_after == "consumed"


def test_hosted_idempotent_retry_altered_payload_fails_closed(test_db):
    """Hosted assessment: reusing client_id with altered events or timing fails closed (409 Conflict)."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    hostile = first_hostile("s1-dawn-recon")
    events = [
        {"t": hostile["spawn_t"] + 5.0, "type": "mark", "contact_id": hostile["id"], "data": {}},
    ]
    payload = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "client-hosted-alt-001",
        "events": events,
        "ended_t": 120.0,
    }

    # Initial submission -> 201 Created
    r1 = c.post("/api/sessions", json=payload)
    assert r1.status_code == 201

    # Retry with altered events
    altered_events = events + [
        {"t": hostile["spawn_t"] + 6.0, "type": "classify", "contact_id": hostile["id"], "data": {"class": "RECON_UAS"}}
    ]
    payload_alt_events = dict(payload, events=altered_events)
    r2 = c.post("/api/sessions", json=payload_alt_events)
    assert r2.status_code == 409
    assert "client_id conflict: payload does not match" in r2.get_json()["error"]

    # Retry with altered ended_t
    payload_alt_t = dict(payload, ended_t=100.0)
    r3 = c.post("/api/sessions", json=payload_alt_t)
    assert r3.status_code == 409
    assert "client_id conflict: payload does not match" in r3.get_json()["error"]


def test_hosted_idempotent_retry_different_trainee_fails_closed(test_db):
    """Hosted assessment: reusing client_id with a different trainee fails closed (409 Conflict)."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    payload = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "client-hosted-trainee-001",
        "events": [],
        "ended_t": 120.0,
    }

    r1 = c.post("/api/sessions", json=payload)
    assert r1.status_code == 201

    # Retry with different callsign
    payload_alt_trainee = dict(payload, callsign="BRAVO-2")
    r2 = c.post("/api/sessions", json=payload_alt_trainee)
    assert r2.status_code == 409
    assert "client_id conflict:" in r2.get_json()["error"]


def test_hosted_idempotent_retry_different_token_fails_closed(test_db):
    """Hosted assessment: reusing client_id with a different assessment token fails closed (409 Conflict)."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r1_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token1 = r1_start.get_json()["assessment_token"]

    payload = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token1,
        "client_id": "client-hosted-token-001",
        "events": [],
        "ended_t": 120.0,
    }

    r1 = c.post("/api/sessions", json=payload)
    assert r1.status_code == 201

    r2_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2 = r2_start.get_json()["assessment_token"]

    # Reusing client_id with a different token
    payload_alt_tok = dict(payload, assessment_token=token2)
    r2 = c.post("/api/sessions", json=payload_alt_tok)
    assert r2.status_code == 409
    assert "client_id conflict: assessment token does not match" in r2.get_json()["error"]


def test_hosted_consumed_token_rejected_for_new_client_id(test_db):
    """Hosted assessment: a consumed assessment token cannot be used to submit a new session with another client_id."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token = r_start.get_json()["assessment_token"]

    payload1 = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "client-first-001",
        "events": [],
        "ended_t": 120.0,
    }

    r1 = c.post("/api/sessions", json=payload1)
    assert r1.status_code == 201

    payload2 = {
        "callsign": "ALPHA-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "client-second-002",
        "events": [],
        "ended_t": 120.0,
    }

    r2 = c.post("/api/sessions", json=payload2)
    assert r2.status_code == 409
    assert "assessment_token has already been consumed (replay rejected)" in r2.get_json()["error"]


def test_adversarial_timing_obtain_scenario_before_start(test_db):
    """Adversarial check 1: Obtaining scenario metadata before starting does not authorize submission without /api/session/start."""
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "lifecycle-test-secret-key-32-chars-long",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # Trainee lists scenarios and fetches scenario configuration
    r_list = c.get("/api/scenarios")
    assert r_list.status_code == 200
    sc_list = r_list.get_json()
    assert any(s["id"] == "s1-dawn-recon" for s in sc_list)

    r_sc = c.get("/api/scenario?id=s1-dawn-recon")
    assert r_sc.status_code == 200
    sc_data = r_sc.get_json()
    assert sc_data["id"] == "s1-dawn-recon"

    # Attempting to submit without calling /api/session/start fails closed
    r_sub_notoken = c.post("/api/sessions", json={
        "callsign": "ADV-01",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "client_id": "cid-notoken-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_sub_notoken.status_code == 403
    assert "assessment_token is required" in r_sub_notoken.get_json()["error"]

    # Even if scenario was fetched with ?token=1, the token is not authorized in assessment_runs
    r_sc_tok = c.get("/api/scenario?id=s1-dawn-recon&token=1")
    assert r_sc_tok.status_code == 200
    unregistered_token = r_sc_tok.get_json()["assessment_token"]

    r_sub_unauth = c.post("/api/sessions", json={
        "callsign": "ADV-01",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": unregistered_token,
        "client_id": "cid-unauth-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_sub_unauth.status_code == 403
    assert "unauthorized or unstarted assessment run" in r_sub_unauth.get_json()["error"]

    # Attempting to submit with a completely fabricated token fails closed
    r_sub_fake = c.post("/api/sessions", json={
        "callsign": "ADV-01",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": "fake.token.value",
        "client_id": "cid-fake-01",
        "events": [],
        "ended_t": 120.0,
    })
    assert r_sub_fake.status_code == 403
    assert "invalid or expired assessment_token" in r_sub_fake.get_json()["error"]


def test_session_submission_database_error_distinction_and_no_leakage(test_db, monkeypatch):
    """Finding C: Database failures return 500 without leaking exception/SQL internals.

    Verifies:
    1. Operational / storage database failures return HTTP 500 (not 409).
    2. Response body is a generic message and does not expose file paths, table names, or raw exception strings.
    3. Failed submission transaction rolls back cleanly, leaving no partial records.
    4. Genuine integrity / uniqueness conflicts return HTTP 409 without detail leakage.
    5. Exact concurrent retry with matching client_id and request_hash returns 200 with existing session.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "phase1-remediation-test-secret-key-32-chars",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    # 1. Start an assessment run
    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    token = r_start.get_json()["assessment_token"]

    # 2. Inject unexpected database operational failure during session insert
    from app.db import SQLiteDB
    orig_insert = SQLiteDB.insert

    def mock_broken_insert(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise sqlite3.OperationalError("database disk image is malformed at block 4096 /data/secure/trainer.db")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_broken_insert)

    payload = {
        "callsign": "FAULT-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-db-fault-01",
        "events": [],
        "ended_t": 30.0,
    }

    r_fail = c.post("/api/sessions", json=payload)

    # Must be 500 Internal Server Error, NOT 409 Conflict
    assert r_fail.status_code == 500
    res_json = r_fail.get_json()
    assert res_json == {"error": "internal database error during session submission"}

    # Must NOT leak raw exception text, block numbers, or file paths
    raw_text = r_fail.get_data(as_text=True)
    assert "block 4096" not in raw_text
    assert "/data/secure" not in raw_text
    assert "OperationalError" not in raw_text
    assert "malformed" not in raw_text

    # 3. Verify clean transaction rollback: no partial session or trainee write
    conn = sqlite3.connect(test_db)
    sess_count = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id = 'cid-db-fault-01'").fetchone()[0]
    assert sess_count == 0

    # assessment_runs row was rolled back to 'active'
    run_status = conn.execute("SELECT status FROM assessment_runs WHERE run_id = (SELECT run_id FROM assessment_runs LIMIT 1)").fetchone()[0]
    assert run_status == "active"
    conn.close()

    # 4. Remove fault injection and verify normal successful submission
    monkeypatch.undo()

    r_ok = c.post("/api/sessions", json=payload)
    assert r_ok.status_code == 201
    s_id = r_ok.get_json()["session_id"]

    # 5. Exact concurrent retry with same client_id and matching payload returns 200
    r_retry = c.post("/api/sessions", json=payload)
    assert r_retry.status_code == 200
    assert r_retry.get_json()["session_id"] == s_id

    # 6. Replay attempt with same token or altered client_id returns 409 Conflict without leaking details
    payload_replay = dict(payload, client_id="cid-altered-client-02")
    r_conflict = c.post("/api/sessions", json=payload_replay)
    assert r_conflict.status_code == 409
    conf_json = r_conflict.get_json()
    assert "error" in conf_json
    assert "syntax error" not in conf_json["error"].lower()
    assert "traceback" not in conf_json["error"].lower()


def test_finding_c_constraint_violations_classify_as_500_and_never_leak_details(test_db, monkeypatch):
    """Finding C: Non-uniqueness integrity errors (NOT NULL, CHECK, FK) return 500 without leakage.

    Verifies:
    1. NOT NULL constraint failures (SQLITE_CONSTRAINT_NOTNULL / code 1299) return HTTP 500 (not 409).
    2. CHECK constraint failures (SQLITE_CONSTRAINT_CHECK / code 275) return HTTP 500 (not 409).
    3. FOREIGN KEY constraint failures (SQLITE_CONSTRAINT_FOREIGNKEY / code 787) return HTTP 500 (not 409).
    4. Unknown integrity errors default conservatively to HTTP 500.
    5. PostgreSQL SQLSTATE 23502 (NOT NULL) returns HTTP 500, while 23505 (UniqueViolation) returns 409.
    6. Error responses contain generic error messages without exposing SQL, tables, or column names.
    7. No partial records remain in the database after constraint failure rollback.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "phase1-remediation-test-secret-key-32-chars",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    from app.db import SQLiteDB
    orig_insert = SQLiteDB.insert

    # 1. NOT NULL constraint failure with structured SQLite error attributes
    def mock_not_null(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("NOT NULL constraint failed: sessions.started_at")
            err.sqlite_errorcode = 1299
            err.sqlite_errorname = "SQLITE_CONSTRAINT_NOTNULL"
            raise err
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_not_null)

    r_start1 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token1 = r_start1.get_json()["assessment_token"]
    payload1 = {
        "callsign": "NOTNULL-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token1,
        "client_id": "cid-notnull-test-01",
        "events": [],
        "ended_t": 30.0,
    }

    r_nn = c.post("/api/sessions", json=payload1)
    assert r_nn.status_code == 500
    assert r_nn.get_json() == {"error": "internal database error during session submission"}
    data_nn = r_nn.get_data(as_text=True)
    assert "started_at" not in data_nn
    assert "NOT NULL" not in data_nn
    assert "sessions" not in data_nn

    # 2. CHECK constraint failure with structured SQLite error attributes
    def mock_check(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("CHECK constraint failed: total >= 0")
            err.sqlite_errorcode = 275
            err.sqlite_errorname = "SQLITE_CONSTRAINT_CHECK"
            raise err
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_check)

    r_start2 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2 = r_start2.get_json()["assessment_token"]
    payload2 = dict(payload1, assessment_token=token2, client_id="cid-check-test-02")

    r_ck = c.post("/api/sessions", json=payload2)
    assert r_ck.status_code == 500
    assert r_ck.get_json() == {"error": "internal database error during session submission"}
    data_ck = r_ck.get_data(as_text=True)
    assert "CHECK constraint" not in data_ck
    assert "total >= 0" not in data_ck

    # 3. FOREIGN KEY constraint failure with structured SQLite error attributes
    def mock_fk(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("FOREIGN KEY constraint failed")
            err.sqlite_errorcode = 787
            err.sqlite_errorname = "SQLITE_CONSTRAINT_FOREIGNKEY"
            raise err
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_fk)

    r_start3 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token3 = r_start3.get_json()["assessment_token"]
    payload3 = dict(payload1, assessment_token=token3, client_id="cid-fk-test-03")

    r_fk = c.post("/api/sessions", json=payload3)
    assert r_fk.status_code == 500
    assert r_fk.get_json() == {"error": "internal database error during session submission"}
    data_fk = r_fk.get_data(as_text=True)
    assert "FOREIGN KEY" not in data_fk

    # 4. Unknown integrity error defaults conservatively to 500
    def mock_unknown(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("some unclassified internal error")
            err.sqlite_errorcode = 19
            err.sqlite_errorname = "SQLITE_CONSTRAINT"
            raise err
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_unknown)

    r_start4 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token4 = r_start4.get_json()["assessment_token"]
    payload4 = dict(payload1, assessment_token=token4, client_id="cid-unknown-test-04")

    r_unk = c.post("/api/sessions", json=payload4)
    assert r_unk.status_code == 500
    assert r_unk.get_json() == {"error": "internal database error during session submission"}

    # 5. PostgreSQL SQLSTATE classification: 23502 (NOT NULL) -> 500, 23505 (UniqueViolation) -> 409
    class MockPgError(Exception):
        def __init__(self, msg, sqlstate):
            super().__init__(msg)
            self.sqlstate = sqlstate

    def mock_pg_not_null(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise MockPgError("null value in column violates not-null constraint", "23502")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_pg_not_null)
    r_start5 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token5 = r_start5.get_json()["assessment_token"]
    r_pg_nn = c.post("/api/sessions", json=dict(payload1, assessment_token=token5, client_id="cid-pg-nn-05"))
    assert r_pg_nn.status_code == 500

    def mock_pg_unique(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise MockPgError("duplicate key value violates unique constraint", "23505")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_pg_unique)
    r_start6 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token6 = r_start6.get_json()["assessment_token"]
    r_pg_uq = c.post("/api/sessions", json=dict(payload1, assessment_token=token6, client_id="cid-pg-uq-06"))
    assert r_pg_uq.status_code == 409
    assert "conflict or replay" in r_pg_uq.get_json()["error"]

    # 6. Driver-less fallback classification: when driver error codes and SQLSTATE are absent
    # Case A: Ambiguous message containing 'unique' in a CHECK constraint -> 500
    def mock_ambiguous_check(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise sqlite3.IntegrityError("CHECK constraint failed: unique_identifier > 0")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_ambiguous_check)
    r_start7 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token7 = r_start7.get_json()["assessment_token"]
    r_amb_ck = c.post("/api/sessions", json=dict(payload1, assessment_token=token7, client_id="cid-fallback-check-07"))
    assert r_amb_ck.status_code == 500
    assert r_amb_ck.get_json() == {"error": "internal database error during session submission"}

    # Case B: Ambiguous message containing 'unique' in a NOT NULL column -> 500
    def mock_ambiguous_notnull(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise sqlite3.IntegrityError("NOT NULL constraint failed: sessions.unique_field")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_ambiguous_notnull)
    r_start8 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token8 = r_start8.get_json()["assessment_token"]
    r_amb_nn = c.post("/api/sessions", json=dict(payload1, assessment_token=token8, client_id="cid-fallback-nn-08"))
    assert r_amb_nn.status_code == 500
    assert r_amb_nn.get_json() == {"error": "internal database error during session submission"}

    # Case C: Unknown integrity error without driver attributes defaults conservatively to 500
    def mock_unknown_bare(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise sqlite3.IntegrityError("unclassified database integrity error")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_unknown_bare)
    r_start9 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token9 = r_start9.get_json()["assessment_token"]
    r_unk_bare = c.post("/api/sessions", json=dict(payload1, assessment_token=token9, client_id="cid-fallback-unk-09"))
    assert r_unk_bare.status_code == 500
    assert r_unk_bare.get_json() == {"error": "internal database error during session submission"}

    # Case D: Genuine SQLite uniqueness violation without driver attributes -> 409
    def mock_unique_bare(self, sql, args):
        if "INSERT INTO sessions" in sql:
            raise sqlite3.IntegrityError("UNIQUE constraint failed: sessions.client_id")
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_unique_bare)
    r_start10 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token10 = r_start10.get_json()["assessment_token"]
    r_uq_bare = c.post("/api/sessions", json=dict(payload1, assessment_token=token10, client_id="cid-fallback-uq-10"))
    assert r_uq_bare.status_code == 409
    assert "conflict or replay" in r_uq_bare.get_json()["error"]

    # 7. Confirm clean rollback: no session rows created
    conn = sqlite3.connect(test_db)
    cnt = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id LIKE 'cid-%'").fetchone()[0]
    assert cnt == 0
    conn.close()


def test_finding_d_concurrent_idempotency_recovery_branch(test_db, monkeypatch):
    """Finding D: Concurrent insert race condition deterministically exercises exception-recovery branch.

    Verifies:
    1. Pre-insert idempotency check sees no existing record (simulating concurrent insert race).
    2. During insert, SQLite's real UNIQUE index raises sqlite3.IntegrityError on sessions.client_id.
    3. Exception-recovery branch catches IntegrityError and evaluates _match_idempotent_retry.
    4. Same client ID, identical payload, same nonce: returns 200 with previously committed session.
    5. Same client ID, but different nonce: returns 409 conflict, NOT the concurrent session.
    6. Same client ID, but different request hash: returns 409 conflict.
    7. Same client ID, but different trainee identity: returns 409 conflict.
    8. Unhosted/local behavior when both records legitimately have no nonce: returns 200.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "phase1-remediation-test-secret-key-32-chars",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    from app.db import SQLiteDB
    from app.scenario import get_scenario
    from app import scoring

    orig_execute = SQLiteDB.execute

    class EmptyCursor:
        def fetchone(self):
            return None
        def fetchall(self):
            return []

    checked_client_ids = set()
    checked_nonces = set()
    recovery_hits = set()

    def mock_execute(self, sql, args=()):
        if "WHERE s.client_id = ?" in sql and args and str(args[0]).startswith("cid-race-"):
            cid = args[0]
            if cid not in checked_client_ids:
                # First check: pretend concurrent insert hasn't happened yet
                checked_client_ids.add(cid)
                return EmptyCursor()
            # Second check: inside exception recovery handler!
            recovery_hits.add(cid)
            return orig_execute(self, sql, args)
        if "WHERE assessment_nonce = ?" in sql and args:
            nonce = args[0]
            if nonce not in checked_nonces:
                checked_nonces.add(nonce)
                return EmptyCursor()
            return orig_execute(self, sql, args)
        return orig_execute(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "execute", mock_execute)

    # Helper to insert an already-committed session row into the test database
    def commit_concurrent_session(client_id, request_hash, nonce, callsign="ALPHA", unit="1 TRG BN"):
        conn = sqlite3.connect(test_db)
        conn.execute("INSERT OR IGNORE INTO trainees (callsign, unit) VALUES (?, ?)", (callsign, unit))
        t_id = conn.execute("SELECT id FROM trainees WHERE callsign = ? AND unit = ?", (callsign, unit)).fetchone()[0]
        cur = conn.execute(
            "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
            "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result, client_id, assessment_nonce, request_hash) "
            "VALUES (?, 's1-dawn-recon', 'Dawn Recon', 0, '{}', '2026-10-17T12:00:00Z', 30.0, 85.0, 85.0, 85.0, 85.0, 'B', 0, 0, 0, "
            "?, ?, ?, ?)",
            (t_id, json.dumps({"total": 85.0, "grade": "B", "stages": {"detection": 85.0, "classification": 85.0, "engagement": 85.0}}),
             client_id, nonce, request_hash)
        )
        s_id = cur.lastrowid
        conn.commit()
        conn.close()
        return s_id

    scen_obj = get_scenario("s1-dawn-recon")
    rub_obj = scoring.load_rubric(app.config["RUBRIC_PATH"])
    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    valid_events = scoring.validate_events(events, scen_obj, rub_obj, ended_t=30.0)
    res_scored = scoring.score_session(scen_obj, valid_events, rub_obj, 30.0)

    # --- Case 1: Identical payload, same nonce -> 200 OK via exception recovery ---
    r_start1 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token1 = r_start1.get_json()["assessment_token"]
    nonce1 = r_start1.get_json()["run_id"]

    req_body1 = {
        "callsign": "ALPHA",
        "unit": "1 TRG BN",
        "scenario_id": scen_obj["id"],
        "seed": scen_obj["seed"],
        "params": {},
        "events": valid_events,
        "ended_t": res_scored["ended_t"],
    }
    expected_hash1 = hashlib.sha256(_canonical_json(req_body1).encode()).hexdigest()

    # Pre-commit concurrent session into database with identical client_id, request_hash, and nonce
    commit_concurrent_session("cid-race-case1", expected_hash1, nonce1)

    payload1 = {
        "callsign": "ALPHA",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token1,
        "client_id": "cid-race-case1",
        "events": events,
        "ended_t": 30.0,
    }

    r_case1 = c.post("/api/sessions", json=payload1)
    assert "cid-race-case1" in recovery_hits, "Must have executed the exception-recovery branch"
    assert r_case1.status_code == 200
    assert r_case1.get_json()["total"] == 85.0
    assert r_case1.get_json()["grade"] == "B"

    # --- Case 2: Same client_id, but different valid nonce -> 409 Conflict ---
    r_start2 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token2 = r_start2.get_json()["assessment_token"]
    commit_concurrent_session("cid-race-case2", expected_hash1, "other-nonce-diff-999")

    payload2 = dict(payload1, assessment_token=token2, client_id="cid-race-case2")
    r_case2 = c.post("/api/sessions", json=payload2)
    assert "cid-race-case2" in recovery_hits
    assert r_case2.status_code == 409
    assert "assessment token does not match original session" in r_case2.get_json()["error"]

    # --- Case 3: Same client_id, but different request hash -> 409 Conflict ---
    r_start3 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token3 = r_start3.get_json()["assessment_token"]
    nonce3 = r_start3.get_json()["run_id"]
    commit_concurrent_session("cid-race-case3", "different-request-hash-xyz", nonce3)

    payload3 = dict(payload1, assessment_token=token3, client_id="cid-race-case3")
    r_case3 = c.post("/api/sessions", json=payload3)
    assert "cid-race-case3" in recovery_hits
    assert r_case3.status_code == 409
    assert "payload does not match existing session" in r_case3.get_json()["error"]

    # --- Case 4: Same client_id, but different trainee identity -> 409 Conflict ---
    r_start4 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    token4 = r_start4.get_json()["assessment_token"]
    nonce4 = r_start4.get_json()["run_id"]
    commit_concurrent_session("cid-race-case4", expected_hash1, nonce4, callsign="OTHER-TRAINEE", unit="9 TRG")

    payload4 = dict(payload1, assessment_token=token4, client_id="cid-race-case4")
    r_case4 = c.post("/api/sessions", json=payload4)
    assert "cid-race-case4" in recovery_hits
    assert r_case4.status_code == 409
    assert "trainee does not match existing session" in r_case4.get_json()["error"]

    # --- Case 5: Unhosted/offline mode where both legitimately have no nonce -> 200 OK ---
    app_offline = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": False,
        "INSTRUCTOR_PASSWORD": None,
    })
    c_off = app_offline.test_client()

    req_body5 = {
        "callsign": "OFFLINE",
        "unit": "SOLO UNIT",
        "scenario_id": scen_obj["id"],
        "seed": scen_obj["seed"],
        "params": {},
        "events": valid_events,
        "ended_t": res_scored["ended_t"],
    }
    expected_hash5 = hashlib.sha256(_canonical_json(req_body5).encode()).hexdigest()
    commit_concurrent_session("cid-race-case5", expected_hash5, None, callsign="OFFLINE", unit="SOLO UNIT")

    payload5 = {
        "callsign": "OFFLINE",
        "unit": "SOLO UNIT",
        "scenario_id": "s1-dawn-recon",
        "client_id": "cid-race-case5",
        "events": events,
        "ended_t": 30.0,
    }

    r_case5 = c_off.post("/api/sessions", json=payload5)
    assert "cid-race-case5" in recovery_hits
    assert r_case5.status_code == 200
    assert r_case5.get_json()["total"] == 85.0


def test_idempotency_recovery_failure_fault_injection(test_db, monkeypatch):
    """Verify that when both the original write and the recovery lookup fail,
    the system safely fails closed with HTTP 500 without leaking SQL or schema internals,
    rolls back completely, and leaves no partial records. Also verifies recovery lookup
    is never attempted for non-uniqueness errors.
    """
    app = create_app({
        "DATABASE": test_db,
        "TESTING": True,
        "HOSTED": True,
        "SECRET_KEY": "phase1-remediation-test-secret-key-32-chars",
        "INSTRUCTOR_PASSWORD": "alpha-secure-pass",
    })
    c = app.test_client()

    from app.db import SQLiteDB
    orig_insert = SQLiteDB.insert
    orig_execute = SQLiteDB.execute

    # 1. Fault injection: original write fails with uniqueness conflict (code 2067)
    # AND recovery lookup fails with OperationalError("database is locked")
    recovery_call_count = [0]
    recovery_attempted = []

    def mock_insert_uniqueness_fail(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("UNIQUE constraint failed: sessions.client_id")
            err.sqlite_errorcode = 2067
            err.sqlite_errorname = "SQLITE_CONSTRAINT_UNIQUE"
            raise err
        return orig_insert(self, sql, args)

    def mock_execute_recovery_fail(self, sql, args=()):
        if "WHERE s.client_id = ?" in sql:
            recovery_call_count[0] += 1
            if recovery_call_count[0] > 1:
                recovery_attempted.append(args[0])
                raise sqlite3.OperationalError("database is locked: disk I/O error on recovery query")
        return orig_execute(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_insert_uniqueness_fail)
    monkeypatch.setattr(SQLiteDB, "execute", mock_execute_recovery_fail)

    r_start = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start.status_code == 201
    token = r_start.get_json()["assessment_token"]

    payload = {
        "callsign": "FAULT-INJECT",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "assessment_token": token,
        "client_id": "cid-fault-recovery-01",
        "events": [],
        "ended_t": 30.0,
    }

    r_submit = c.post("/api/sessions", json=payload)
    # Recovery lookup was attempted because original error was a uniqueness conflict
    assert "cid-fault-recovery-01" in recovery_attempted
    # But because recovery lookup also failed, it failed closed safely with HTTP 500
    assert r_submit.status_code == 500
    assert r_submit.get_json() == {"error": "internal database error during session submission"}
    # Verify zero detail leakage
    resp_text = r_submit.get_data(as_text=True)
    assert "locked" not in resp_text
    assert "disk I/O" not in resp_text
    assert "sessions" not in resp_text
    assert "SELECT" not in resp_text

    # Verify clean rollback: no records created for this client_id
    conn = sqlite3.connect(test_db)
    cnt = conn.execute("SELECT COUNT(*) FROM sessions WHERE client_id = 'cid-fault-recovery-01'").fetchone()[0]
    assert cnt == 0
    conn.close()

    # 2. Verify that recovery lookup is NEVER attempted for non-uniqueness errors
    recovery_call_count[0] = 0
    recovery_attempted.clear()

    def mock_insert_notnull_fail(self, sql, args):
        if "INSERT INTO sessions" in sql:
            err = sqlite3.IntegrityError("NOT NULL constraint failed: sessions.started_at")
            err.sqlite_errorcode = 1299
            err.sqlite_errorname = "SQLITE_CONSTRAINT_NOTNULL"
            raise err
        return orig_insert(self, sql, args)

    monkeypatch.setattr(SQLiteDB, "insert", mock_insert_notnull_fail)

    r_start2 = c.post("/api/session/start", json={"scenario_id": "s1-dawn-recon"})
    assert r_start2.status_code == 201
    token2 = r_start2.get_json()["assessment_token"]

    payload2 = dict(payload, assessment_token=token2, client_id="cid-fault-notnull-02")
    r_submit2 = c.post("/api/sessions", json=payload2)

    assert r_submit2.status_code == 500
    assert r_submit2.get_json() == {"error": "internal database error during session submission"}
    # Recovery lookup was NEVER attempted because error was NOT a uniqueness conflict!
    assert "cid-fault-notnull-02" not in recovery_attempted







