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
        DATABASE_URL=os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL"),
    )
    if test_config:
        app.config.update(test_config)
        if "DATABASE" in test_config and "DATABASE_URL" not in test_config:
            # An explicit SQLite file (as every test passes) wins over a DATABASE_URL left in
            # the shell, so tests can never write to a hosted database by accident.
            app.config["DATABASE_URL"] = None
    app.json.sort_keys = False

    from . import api, db, views
    db.init_app(app)
    hosted = bool(db.database_url(app))
    app.context_processor(lambda: {"hosted": hosted})
    app.register_blueprint(api.bp)
    app.register_blueprint(views.bp)
    return app
