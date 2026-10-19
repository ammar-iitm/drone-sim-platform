"""JSON API (AVD "Data model and API")."""

import csv
import hashlib
import hmac
import io
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request
from werkzeug.exceptions import HTTPException

from . import adaptive, analytics, scenario as scen, scoring
from .auth import get_client_ip, instructor_required, is_hosted, is_instructor, login_enabled
from .db import MAX_ID, avg1, get_db

bp = Blueprint("api", __name__, url_prefix="/api")

CALLSIGN_MAX = 24

_WRITE_ATTEMPTS = {}
MAX_WRITE_ATTEMPTS = 60
WRITE_WINDOW_SECONDS = 60
MAX_WRITE_TRACKED_IPS = 5000


def _canonical_json(obj):
    """Deterministic, canonical JSON serialization with sorted keys and minimal separators."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _check_write_rate_limit(ip):
    now = time.time()
    attempts = [t for t in _WRITE_ATTEMPTS.get(ip, []) if now - t < WRITE_WINDOW_SECONDS]
    if len(attempts) >= MAX_WRITE_ATTEMPTS:
        _WRITE_ATTEMPTS[ip] = attempts
        return True
    attempts.append(now)
    _WRITE_ATTEMPTS[ip] = attempts
    if len(_WRITE_ATTEMPTS) > MAX_WRITE_TRACKED_IPS:
        cutoff = now - WRITE_WINDOW_SECONDS
        stale = [k for k, v in _WRITE_ATTEMPTS.items() if not v or v[-1] < cutoff]
        for k in stale:
            _WRITE_ATTEMPTS.pop(k, None)
        if len(_WRITE_ATTEMPTS) > MAX_WRITE_TRACKED_IPS:
            sorted_keys = sorted(
                (k for k in _WRITE_ATTEMPTS.keys() if k != ip),
                key=lambda k: _WRITE_ATTEMPTS[k][-1] if _WRITE_ATTEMPTS[k] else 0
            )
            excess = len(_WRITE_ATTEMPTS) - MAX_WRITE_TRACKED_IPS
            for k in sorted_keys[:excess]:
                _WRITE_ATTEMPTS.pop(k, None)
    return False


class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message, self.status = message, status


@bp.errorhandler(ApiError)
def _api_error(err):
    return jsonify({"error": err.message}), err.status


@bp.errorhandler(HTTPException)
def _http_error(err):
    return jsonify({"error": err.description}), err.code


def rubric():
    from .audit import check_rubric_provenance
    check_rubric_provenance()
    return scoring.load_rubric(current_app.config["RUBRIC_PATH"])


def _body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("request body must be a JSON object")
    return data


def _trainee_id(value):
    """A trainee id from JSON or a query string, checked before it reaches the database
    (Postgres rejects a wrong type with an error where SQLite just finds nothing)."""
    if isinstance(value, str) and value.strip().isdigit():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ApiError("trainee_id must be an integer")
    if not 1 <= value <= MAX_ID:
        raise ApiError("unknown trainee_id", 404)
    return value


def _clean_name(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"{field} is required")
    value = " ".join(value.strip().split())
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ApiError(f"{field} must not contain control characters")
    if len(value) > CALLSIGN_MAX:
        raise ApiError(f"{field} must be at most {CALLSIGN_MAX} characters")
    return value.upper()


def _params_hash(params):
    if not params or not isinstance(params, dict):
        return "none"
    canonical = _canonical_json(params)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _generate_session_token(scenario_id, seed, params=None, nonce=None, ts=None):
    secret = (current_app.config.get("SECRET_KEY") or "aegis-assessment-secret").encode()
    if ts is None:
        ts = int(time.time())
    if nonce is None:
        nonce = os.urandom(16).hex()
    ph = _params_hash(params)
    msg = f"{scenario_id}:{seed}:{ph}:{ts}:{nonce}"
    sig = hmac.new(secret, msg.encode(), hashlib.sha256).hexdigest()
    return f"{msg}:{sig}"


def _verify_session_token(token, scenario_id, seed, params=None):
    if not token or not isinstance(token, str):
        return False, None
    parts = token.split(":")
    if len(parts) != 6:
        return False, None
    t_sid, t_seed, t_ph, t_ts, t_nonce, t_sig = parts
    if t_sid != str(scenario_id):
        return False, None
    if t_seed != str(seed):
        return False, None
    expected_ph = _params_hash(params)
    if t_ph != expected_ph:
        return False, None
    try:
        ts = int(t_ts)
        now = time.time()
        if now - ts > 86400 or ts - now > 60:
            return False, None
    except ValueError:
        return False, None
    secret = (current_app.config.get("SECRET_KEY") or "aegis-assessment-secret").encode()
    expected_msg = f"{scenario_id}:{seed}:{expected_ph}:{t_ts}:{t_nonce}"
    expected_sig = hmac.new(secret, expected_msg.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(t_sig, expected_sig):
        return False, None
    return True, t_nonce


# ---------------------------------------------------------------- scenarios and rubric

@bp.get("/scenarios")
def list_scenarios():
    return jsonify(scen.list_scripted())


@bp.get("/scenario")
def get_scenario():
    sid = request.args.get("id")
    try:
        if sid and str(sid).lower() != "procedural" and not sid.startswith("proc-"):
            sc = scen.build_scripted(sid, request.args.get("vary"))
        else:
            sc = scen.generate(request.args.to_dict())
        # For testing / backwards-compatibility if explicitly requested with ?token=1
        if request.args.get("token"):
            sc = dict(sc, assessment_token=_generate_session_token(sc["id"], sc["seed"], sc.get("params")))
        return jsonify(sc)
    except KeyError:
        raise ApiError(f"no scripted scenario with id {sid!r}", 404)
    except ValueError as exc:
        raise ApiError(str(exc))


@bp.post("/session/start")
def start_session():
    if is_hosted():
        client_ip = get_client_ip()
        if _check_write_rate_limit(client_ip):
            raise ApiError("rate limit exceeded for write operations", 429)
    data = _body()
    sid = data.get("scenario_id") or "s1-dawn-recon"
    params = data.get("params")
    if params is not None and not isinstance(params, dict):
        raise ApiError("params must be an object")
    p = dict(params or {})
    if "seed" in data and "seed" not in p:
        p["seed"] = data["seed"]
    if "vary" in data and "vary" not in p:
        p["vary"] = data["vary"]

    try:
        scenario = scen.get_scenario(sid, p)
    except KeyError:
        raise ApiError(f"no scripted scenario with id {sid!r}", 404)
    except ValueError as exc:
        raise ApiError(f"params: {exc}")

    now = time.time()
    run_id = os.urandom(16).hex()
    ph = _params_hash(scenario.get("params"))
    token = _generate_session_token(scenario["id"], scenario["seed"], scenario.get("params"), nonce=run_id, ts=int(now))

    db = get_db()
    with db:
        db.execute(
            "INSERT INTO assessment_runs (run_id, scenario_id, seed, params_hash, started_at, status) "
            "VALUES (?, ?, ?, ?, ?, 'active')",
            (run_id, scenario["id"], scenario["seed"], ph, now)
        )

    return jsonify({
        "assessment_token": token,
        "scenario_id": scenario["id"],
        "seed": scenario["seed"],
        "params": scenario.get("params"),
        "run_id": run_id,
        "issued_at": datetime.now(timezone.utc).isoformat()
    }), 201


@bp.get("/rubric")
def get_rubric():
    return jsonify(rubric())


# ---------------------------------------------------------------- trainees

@bp.get("/trainees")
@instructor_required
def list_trainees():
    unit = request.args.get("unit")
    stage_avg = avg1("CASE WHEN s.grade != 'INCOMPLETE' THEN s.total END")
    sql = ("SELECT t.id, t.callsign, t.unit, t.created_at, "
           "COUNT(s.id) AS attempts, "
           "COUNT(s.id) AS sessions, "
           "COUNT(CASE WHEN s.grade != 'INCOMPLETE' THEN 1 END) AS completed, "
           "COUNT(CASE WHEN s.grade = 'INCOMPLETE' THEN 1 END) AS incomplete, "
           f"{stage_avg} AS average FROM trainees t LEFT JOIN sessions s ON s.trainee_id = t.id ")
    args = ()
    if unit:
        sql += "WHERE t.unit = ? "
        args = (unit.upper(),)
    sql += "GROUP BY t.id ORDER BY t.unit, t.callsign"
    return jsonify([dict(r) for r in get_db().execute(sql, args)])


def find_or_create_trainee(callsign, unit):
    db = get_db()
    find = "SELECT * FROM trainees WHERE callsign = ? AND unit = ?"
    row = db.execute(find, (callsign, unit)).fetchone()
    if row:  # the usual case: one round trip
        return dict(row), False
    # Insert-if-missing, then read back: two first-time saves for the same trainee at once
    # (two browsers, a double-click, concurrent serverless instances) cannot collide.
    with db:
        created = db.execute("INSERT INTO trainees (callsign, unit) VALUES (?, ?) "
                             "ON CONFLICT (callsign, unit) DO NOTHING", (callsign, unit)).rowcount == 1
    return dict(db.execute(find, (callsign, unit)).fetchone()), created


@bp.post("/trainees")
def add_trainee():
    if is_hosted():
        client_ip = get_client_ip()
        if _check_write_rate_limit(client_ip):
            raise ApiError("rate limit exceeded for write operations", 429)
    data = _body()
    trainee, created = find_or_create_trainee(_clean_name(data.get("callsign"), "callsign"),
                                              _clean_name(data.get("unit"), "unit"))
    return jsonify(trainee), 201 if created else 200


# ---------------------------------------------------------------- sessions

def _match_idempotent_retry(existing, request_hash, trainee_id, trainee, callsign, unit, token_nonce, hosted):
    """Enforces strict idempotency criteria for both normal retries and concurrent insert recovery."""
    if not existing["request_hash"] or existing["request_hash"] != request_hash:
        raise ApiError("client_id conflict: payload does not match existing session", 409)
    if trainee_id is not None and existing["trainee_id"] != trainee["id"]:
        raise ApiError("client_id conflict: trainee does not match existing session", 409)
    if existing["callsign"] != callsign or existing["unit"] != unit:
        raise ApiError("client_id conflict: trainee does not match existing session", 409)
    if (hosted or existing["assessment_nonce"] or token_nonce) and existing["assessment_nonce"] != token_nonce:
        raise ApiError("client_id conflict: assessment token does not match original session", 409)
    res = json.loads(existing["result"])
    trainee_info = {"id": existing["trainee_id"], "callsign": existing["callsign"], "unit": existing["unit"]}
    return jsonify({"session_id": existing["id"], "trainee": trainee_info, "started_at": existing["started_at"], **res}), 200


@bp.post("/sessions")
def submit_session():
    if is_hosted():
        client_ip = get_client_ip()
        if _check_write_rate_limit(client_ip):
            raise ApiError("rate limit exceeded for write operations", 429)

    data = _body()
    rub = rubric()

    trainee_id = data.get("trainee_id")
    trainee = None
    callsign = None
    unit = None
    db = get_db()
    if trainee_id is not None:
        row = db.execute("SELECT * FROM trainees WHERE id = ?", (_trainee_id(trainee_id),)).fetchone()
        if row is None:
            raise ApiError("unknown trainee_id", 404)
        trainee = dict(row)
        callsign = trainee["callsign"]
        unit = trainee["unit"]
    else:
        callsign = _clean_name(data.get("callsign"), "callsign")
        unit = _clean_name(data.get("unit"), "unit")
        row = db.execute("SELECT * FROM trainees WHERE callsign = ? AND unit = ?", (callsign, unit)).fetchone()
        if row:
            trainee = dict(row)

    # Rebuild the scenario on the server; the client's copy is never trusted.
    try:
        scenario = scen.get_scenario(data.get("scenario_id"), data.get("params"))
    except KeyError:
        raise ApiError("unknown scenario_id", 404)
    except ValueError as exc:
        raise ApiError(f"params: {exc}")

    # Hosted Assessment Contract: assessment_token is required when hosted
    hosted = is_hosted()
    token = data.get("assessment_token")
    if hosted and not token:
        raise ApiError("assessment_token is required in hosted mode", 403)

    token_nonce = None
    if token:
        valid, token_nonce = _verify_session_token(token, scenario["id"], scenario["seed"], scenario.get("params"))
        if not valid:
            raise ApiError("invalid or expired assessment_token", 403)

    run_record = None
    if hosted or token_nonce:
        run_record = db.execute(
            "SELECT run_id, scenario_id, seed, params_hash, started_at, status FROM assessment_runs WHERE run_id = ?",
            (token_nonce,)
        ).fetchone()

        if hosted:
            if not run_record:
                raise ApiError("unauthorized or unstarted assessment run: session must be started via /api/session/start", 403)
            if (str(run_record["scenario_id"]) != str(scenario["id"]) or
                run_record["seed"] != scenario["seed"] or
                run_record["params_hash"] != _params_hash(scenario.get("params"))):
                raise ApiError("assessment run parameters do not match token", 403)

    session_end_tol = float(rub.get("geometry", {}).get("session_end_tolerance_s", 0.5))
    ended_t = data.get("ended_t")
    if hosted and ended_t is None:
        raise ApiError("ended_t is required in hosted mode", 400)
    if ended_t is not None and (not isinstance(ended_t, (int, float)) or isinstance(ended_t, bool)
                                or not 0 <= ended_t <= scenario["duration_s"] + session_end_tol):
        raise ApiError("ended_t must be a number within the scenario duration")

    try:
        events = scoring.validate_events(data.get("events"), scenario, rub, ended_t=ended_t)
    except ValueError as exc:
        raise ApiError(str(exc))

    result = scoring.score_session(scenario, events, rub, ended_t)

    # Server-side timing verification in hosted mode based on authoritative server started_at
    if hosted and run_record and ended_t is not None:
        now = time.time()
        elapsed = now - float(run_record["started_at"])
        min_physical = max(0.0, (float(ended_t) / 16.0) - 2.0)
        if elapsed < min_physical:
            result["session_status"] = "unverified"
            result["grade"] = "INCOMPLETE"
            result["grade_label"] = "Session completion unverified — assessment incomplete"

    # Compute deterministic request fingerprint from normalized assessment inputs
    req_payload = {
        "callsign": callsign,
        "unit": unit,
        "scenario_id": scenario["id"],
        "seed": scenario["seed"],
        "params": scenario.get("params") or {},
        "events": events,
        "ended_t": result["ended_t"],
    }
    request_hash = hashlib.sha256(_canonical_json(req_payload).encode()).hexdigest()

    client_id = data.get("client_id")

    # 1. Idempotency check on client_id: fail closed if stored request_hash is missing or does not match
    if client_id and isinstance(client_id, str):
        existing = db.execute(
            f"SELECT {SESSION_COLUMNS}, s.params, s.result FROM sessions s "
            "JOIN trainees t ON t.id = s.trainee_id WHERE s.client_id = ?", (client_id,)).fetchone()
        if existing:
            return _match_idempotent_retry(existing, request_hash, trainee_id, trainee, callsign, unit, token_nonce, hosted)

    # 2. Token replay check on run_record and token_nonce (only reached if this is NOT an exact retry)
    if run_record and hosted:
        if run_record["status"] == "consumed":
            raise ApiError("assessment_token has already been consumed (replay rejected)", 409)
        if run_record["status"] != "active":
            raise ApiError(f"assessment run is {run_record['status']}, not active", 403)

    if token_nonce:
        existing_nonce = db.execute(
            "SELECT id, client_id, request_hash FROM sessions WHERE assessment_nonce = ?", (token_nonce,)).fetchone()
        if existing_nonce:
            raise ApiError("assessment_token has already been consumed (replay rejected)", 409)

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        with db:  # one transaction: a failure leaves no half-written session or trainee
            if trainee is None:
                db.execute(
                    "INSERT INTO trainees (callsign, unit) VALUES (?, ?) "
                    "ON CONFLICT (callsign, unit) DO NOTHING", (callsign, unit)
                )
                t_row = db.execute("SELECT * FROM trainees WHERE callsign = ? AND unit = ?", (callsign, unit)).fetchone()
                trainee = dict(t_row)

            if run_record:
                upd = db.execute(
                    "UPDATE assessment_runs SET status = 'consumed' WHERE run_id = ? AND status = 'active'",
                    (token_nonce,)
                )
                if upd.rowcount != 1:
                    raise ApiError("assessment_token has already been consumed (replay rejected)", 409)
            session_id = db.insert(
                "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
                "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result, client_id, assessment_nonce, request_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (trainee["id"], scenario["id"], scenario["name"], scenario["seed"],
                 json.dumps(scenario.get("params")), started_at, result["ended_t"], result["total"],
                 result["stages"]["detection"], result["stages"]["classification"], result["stages"]["engagement"],
                 result["grade"], result["penalties"]["false_alarms"], result["penalties"]["breaches"],
                 result["penalties"]["critical_errors"], json.dumps(result), client_id, token_nonce, request_hash))
            db.executemany("INSERT INTO events (session_id, t, type, contact_id, data) VALUES (?, ?, ?, ?, ?)",
                           [(session_id, e["t"], e["type"], e["contact_id"], json.dumps(e["data"])) for e in events])
    except Exception as exc:
        if isinstance(exc, ApiError):
            raise

        # Structured database error classification using driver error codes and SQLSTATE
        is_uniqueness_conflict = False

        # 1. PostgreSQL SQLSTATE classification
        sqlstate = getattr(exc, "sqlstate", None) or getattr(getattr(exc, "diag", None), "sqlstate", None)
        if sqlstate is not None:
            # 23505 is PostgreSQL unique_violation
            if sqlstate == "23505":
                is_uniqueness_conflict = True
            else:
                # Other integrity constraints (23502 NOT NULL, 23503 FK, 23514 CHECK) or operational errors
                is_uniqueness_conflict = False
        else:
            # 2. SQLite driver error codes and extended error names
            sqlite_errname = getattr(exc, "sqlite_errorname", None)
            sqlite_errcode = getattr(exc, "sqlite_errorcode", None)

            if sqlite_errname is not None:
                if sqlite_errname in ("SQLITE_CONSTRAINT_UNIQUE", "SQLITE_CONSTRAINT_PRIMARYKEY"):
                    is_uniqueness_conflict = True
                else:
                    is_uniqueness_conflict = False
            elif sqlite_errcode is not None:
                # 2067: SQLITE_CONSTRAINT_UNIQUE, 1555: SQLITE_CONSTRAINT_PRIMARYKEY
                if sqlite_errcode in (2067, 1555):
                    is_uniqueness_conflict = True
                else:
                    is_uniqueness_conflict = False
            elif isinstance(exc, sqlite3.IntegrityError) or "integrityerror" in type(exc).__name__.lower():
                # Fallback classification only when driver does not expose extended error codes/names or SQLSTATE.
                # Strictly filters non-uniqueness constraint indicators first to prevent false-positive uniqueness matching.
                exc_msg = str(exc).lower()
                if any(k in exc_msg for k in ("not null", "check", "foreign key", "datatype", "trigger", "cannot be null")):
                    is_uniqueness_conflict = False
                elif any(k in exc_msg for k in (
                    "unique constraint failed:",
                    "primary key must be unique",
                    "are not unique",
                    "is not unique",
                    "duplicate key value violates unique constraint",
                )):
                    is_uniqueness_conflict = True
                else:
                    # Unknown or ambiguous integrity error defaults conservatively to False (HTTP 500)
                    is_uniqueness_conflict = False

        # 3. Attempt idempotency recovery ONLY where appropriate for the original error (uniqueness conflict)
        if is_uniqueness_conflict and client_id and isinstance(client_id, str):
            try:
                existing = db.execute(
                    f"SELECT {SESSION_COLUMNS}, s.params, s.result FROM sessions s "
                    "JOIN trainees t ON t.id = s.trainee_id WHERE s.client_id = ?", (client_id,)).fetchone()
                if existing:
                    return _match_idempotent_retry(existing, request_hash, trainee_id, trainee, callsign, unit, token_nonce, hosted)
            except ApiError:
                # Re-raise explicit application conflict/rejection from _match_idempotent_retry
                raise
            except Exception as recovery_exc:
                # If recovery lookup itself fails, log safely and fail closed with generic HTTP 500 without leaking details
                current_app.logger.error("Database failure during idempotency recovery lookup: %s", recovery_exc, exc_info=True)
                raise ApiError("internal database error during session submission", 500)

        if is_uniqueness_conflict:
            current_app.logger.warning("Session submission rejected due to database uniqueness conflict: %s", exc)
            raise ApiError("submission rejected due to conflict or replay", 409)

        current_app.logger.error("Unexpected database failure during session submission: %s", exc, exc_info=True)
        raise ApiError("internal database error during session submission", 500)

    return jsonify({"session_id": session_id, "trainee": trainee, "started_at": started_at, **result}), 201


SESSION_COLUMNS = ("s.id, s.trainee_id, t.callsign, t.unit, s.scenario_id, s.scenario_name, s.seed, s.started_at, "
                   "s.duration_s, s.total, s.detection, s.classification, s.engagement, s.grade, s.false_alarms, "
                   "s.breaches, s.critical_errors, s.client_id, s.assessment_nonce, s.request_hash")


@bp.get("/sessions")
@instructor_required
def list_sessions():
    clauses, args = [], []
    if request.args.get("trainee_id"):
        clauses.append("s.trainee_id = ?")
        args.append(_trainee_id(request.args["trainee_id"]))
    if request.args.get("unit"):
        clauses.append("t.unit = ?")
        args.append(request.args["unit"].upper())
    sql = f"SELECT {SESSION_COLUMNS} FROM sessions s JOIN trainees t ON t.id = s.trainee_id"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY s.started_at DESC, s.id DESC LIMIT 500"
    return jsonify([dict(r) for r in get_db().execute(sql, args)])


@bp.get("/sessions/<id:session_id>")
@instructor_required
def get_session(session_id):
    db = get_db()
    row = db.execute(f"SELECT {SESSION_COLUMNS}, s.params, s.result FROM sessions s "
                     f"JOIN trainees t ON t.id = s.trainee_id WHERE s.id = ?", (session_id,)).fetchone()
    if row is None:
        raise ApiError("session not found", 404)
    out = dict(row)
    out["params"] = json.loads(out["params"]) if out["params"] else None
    out["result"] = json.loads(out["result"])
    out["events"] = [{"t": e["t"], "type": e["type"], "contact_id": e["contact_id"], "data": json.loads(e["data"])}
                     for e in db.execute("SELECT * FROM events WHERE session_id = ? ORDER BY t, id", (session_id,))]
    return jsonify(out)


# ---------------------------------------------------------------- CSV export (F21)

def _sanitize_csv_cell(val):
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str) and len(val) > 0:
        stripped = val.lstrip()
        if stripped.startswith("-"):
            try:
                float(stripped)
                return val
            except ValueError:
                pass
        if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
            return "'" + val
    return val


def _csv(filename, header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([_sanitize_csv_cell(h) for h in header])
    for r in rows:
        writer.writerow([_sanitize_csv_cell(c) for c in r])
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", filename)
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{safe}"'})


@bp.get("/sessions/<id:session_id>/export.csv")
@instructor_required
def export_session(session_id):
    row = get_db().execute(f"SELECT {SESSION_COLUMNS}, s.result FROM sessions s JOIN trainees t ON t.id = s.trainee_id "
                           f"WHERE s.id = ?", (session_id,)).fetchone()
    if row is None:
        raise ApiError("session not found", 404)
    result = json.loads(row["result"])
    header = ["session_id", "date_utc", "callsign", "unit", "scenario", "seed", "session_total", "grade",
              "contact", "model", "true_class", "threat", "scored", "path",
              "detection_node", "detection_pct", "detection_reason",
              "classification_node", "classification_pct", "classified_as", "classification_reason",
              "engagement_node", "engagement_pct", "engagement_reason", "breached", "neutralised_t", "critical"]
    rows = []
    for c in result["contacts"]:
        stage = lambda s, k: (c.get(s) or {}).get(k, "")  # noqa: E731
        pct = lambda s: round(c[s]["points"] * 100) if c.get(s) else ""  # noqa: E731
        rows.append([row["id"], row["started_at"], row["callsign"], row["unit"], row["scenario_name"], row["seed"],
                     row["total"], row["grade"], c["id"], c["model"], c["true_class"], c["threat"], c["scored"],
                     " > ".join(c["path"]), stage("detection", "node"), pct("detection"), stage("detection", "reason"),
                     stage("classification", "node"), pct("classification"), stage("classification", "chosen") or "",
                     stage("classification", "reason"), stage("engagement", "node"), pct("engagement"),
                     stage("engagement", "reason"), c["breached"], c["neutralised_t"] if c["neutralised_t"] is not None else "",
                     ";".join(c["critical"])])
    resp = _csv(f"session-{session_id}-{row['callsign']}.csv", header, rows)
    try:
        from .audit import log_audit_event
        log_audit_event(
            "export.session_csv.success",
            outcome="success",
            actor="instructor",
            resource_type="session",
            resource_id=str(session_id),
            details={"callsign": row["callsign"], "scenario": row["scenario_name"]}
        )
    except Exception:
        pass
    return resp


@bp.get("/analytics/unit/<unit>/export.csv")
@instructor_required
def export_unit(unit):
    unit = unit.upper()
    rows = get_db().execute(
        "SELECT s.id, s.started_at, t.callsign, s.scenario_name, s.seed, s.total, s.grade, s.detection, "
        "s.classification, s.engagement, s.false_alarms, s.breaches, s.critical_errors FROM sessions s "
        "JOIN trainees t ON t.id = s.trainee_id WHERE t.unit = ? ORDER BY s.started_at, s.id", (unit,)).fetchall()
    if not rows:
        raise ApiError("no sessions for that unit", 404)
    header = ["session_id", "date_utc", "callsign", "scenario", "seed", "total", "grade", "detection",
              "classification", "engagement", "false_alarms", "breaches", "critical_errors"]
    resp = _csv(f"unit-{unit}.csv", header, [tuple(dict(r).values()) for r in rows])
    try:
        from .audit import log_audit_event
        log_audit_event(
            "export.unit_csv.success",
            outcome="success",
            actor="instructor",
            resource_type="unit",
            resource_id=unit,
            details={"session_count": len(rows)}
        )
    except Exception:
        pass
    return resp


@bp.get("/health")
def api_health():
    """Machine-readable readiness check alias for API clients."""
    from .views import health as views_health
    return views_health()


# ---------------------------------------------------------------- analytics

@bp.get("/analytics/trainee/<id:trainee_id>")
@instructor_required
def trainee_analytics(trainee_id):
    data = analytics.trainee(get_db(), trainee_id, rubric())
    if data is None:
        raise ApiError("trainee not found", 404)
    return jsonify(data)


@bp.get("/analytics/unit/<unit>")
@instructor_required
def unit_analytics(unit):
    data = analytics.unit(get_db(), unit.upper())
    if data is None:
        raise ApiError("no trainees in that unit", 404)
    return jsonify(data)


# ---------------------------------------------------------------- adaptive training (Phase 3)

@bp.get("/adaptive/recommendation")
def adaptive_recommendation():
    trainee_id = request.args.get("trainee_id")
    callsign = request.args.get("callsign")
    unit = request.args.get("unit")

    db = get_db()
    trainee = None

    is_auth = is_instructor() or (not is_hosted() and not login_enabled())

    if trainee_id is not None:
        if not is_auth:
            raise ApiError("instructor login required", 401)
        tid = _trainee_id(trainee_id)
        row = db.execute("SELECT * FROM trainees WHERE id = ?", (tid,)).fetchone()
        if row is None:
            raise ApiError("unknown trainee_id", 404)
        trainee = dict(row)
    elif callsign is not None:
        clean_callsign = _clean_name(callsign, "callsign")
        clean_unit = _clean_name(unit, "unit") if unit else None
        if is_auth:
            if clean_unit:
                row = db.execute("SELECT * FROM trainees WHERE callsign = ? AND unit = ?", (clean_callsign, clean_unit)).fetchone()
            else:
                row = db.execute("SELECT * FROM trainees WHERE callsign = ? ORDER BY id DESC LIMIT 1", (clean_callsign,)).fetchone()
            if row:
                trainee = dict(row)
            else:
                trainee = {"callsign": clean_callsign, "unit": clean_unit or "UNKNOWN"}
        else:
            # In hosted or password-protected mode, unauthenticated callers cannot retrieve
            # private history-derived skill profiles of existing trainees by guessing callsign/unit.
            # Return baseline onboarding profile without querying historical sessions.
            trainee = {"callsign": clean_callsign, "unit": clean_unit or "UNKNOWN"}
    else:
        raise ApiError("callsign or trainee_id is required", 400)

    parsed_sessions = []
    if "id" in trainee:
        session_rows = db.execute(
            f"SELECT {SESSION_COLUMNS}, s.params, s.result FROM sessions s "
            "JOIN trainees t ON t.id = s.trainee_id WHERE s.trainee_id = ? "
            "ORDER BY s.started_at ASC, s.id ASC",
            (trainee["id"],)
        ).fetchall()
        for r in session_rows:
            d = dict(r)
            if isinstance(d.get("result"), str):
                try:
                    d["result"] = json.loads(d["result"])
                except Exception:
                    pass
            if isinstance(d.get("params"), str):
                try:
                    d["params"] = json.loads(d["params"])
                except Exception:
                    pass
            parsed_sessions.append(d)

    rec = adaptive.recommend_next_scenario(trainee, parsed_sessions, rubric())
    return jsonify(rec)


@bp.get("/adaptive/profile")
def adaptive_profile():
    return adaptive_recommendation()
