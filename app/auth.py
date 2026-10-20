"""Instructor login: protects results (dashboard, session reviews, exports, analytics).

Optional: off unless INSTRUCTOR_PASSWORD is set, on the laptop and on the hosted version alike,
so results stay open until a password is configured. The one exception is a --lan classroom
server, which needs a password unless started with --allow-unauthenticated-lan. When it is
set, trainees can still pick a scenario, play it and see their own score; only the pages and
API calls that show other people's results need an instructor login.
"""

import functools
import hashlib
import hmac
import ipaddress
import os
import time
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

bp = Blueprint("auth", __name__)

_FAILED_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 60
MAX_TRACKED_IPS = 5000


def is_hosted():
    return bool(current_app.config.get("HOSTED")
                or current_app.config.get("DATABASE_URL")
                or os.environ.get("VERCEL")
                or os.environ.get("HOSTED"))


def is_lan():
    return bool(current_app.config.get("LAN_MODE") and not current_app.config.get("ALLOW_UNAUTHENTICATED_LAN"))


def login_enabled():
    return bool(current_app.config.get("INSTRUCTOR_PASSWORD"))


def is_instructor():
    if is_lan() and not login_enabled():
        return False
    return not login_enabled() or session.get("instructor") is True


def _parse_ip(addr):
    """Parse address string into IPv4Address or IPv6Address, or None if invalid."""
    if not addr or not isinstance(addr, str):
        return None
    try:
        return ipaddress.ip_address(addr.strip())
    except ValueError:
        return None


def _parse_trusted_proxies(trusted_config):
    """Parse TRUSTED_PROXIES configuration into a list of IP networks."""
    if not trusted_config:
        return []
    if isinstance(trusted_config, str):
        raw_items = [x.strip() for x in trusted_config.split(",") if x.strip()]
    elif isinstance(trusted_config, (list, tuple, set)):
        raw_items = [str(x).strip() for x in trusted_config if str(x).strip()]
    else:
        return []
    networks = []
    for item in raw_items:
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            continue
    return networks


def get_client_ip():
    """Extract client IP address adhering to reverse proxy security standards.
    - If no TRUSTED_PROXIES is configured or direct peer is not trusted, returns direct remote_addr.
    - If direct peer is trusted, traverses X-Forwarded-For right-to-left, accepting proxies
      until the first untrusted upstream IP is encountered.
    - Validates IP syntax and rejects malformed values.
    """
    remote_str = request.remote_addr or "127.0.0.1"
    trusted_cfg = current_app.config.get("TRUSTED_PROXIES")
    if not trusted_cfg:
        return remote_str

    trusted_nets = _parse_trusted_proxies(trusted_cfg)
    remote_ip = _parse_ip(remote_str)
    if not trusted_nets or not remote_ip:
        return remote_str

    # Only process X-Forwarded-For if the immediate peer is a configured trusted proxy
    if not any(remote_ip in net for net in trusted_nets):
        return remote_str

    forwarded = request.headers.get("X-Forwarded-For")
    if not forwarded:
        return remote_str

    # Right-to-left traversal (from closest trusted proxy backward)
    hops = [h.strip() for h in forwarded.split(",") if h.strip()]
    candidate = remote_str
    for hop in reversed(hops):
        parsed = _parse_ip(hop)
        if parsed is None:
            # Malformed IP syntax: stop traversal immediately, do not trust spoofed input
            break
        if any(parsed in net for net in trusted_nets):
            candidate = str(parsed)
            continue
        # First non-trusted IP encountered is the authoritative client
        return str(parsed)

    return candidate


def _is_rate_limited(ip):
    now = time.time()
    attempts = [t for t in _FAILED_ATTEMPTS.get(ip, []) if now - t < LOCKOUT_SECONDS]
    if attempts:
        _FAILED_ATTEMPTS[ip] = attempts
    else:
        _FAILED_ATTEMPTS.pop(ip, None)
    return len(attempts) >= MAX_FAILED_ATTEMPTS


