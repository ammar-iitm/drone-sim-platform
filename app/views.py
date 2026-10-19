from flask import Blueprint, jsonify, redirect, render_template, url_for

from .auth import instructor_required
from .db import check_database_health

bp = Blueprint("views", __name__)


@bp.get("/health")
def health():
    """Readiness probe checking database reachability and schema version (Phase 4 OPS-01).

    Returns:
        HTTP 200 with {"status": "ok", "checks": {"database": "ok", "schema": "ok"}} if healthy.
        HTTP 503 with {"status": "unhealthy", "checks": {...}} if database or schema is degraded.
    """
    db_ok, schema_ok = check_database_health()
    status_str = "ok" if (db_ok and schema_ok) else "unhealthy"
    payload = {
        "status": status_str,
        "checks": {
            "database": "ok" if db_ok else "error",
            "schema": "ok" if schema_ok else "error",
        },
    }
    http_code = 200 if (db_ok and schema_ok) else 503
    return jsonify(payload), http_code


@bp.get("/")
def index():
    return redirect(url_for("views.mission"))


@bp.get("/mission")
def mission():
    return render_template("mission.html", active="mission")


@bp.get("/sim")
def sim():
    return render_template("sim.html", active="sim", compact=True)


@bp.get("/dashboard")
@instructor_required
def dashboard():
    return render_template("dashboard.html", active="dashboard")


@bp.get("/help")
def help_page():
    return render_template("help.html", active="help")


@bp.get("/dashboard/session/<id:session_id>")
@instructor_required
def session_review(session_id):
    return render_template("session.html", active="dashboard", session_id=session_id)
