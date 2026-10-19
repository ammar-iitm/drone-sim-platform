"""Structured, attributable security audit logging for AEGIS.

Emits machine-parseable JSON log records for security-relevant lifecycle events:
- Authentication (login success, login failure, lockout / rate limiting, logout, access denied)
- Data exports (session CSV export, unit CSV export, export access denied)
- Rubric provenance (version fingerprinting and version-change observations)

Security & Privacy Guarantees:
- Never logs passwords, tokens, cookies, SECRET_KEY, DATABASE_URL, request bodies, or CSV content.
- Query parameters and user-controlled strings are strictly sanitized.
- Safe execution: logging exceptions are caught and never cause user-facing errors.
"""

import hashlib
import json
import logging
import os
import re
import secrets
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from flask import current_app, has_request_context, request

AUDIT_LOGGER_NAME = "aegis.audit"

# Thread-safe cache for tracking rubric version fingerprint provenance
_RUBRIC_PROVENANCE_LOCK = threading.Lock()
_LAST_OBSERVED_RUBRIC_HASH = None

# Sensitive keys that must never appear in audit details
EXACT_FORBIDDEN_KEYS = {
    "data",
    "body",
    "csv",
    "key",
}

SUBSTRING_FORBIDDEN_KEYS = {
    "password",
    "secret",
    "token",
    "cookie",
    "authorization",
    "credential",
    "database_url",
    "postgres_url",
}


def _is_forbidden_key(key_str):
    k_lower = key_str.lower()
    if k_lower in EXACT_FORBIDDEN_KEYS:
        return True
    return any(bad in k_lower for bad in SUBSTRING_FORBIDDEN_KEYS)

MAX_AUDIT_DEPTH = 8
MAX_ITEMS_PER_COLLECTION = 25
MAX_STRING_LEN = 256
_SAFE_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_\-\.]{1,64}$")


def get_audit_logger():
    """Retrieve or configure the structured audit logger.

    Guarantees:
    - Dedicated StreamHandler outputting unadorned JSON messages.
    - Operates at INFO level even under default root logger settings.
    - Disables propagation to root to prevent duplicate logs or polluting Flask output.
    - Idempotent: does not add duplicate handlers on multiple calls.
    """
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    elif logger.level > logging.INFO:
        logger.setLevel(logging.INFO)
    return logger


def _sanitize_value(val, depth=0):
    if depth > MAX_AUDIT_DEPTH:
        return "[DEPTH_EXCEEDED]"
    if val is None or isinstance(val, (bool, int, float)):
        return val
    if isinstance(val, str):
        return val[:MAX_STRING_LEN]
    if isinstance(val, dict):
        return _sanitize_dict(val, depth)
    if isinstance(val, (list, tuple, set)):
        return [_sanitize_value(item, depth + 1) for item in list(val)[:MAX_ITEMS_PER_COLLECTION]]
    return str(val)[:MAX_STRING_LEN]


def _sanitize_dict(d, depth=0):
    if not isinstance(d, dict):
        return {}
    if depth > MAX_AUDIT_DEPTH:
        return {"_truncated": "[DEPTH_EXCEEDED]"}
    clean = {}
    for i, (k, v) in enumerate(d.items()):
        if i >= MAX_ITEMS_PER_COLLECTION:
            clean["_more"] = "[TRUNCATED]"
            break
        key_str = str(k)[:64]
        if _is_forbidden_key(key_str):
            clean[key_str] = "[REDACTED]"
            continue
        clean[key_str] = _sanitize_value(v, depth + 1)
    return clean


def _sanitize_details(details):
    """Sanitize detail dictionary to prevent secret or oversized data leakage.

    Recursively inspects mappings, lists, and tuples to scrub forbidden keys,
    bound collection lengths and string sizes, and preserve scalar JSON types.
    """
    if not isinstance(details, dict):
        return {}
    return _sanitize_dict(details, depth=0)


def _safe_request_id(raw_id):
    """Validate and bound caller-supplied X-Request-ID.

    Accepts alphanumeric strings with '-', '_', '.' up to 64 chars.
    Rejects malformed, oversized, or control-character-containing IDs.
    """
    if raw_id and isinstance(raw_id, str):
        cleaned = raw_id.strip()
        if _SAFE_REQUEST_ID_RE.match(cleaned) and not any(ord(c) < 32 or ord(c) > 126 for c in cleaned):
            return cleaned
    return None