def _record_failed(ip):
    now = time.time()
    attempts = [t for t in _FAILED_ATTEMPTS.get(ip, []) if now - t < LOCKOUT_SECONDS]
    attempts.append(now)
    _FAILED_ATTEMPTS[ip] = attempts
    if len(_FAILED_ATTEMPTS) > MAX_TRACKED_IPS:
        cutoff = now - LOCKOUT_SECONDS
        stale = [k for k, v in _FAILED_ATTEMPTS.items() if not v or v[-1] < cutoff]
        for k in stale:
            _FAILED_ATTEMPTS.pop(k, None)
        if len(_FAILED_ATTEMPTS) > MAX_TRACKED_IPS:
            sorted_keys = sorted(
                (k for k in _FAILED_ATTEMPTS.keys() if k != ip),
                key=lambda k: _FAILED_ATTEMPTS[k][-1] if _FAILED_ATTEMPTS[k] else 0
            )
            excess = len(_FAILED_ATTEMPTS) - MAX_TRACKED_IPS
            for k in sorted_keys[:excess]:
                _FAILED_ATTEMPTS.pop(k, None)


def _clear_failed(ip):
    _FAILED_ATTEMPTS.pop(ip, None)


def _safe_audit(*args, **kwargs):
    """Failsafe invocation of audit logging to guarantee security logging cannot crash auth."""
    try:
        from .audit import log_audit_event
        return log_audit_event(*args, **kwargs)
    except Exception:
        return {}


def instructor_required(view):
    """Pages redirect to the login page; API calls get a 401 with a JSON error.
    In LAN mode where INSTRUCTOR_PASSWORD is missing, fails closed with 503."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if is_lan() and not login_enabled():
            _safe_audit("auth.access.denied", outcome="denied", actor="anonymous",
                        resource_type="endpoint", details={"target": request.path, "reason": "lan_config_missing"})
            if request.path.startswith("/api/"):
                return jsonify({"error": "LAN security configuration missing: INSTRUCTOR_PASSWORD must be configured"}), 503
            return render_template("login.html", active="dashboard",
                                   error="LAN mode requires INSTRUCTOR_PASSWORD to be configured before accessing training records.",
                                   next=""), 503
        if is_instructor():
            return view(*args, **kwargs)
        _safe_audit("auth.access.denied", outcome="denied", actor="anonymous",
                    resource_type="endpoint", details={"target": request.path, "reason": "unauthenticated"})
        if request.path.startswith("/api/"):
            return jsonify({"error": "instructor login required"}), 401
        return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
    return wrapped


def init_app(app):
    password = app.config.get("INSTRUCTOR_PASSWORD")
    # Flask defines both keys (31 days, no SameSite), so set them outright.
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)
    app.context_processor(lambda: {"login_enabled": bool(password), "instructor": is_instructor()})
    app.register_blueprint(bp)


def _safe_next(target):
    # Only same-site paths, never another host.
    return target if target and target.startswith("/") and not target.startswith("//") else url_for("views.dashboard")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_lan() and not login_enabled():
        return render_template("login.html", active="dashboard",
                               error="LAN mode requires INSTRUCTOR_PASSWORD to be configured before accessing training records.",
                               next=""), 503
    if not login_enabled():
        return redirect(url_for("views.dashboard"))
    error = None
    client_ip = get_client_ip()
    if request.method == "POST":
        if _is_rate_limited(client_ip):
            _safe_audit("auth.login.rate_limited", outcome="rate_limited", actor="anonymous",
                        resource_type="auth", details={"reason": "lockout_active"})
            return render_template("login.html", active="dashboard",
                                   error="Too many failed login attempts. Please wait 60 seconds before trying again.",
                                   next=request.values.get("next", "")), 429
        given = request.form.get("password", "")
        if hmac.compare_digest(given.encode(), current_app.config["INSTRUCTOR_PASSWORD"].encode()):
            session.clear()
            session["instructor"] = True
            session.permanent = True
            _clear_failed(client_ip)
            _safe_audit("auth.login.success", outcome="success", actor="instructor", resource_type="auth")
            return redirect(_safe_next(request.form.get("next")))
        _record_failed(client_ip)
        time.sleep(0.5)  # slows guessing
        _safe_audit("auth.login.failure", outcome="failure", actor="anonymous",
                    resource_type="auth", details={"reason": "invalid_credentials"})
        error = "That password is not right."
    return render_template("login.html", active="dashboard", error=error, next=request.values.get("next", "")), \
        (401 if error else 200)


@bp.post("/logout")
def logout():
    _safe_audit("auth.logout.success", outcome="success", actor="instructor", resource_type="auth")
    session.clear()
    return redirect(url_for("views.mission"))
