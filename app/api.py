"""JSON API (AVD "Data model and API")."""

import csv
import io
import json
import re
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request
from werkzeug.exceptions import HTTPException

from . import analytics, scenario as scen, scoring
from .db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

CALLSIGN_MAX = 24


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
    return scoring.load_rubric(current_app.config["RUBRIC_PATH"])


def _body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("request body must be a JSON object")
    return data


def _clean_name(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"{field} is required")
    value = " ".join(value.strip().split())
    if len(value) > CALLSIGN_MAX:
        raise ApiError(f"{field} must be at most {CALLSIGN_MAX} characters")
    return value.upper()


# ---------------------------------------------------------------- scenarios and rubric

@bp.get("/scenarios")
def list_scenarios():
    return jsonify(scen.list_scripted())


@bp.get("/scenario")
def get_scenario():
    sid = request.args.get("id")
    try:
        if sid and not sid.startswith("proc-"):
            return jsonify(scen.build_scripted(sid, request.args.get("vary")))
        return jsonify(scen.generate(request.args.to_dict()))
    except KeyError:
        raise ApiError(f"no scripted scenario with id {sid!r}", 404)
    except ValueError as exc:
        raise ApiError(str(exc))


@bp.get("/rubric")
def get_rubric():
    return jsonify(rubric())


# ---------------------------------------------------------------- trainees

@bp.get("/trainees")
def list_trainees():
    unit = request.args.get("unit")
    sql = ("SELECT t.id, t.callsign, t.unit, t.created_at, COUNT(s.id) AS sessions, "
           "ROUND(AVG(s.total), 1) AS average FROM trainees t LEFT JOIN sessions s ON s.trainee_id = t.id ")
    args = ()
    if unit:
        sql += "WHERE t.unit = ? "
        args = (unit.upper(),)
    sql += "GROUP BY t.id ORDER BY t.unit, t.callsign"
    return jsonify([dict(r) for r in get_db().execute(sql, args)])


def find_or_create_trainee(callsign, unit):
    db = get_db()
    row = db.execute("SELECT * FROM trainees WHERE callsign = ? AND unit = ?", (callsign, unit)).fetchone()
    if row:
        return dict(row), False
    with db:
        cur = db.execute("INSERT INTO trainees (callsign, unit) VALUES (?, ?)", (callsign, unit))
    return dict(db.execute("SELECT * FROM trainees WHERE id = ?", (cur.lastrowid,)).fetchone()), True


@bp.post("/trainees")
def add_trainee():
    data = _body()
    trainee, created = find_or_create_trainee(_clean_name(data.get("callsign"), "callsign"),
                                              _clean_name(data.get("unit"), "unit"))
    return jsonify(trainee), 201 if created else 200


# ---------------------------------------------------------------- sessions

@bp.post("/sessions")
def submit_session():
    data = _body()
    rub = rubric()

    trainee_id = data.get("trainee_id")
    if trainee_id is not None:
        row = get_db().execute("SELECT * FROM trainees WHERE id = ?", (trainee_id,)).fetchone()
        if row is None:
            raise ApiError("unknown trainee_id", 404)
        trainee = dict(row)
    else:
        trainee, _ = find_or_create_trainee(_clean_name(data.get("callsign"), "callsign"),
                                            _clean_name(data.get("unit"), "unit"))

    # Rebuild the scenario on the server; the client's copy is never trusted.
    try:
        scenario = scen.get_scenario(data.get("scenario_id"), data.get("params"))
    except KeyError:
        raise ApiError("unknown scenario_id", 404)
    except ValueError as exc:
        raise ApiError(f"params: {exc}")

    ended_t = data.get("ended_t")
    if ended_t is not None and (not isinstance(ended_t, (int, float)) or isinstance(ended_t, bool)
                                or not 0 <= ended_t <= scenario["duration_s"] + 60):
        raise ApiError("ended_t must be a number within the scenario duration")

    try:
        events = scoring.validate_events(data.get("events"), scenario, rub)
    except ValueError as exc:
        raise ApiError(str(exc))

    result = scoring.score_session(scenario, events, rub, ended_t)
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    db = get_db()
    with db:  # one transaction: a failure leaves no half-written session
        cur = db.execute(
            "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
            "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trainee["id"], scenario["id"], scenario["name"], scenario["seed"],
             json.dumps(scenario.get("params")), started_at, result["ended_t"], result["total"],
             result["stages"]["detection"], result["stages"]["classification"], result["stages"]["engagement"],
             result["grade"], result["penalties"]["false_alarms"], result["penalties"]["breaches"],
             result["penalties"]["critical_errors"], json.dumps(result)))
        session_id = cur.lastrowid
        db.executemany("INSERT INTO events (session_id, t, type, contact_id, data) VALUES (?, ?, ?, ?, ?)",
                       [(session_id, e["t"], e["type"], e["contact_id"], json.dumps(e["data"])) for e in events])
    return jsonify({"session_id": session_id, "trainee": trainee, "started_at": started_at, **result}), 201


SESSION_COLUMNS = ("s.id, s.trainee_id, t.callsign, t.unit, s.scenario_id, s.scenario_name, s.seed, s.started_at, "
                   "s.duration_s, s.total, s.detection, s.classification, s.engagement, s.grade, s.false_alarms, "
                   "s.breaches, s.critical_errors")


@bp.get("/sessions")
def list_sessions():
    clauses, args = [], []
    if request.args.get("trainee_id"):
        clauses.append("s.trainee_id = ?")
        args.append(request.args["trainee_id"])
    if request.args.get("unit"):
        clauses.append("t.unit = ?")
        args.append(request.args["unit"].upper())
    sql = f"SELECT {SESSION_COLUMNS} FROM sessions s JOIN trainees t ON t.id = s.trainee_id"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY s.started_at DESC, s.id DESC LIMIT 500"
    return jsonify([dict(r) for r in get_db().execute(sql, args)])


@bp.get("/sessions/<int:session_id>")
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

def _csv(filename, header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", filename)
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{safe}"'})


@bp.get("/sessions/<int:session_id>/export.csv")
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
    return _csv(f"session-{session_id}-{row['callsign']}.csv", header, rows)


@bp.get("/analytics/unit/<unit>/export.csv")
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
    return _csv(f"unit-{unit}.csv", header, [tuple(r) for r in rows])


# ---------------------------------------------------------------- analytics

@bp.get("/analytics/trainee/<int:trainee_id>")
def trainee_analytics(trainee_id):
    data = analytics.trainee(get_db(), trainee_id, rubric())
    if data is None:
        raise ApiError("trainee not found", 404)
    return jsonify(data)


@bp.get("/analytics/unit/<unit>")
def unit_analytics(unit):
    data = analytics.unit(get_db(), unit.upper())
    if data is None:
        raise ApiError("no trainees in that unit", 404)
    return jsonify(data)