def log_audit_event(event_name, outcome="success", actor=None, resource_type=None,
                    resource_id=None, details=None):
    """Emit a structured, machine-parseable JSON audit event.

    Args:
        event_name (str): Stable event identifier (e.g. 'auth.login.success').
        outcome (str): Event result ('success', 'failure', 'denied', 'rate_limited').
        actor (str, optional): Categorical or verified identity ('instructor', 'anonymous', etc.).
        resource_type (str, optional): Target resource category ('session', 'unit', 'rubric', 'auth').
        resource_id (str, optional): Minimal identifier of target resource.
        details (dict, optional): Contextual metadata (pre-sanitized).

    Returns:
        dict: The emitted structured audit record.
    """
    try:
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Resolve request context if available
        method = None
        path = None
        client_ip = None
        request_id = None

        if has_request_context():
            method = request.method
            path = request.path
            raw_req_id = request.headers.get("X-Request-ID")
            valid_req_id = _safe_request_id(raw_req_id)
            if valid_req_id:
                request_id = valid_req_id
            else:
                # Generate a transient correlation ID for this request
                if not hasattr(request, "_aegis_req_id"):
                    request._aegis_req_id = secrets.token_hex(8)
                request_id = request._aegis_req_id

            from .auth import get_client_ip
            client_ip = get_client_ip()

            if actor is None:
                from .auth import is_instructor
                actor = "instructor" if is_instructor() else "anonymous"
        else:
            if actor is None:
                actor = "system"

        record = {
            "timestamp": now_utc,
            "event": str(event_name),
            "outcome": str(outcome),
            "actor": str(actor),
            "method": method,
            "path": path,
            "request_id": request_id,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id is not None else None,
            "client_ip": client_ip,
            "details": _sanitize_details(details or {}),
        }

        logger = get_audit_logger()
        logger.info(json.dumps(record, sort_keys=True))
        return record
    except Exception:
        # Failsafe: Audit logging failure must never reveal secrets or crash user operations
        return {}


def compute_rubric_hash(rubric_path):
    """Compute SHA-256 fingerprint of the rubric definition file.

    Returns hex digest string or None if unreadable.
    """
    try:
        data = Path(rubric_path).read_bytes()
        return hashlib.sha256(data).hexdigest()
    except Exception:
        return None


def check_rubric_provenance(app=None):
    """Audit rubric version provenance and detect external modifications.

    Note on Attribution:
    Observing a new file hash indicates external modification of rubric.json.
    It proves version change provenance but does not identify which OS user
    or process modified the file on disk.
    """
    global _LAST_OBSERVED_RUBRIC_HASH

    try:
        if app is None:
            if has_request_context():
                app = current_app
            else:
                return None

        rubric_path = app.config.get("RUBRIC_PATH")
        if not rubric_path:
            return None

        current_hash = compute_rubric_hash(rubric_path)
        if not current_hash:
            return None

        with _RUBRIC_PROVENANCE_LOCK:
            if _LAST_OBSERVED_RUBRIC_HASH is None:
                _LAST_OBSERVED_RUBRIC_HASH = current_hash
                log_audit_event(
                    "rubric.provenance.loaded",
                    outcome="success",
                    actor="system",
                    resource_type="rubric",
                    details={"rubric_hash": current_hash},
                )
            elif _LAST_OBSERVED_RUBRIC_HASH != current_hash:
                old_hash = _LAST_OBSERVED_RUBRIC_HASH
                _LAST_OBSERVED_RUBRIC_HASH = current_hash
                log_audit_event(
                    "rubric.version.changed",
                    outcome="success",
                    actor="system",
                    resource_type="rubric",
                    details={
                        "old_hash": old_hash,
                        "new_hash": current_hash,
                        "attribution_boundary": "External file modification observed on disk",
                    },
                )
        return current_hash
    except Exception:
        return None


def reset_rubric_provenance():
    """Reset cached rubric provenance state (useful for test isolation)."""
    global _LAST_OBSERVED_RUBRIC_HASH
    with _RUBRIC_PROVENANCE_LOCK:
        _LAST_OBSERVED_RUBRIC_HASH = None

