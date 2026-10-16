"""Server-rendered pages. All data is loaded from the JSON API by page scripts."""

from flask import Blueprint, redirect, render_template, url_for

from .auth import instructor_required

bp = Blueprint("views", __name__)


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
