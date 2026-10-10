"""Drone Threat Trainer: Flask app factory."""

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
    )
    if test_config:
        app.config.update(test_config)
    app.json.sort_keys = False

    from . import api, db, views
    db.init_app(app)
    hosted = bool(db.database_url(app))
    app.context_processor(lambda: {"hosted": hosted})
    app.register_blueprint(api.bp)
    app.register_blueprint(views.bp)
    return app
