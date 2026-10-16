"""Drone Threat Trainer: Flask app factory."""

import os
from pathlib import Path

from flask import Flask

ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(ROOT / "data" / "trainer.db"),
        RUBRIC_PATH=str(ROOT / "rubric.json"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        JSON_SORT_KEYS=False,
        # Postgres for hosted deployments (Vercel with Neon); unset means the local SQLite file.
        # Read from the environment only for a real start: a test config never inherits a
        # DATABASE_URL left in the shell, and passes one explicitly to test on Postgres.
        DATABASE_URL=None if test_config is not None else (
            os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")),
        # Instructor login for results; off when unset (see app/auth.py).
        INSTRUCTOR_PASSWORD=None if test_config is not None else os.environ.get("INSTRUCTOR_PASSWORD"),
        SECRET_KEY=None if test_config is not None else os.environ.get("SECRET_KEY"),
        SESSION_COOKIE_SECURE=bool(os.environ.get("VERCEL")),  # HTTPS-only cookie when hosted
    )
    if test_config:
        app.config.update(test_config)
    app.json.sort_keys = False

    from . import api, auth, db, views
    app.url_map.converters["id"] = db.IdConverter
    db.init_app(app)
    auth.init_app(app)
    hosted = bool(db.database_url(app))
    app.context_processor(lambda: {"hosted": hosted})
    app.register_blueprint(api.bp)
    app.register_blueprint(views.bp)
    return app
