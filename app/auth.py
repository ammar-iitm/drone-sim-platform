"""Instructor login: protects results (dashboard, session reviews, exports, analytics).

Off unless INSTRUCTOR_PASSWORD is set, so the offline laptop version stays open. When it is
set, trainees can still pick a scenario, play it and see their own score; only the pages and
API calls that show other people's results need an instructor login.
"""

import functools
import hashlib
import hmac
import time
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

bp = Blueprint("auth", __name__)


def login_enabled():
    return bool(current_app.config.get("INSTRUCTOR_PASSWORD"))


def is_instructor():
    return not login_enabled() or session.get("instructor") is True


def instructor_required(view):
    """Pages redirect to the login page; API calls get a 401 with a JSON error."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if is_instructor():
            return view(*args, **kwargs)
        if request.path.startswith("/api/"):
            return jsonify({"error": "instructor login required"}), 401
        return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
    return wrapped


def init_app(app):
    password = app.config.get("INSTRUCTOR_PASSWORD")
    if password and not app.config.get("SECRET_KEY"):
        # Serverless instances must agree on the key without shared state, so derive it from the
        # password when no SECRET_KEY is given. Changing the password signs everyone out.
        app.config["SECRET_KEY"] = hashlib.sha256(b"aegis-instructor-session:" + password.encode()).hexdigest()
    # Flask already defines both keys (31 days, no SameSite), so set them outright.
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)
    app.context_processor(lambda: {"login_enabled": bool(password), "instructor": is_instructor()})
    app.register_blueprint(bp)


def _safe_next(target):
    # Only same-site paths, never another host.
    return target if target and target.startswith("/") and not target.startswith("//") else url_for("views.dashboard")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if not login_enabled():
        return redirect(url_for("views.dashboard"))
    error = None
    if request.method == "POST":
        given = request.form.get("password", "")
        if hmac.compare_digest(given.encode(), current_app.config["INSTRUCTOR_PASSWORD"].encode()):
            session.clear()
            session["instructor"] = True
            session.permanent = True
            return redirect(_safe_next(request.form.get("next")))
        time.sleep(0.5)  # slows guessing
        error = "That password is not right."
    return render_template("login.html", active="dashboard", error=error, next=request.values.get("next", "")), \
        (401 if error else 200)


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("views.mission"))
