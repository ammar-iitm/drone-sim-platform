"""Drone Threat Trainer: Flask app factory."""

import os
from pathlib import Path

from flask import Flask

ROOT = Path(__file__).resolve().parent.parent


KNOWN_INSECURE_SECRETS = {
    "aegis-offline-workstation-local-secret",
    "aegis-assessment-secret",
    "test-secret-key-for-testing-only",
    "dev",
    "development",
    "secret",
    "secret_key",
    "changeme",
    "password",
    "admin",
    "12345678",
    "flask-secret-key",
}
MIN_SECRET_KEY_LEN = 32


def validate_hosted_secret_key(secret_key):
    """Validate that the secret key configured for hosted or network deployment meets security policy.
    Requires minimum length of 32 characters and rejects known defaults, common
    placeholder patterns, and low-diversity/predictable strings.
    Note: Structural heuristic checks (length >= 32, unique chars >= 8) reject trivial or
    placeholder keys but cannot mathematically prove high entropy. Operators must generate
    cryptographically strong random keys using an OS CSPRNG:
    python -c "import secrets; print(secrets.token_hex(32))"
    """
    if not secret_key or not isinstance(secret_key, str):
        return False, "SECRET_KEY must be a non-empty string in hosted/LAN deployment."
    sk_stripped = secret_key.strip()
    if sk_stripped.lower() in KNOWN_INSECURE_SECRETS:
        return False, "Insecure or known-default SECRET_KEY cannot be used in hosted/LAN deployment."
    if len(sk_stripped) < MIN_SECRET_KEY_LEN:
        return False, (
            f"SECRET_KEY is too short ({len(sk_stripped)} chars; minimum {MIN_SECRET_KEY_LEN} required). "
            "Generate a strong secret with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    if len(set(sk_stripped)) < 8:
        return False, (
            "SECRET_KEY contains too few unique characters (predictable or repetitive). "
            "Generate a strong secret with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    return True, None


def create_app(test_config=None):
    app = Flask(__name__)

    env_hosted = bool(
        os.environ.get("HOSTED")
        or os.environ.get("VERCEL")
        or (os.environ.get("DATABASE_URL") if test_config is None else None)
        or (os.environ.get("POSTGRES_URL") if test_config is None else None)
    )

    app.config.from_mapping(
        DATABASE=str(ROOT / "data" / "trainer.db"),
        RUBRIC_PATH=str(ROOT / "rubric.json"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        JSON_SORT_KEYS=False,
        # Postgres for hosted deployments (Vercel with Neon); unset means the local SQLite file.
        DATABASE_URL=None if test_config is not None else (
            os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")),
        HOSTED=False if test_config is not None else env_hosted,
        # Instructor login for results; off when unset (see app/auth.py).
        INSTRUCTOR_PASSWORD=None if test_config is not None else os.environ.get("INSTRUCTOR_PASSWORD"),
        SECRET_KEY=None if test_config is not None else os.environ.get("SECRET_KEY"),
        TRUSTED_PROXIES=None if test_config is not None else os.environ.get("TRUSTED_PROXIES"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
    app.json.sort_keys = False

    from . import api, auth, db, views

    # Database URL implies hosted mode
    if db.database_url(app):
        app.config["HOSTED"] = True

    # Enforce strong SECRET_KEY in hosted and LAN network modes
    is_network_mode = bool(app.config.get("HOSTED") or app.config.get("LAN_MODE"))
    if is_network_mode:
        sk = app.config.get("SECRET_KEY")
        if not app.config.get("TESTING") or app.config.get("VALIDATE_HOSTED_SECRET_KEY"):
            valid, reason = validate_hosted_secret_key(sk)
            if not valid:
                mode_desc = "Hosted deployment" if app.config.get("HOSTED") else "LAN deployment"
                raise RuntimeError(
                    f"{mode_desc} security configuration error: High-entropy SECRET_KEY "
                    f"must be explicitly configured. {reason} "
                    "Refusing to start with insecure defaults."
                )
        else:
            if not sk:
                app.config["SECRET_KEY"] = "test-secret-key-for-testing-only-with-at-least-32-chars-long"
    elif not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "aegis-offline-workstation-local-secret"

    # Resolve HTTPS and cookie security configuration from config and environment
    env_https_proxied = os.environ.get("HTTPS_PROXIED")
    if env_https_proxied and str(env_https_proxied).lower() in ("1", "true", "yes", "on"):
        app.config["HTTPS_PROXIED"] = True

    is_https = bool(
        app.config.get("SESSION_COOKIE_SECURE")
        or app.config.get("HTTPS_PROXIED")
        or os.environ.get("HTTPS") == "on"
        or os.environ.get("PREFERRED_URL_SCHEME") == "https"
        or os.environ.get("VERCEL")
    )
    app.config["SESSION_COOKIE_SECURE"] = is_https

    app.url_map.converters["id"] = db.IdConverter
    db.init_app(app)
    auth.init_app(app)
    hosted = bool(app.config.get("HOSTED") or db.database_url(app))
    app.context_processor(lambda: {"hosted": hosted})
    app.register_blueprint(api.bp)
    app.register_blueprint(views.bp)

    from . import audit
    audit.check_rubric_provenance(app)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        script_src = "'self' 'unsafe-inline' 'unsafe-eval'" if app.config.get("TESTING") else "'self' 'unsafe-inline'"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src {script_src}; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    return app
