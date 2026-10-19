#!/usr/bin/env python3
"""AEGIS Deployment Environment Validator (Phase 4 OPS-01).

Validates deployment configuration before startup to help operators identify
misconfigurations, missing credentials, insecure keys, or invalid storage settings.

Operating Modes:
  auto    - Infers mode from environment using identical application rules (default)
  offline - Validates local workstation configuration
  lan     - Validates classroom/network deployment configuration
  hosted  - Validates hosted cloud deployment configuration

Usage:
  python scripts/check_env.py [--mode {auto,offline,lan,hosted}] [--json]

Exit Codes:
  0 - All configuration checks for the selected mode passed
  1 - One or more configuration checks failed
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from app import validate_hosted_secret_key
except ImportError:
    # Standalone fallback if app cannot be imported
    def validate_hosted_secret_key(secret_key):
        if not secret_key or not isinstance(secret_key, str):
            return False, "SECRET_KEY must be a non-empty string."
        if len(secret_key.strip()) < 32:
            return False, f"SECRET_KEY too short ({len(secret_key.strip())} chars; min 32 required)."
        if len(set(secret_key.strip())) < 8:
            return False, "SECRET_KEY contains too few unique characters."
        return True, None


def infer_mode(env=None):
    """Infer deployment mode following application rules in app/__init__.py and run.py."""
    if env is None:
        env = os.environ
    if bool(env.get("HOSTED") or env.get("VERCEL") or env.get("DATABASE_URL") or env.get("POSTGRES_URL")):
        return "hosted"
    if bool(env.get("LAN_MODE")):
        return "lan"
    return "offline"


def redact_db_url(url_str):
    """Safe database description omitting all connection details."""
    if not url_str or not isinstance(url_str, str):
        return "[Not set]"
    return "URL details intentionally omitted"


def check_rubric(rubric_path):
    """Validate existence, format, and essential schema of rubric.json."""
    p = Path(rubric_path)
    if not p.is_file():
        return False, f"Rubric file missing at {p}. Remediation: Ensure rubric.json exists in project root."
    try:
        content = p.read_bytes()
        import hashlib
        h = hashlib.sha256(content).hexdigest()
        data = json.loads(content.decode("utf-8"))
        if not isinstance(data, dict):
            return False, "Rubric file content is not a JSON object."
        required_keys = {"version", "weights", "grade_bands", "classes", "geometry"}
        missing = required_keys - set(data.keys())
        if missing:
            return False, f"Rubric missing essential top-level sections: {sorted(missing)}."
        return True, f"Valid rubric JSON (version: {data.get('version', 'unknown')}, SHA-256: {h[:16]}...)"
    except Exception as exc:
        return False, f"Failed to parse rubric JSON: {exc}"


def run_checks(mode="auto", env=None):
    """Run environment validation checks for the specified deployment mode.

    Returns:
        tuple[list[dict], int]: List of check results and final exit code (0 or 1).
    """
    if env is None:
        env = os.environ

    if mode == "auto":
        resolved_mode = infer_mode(env)
    else:
        resolved_mode = mode.lower()

    if resolved_mode not in ("offline", "lan", "hosted"):
        return [{"status": "FAIL", "name": "Mode Resolution",
                 "message": f"Unknown mode '{mode}'. Choose from: auto, offline, lan, hosted."}], 1

    checks = []

    # 1. Rubric Configuration Check
    rubric_path = env.get("RUBRIC_PATH", str(ROOT / "rubric.json"))
    rubric_ok, rubric_msg = check_rubric(rubric_path)
    checks.append({
        "status": "PASS" if rubric_ok else "FAIL",
        "name": "Rubric Configuration",
        "message": rubric_msg,
    })

    # 2. SECRET_KEY Configuration Check
    sk = env.get("SECRET_KEY")
    if resolved_mode in ("hosted", "lan"):
        if not sk:
            checks.append({
                "status": "FAIL",
                "name": "SECRET_KEY Policy",
                "message": (
                    f"SECRET_KEY is mandatory for {resolved_mode.upper()} deployment. "
                    "Remediation: Set a strong key with: python -c 'import secrets; print(secrets.token_hex(32))'"
                ),
            })
        else:
            valid, reason = validate_hosted_secret_key(sk)
            if valid:
                checks.append({
                    "status": "PASS",
                    "name": "SECRET_KEY Policy",
                    "message": f"High-entropy SECRET_KEY configured ({len(sk)} characters, validated).",
                })
            else:
                checks.append({
                    "status": "FAIL",
                    "name": "SECRET_KEY Policy",
                    "message": (
                        f"Insecure or invalid SECRET_KEY: {reason}. "
                        "Remediation: Generate a key with: python -c 'import secrets; print(secrets.token_hex(32))'"
                    ),
                })
    else:
        # Offline mode: default fallback permitted
        if sk:
            checks.append({
                "status": "PASS",
                "name": "SECRET_KEY Policy",
                "message": f"Custom SECRET_KEY configured ({len(sk)} characters).",
            })
        else:
            checks.append({
                "status": "PASS",
                "name": "SECRET_KEY Policy",
                "message": "Offline mode: Unset SECRET_KEY will use default local workstation secret.",
            })

    # 3. INSTRUCTOR_PASSWORD Authentication Check
    pwd = env.get("INSTRUCTOR_PASSWORD")
    if resolved_mode == "hosted":
        if not pwd:
            checks.append({
                "status": "FAIL",
                "name": "Instructor Authentication",
                "message": (
                    "INSTRUCTOR_PASSWORD is mandatory for HOSTED deployment. "
                    "Without it, endpoints fail closed with HTTP 503. "
                    "Remediation: Set INSTRUCTOR_PASSWORD in your environment."
                ),
            })
        else:
            checks.append({
                "status": "PASS",
                "name": "Instructor Authentication",
                "message": f"INSTRUCTOR_PASSWORD configured ({len(pwd)} characters).",
            })
    elif resolved_mode == "lan":
        allow_unauth = bool(env.get("ALLOW_UNAUTHENTICATED_LAN"))
        if not pwd and not allow_unauth:
            checks.append({
                "status": "FAIL",
                "name": "Instructor Authentication",
                "message": (
                    "LAN deployment exposes AEGIS on network. INSTRUCTOR_PASSWORD is required "
                    "unless explicitly bypassed with ALLOW_UNAUTHENTICATED_LAN=1 for isolated classrooms."
                ),
            })
        elif not pwd and allow_unauth:
            checks.append({
                "status": "WARN",
                "name": "Instructor Authentication",
                "message": "Classroom LAN running unauthenticated. Training records visible to entire network.",
            })
        else:
            checks.append({
                "status": "PASS",
                "name": "Instructor Authentication",
                "message": "INSTRUCTOR_PASSWORD configured for LAN access control.",
            })
    else:
        # Offline mode
        if pwd:
            checks.append({
                "status": "PASS",
                "name": "Instructor Authentication",
                "message": "INSTRUCTOR_PASSWORD configured for workstation results access.",
            })
        else:
            checks.append({
                "status": "PASS",
                "name": "Instructor Authentication",
                "message": "Offline mode: INSTRUCTOR_PASSWORD unset (local workstation open access enabled).",
            })

    # 4. Storage & Database Configuration Check
    db_url = env.get("DATABASE_URL") or env.get("POSTGRES_URL")
    is_vercel = bool(env.get("VERCEL"))

    if is_vercel:
        if not db_url:
            checks.append({
                "status": "FAIL",
                "name": "Database Configuration",
                "message": (
                    "Serverless platform (Vercel) detected without persistent database. "
                    "Local disk does not persist across cold starts. "
                    "Remediation: Configure DATABASE_URL or POSTGRES_URL to point to a PostgreSQL instance."
                ),
            })
        else:
            try:
                parsed = urlparse(db_url)
                if parsed.scheme not in ("postgres", "postgresql"):
                    checks.append({
                        "status": "FAIL",
                        "name": "Database Configuration",
                        "message": "DATABASE_URL must use postgresql:// scheme; URL details intentionally omitted.",
                    })
                else:
                    checks.append({
                        "status": "PASS",
                        "name": "Database Configuration",
                        "message": "Persistent PostgreSQL configured on Vercel; URL details intentionally omitted.",
                    })
            except Exception:
                checks.append({
                    "status": "FAIL",
                    "name": "Database Configuration",
                    "message": "Failed to parse DATABASE_URL; URL details intentionally omitted.",
                })
    elif db_url:
        try:
            parsed = urlparse(db_url)
            if parsed.scheme not in ("postgres", "postgresql"):
                checks.append({
                    "status": "FAIL",
                    "name": "Database Configuration",
                    "message": "DATABASE_URL must use postgresql:// scheme; URL details intentionally omitted.",
                })
            else:
                checks.append({
                    "status": "PASS",
                    "name": "Database Configuration",
                    "message": "PostgreSQL configured; URL details intentionally omitted.",
                })
        except Exception:
            checks.append({
                "status": "FAIL",
                "name": "Database Configuration",
                "message": "Failed to parse DATABASE_URL; URL details intentionally omitted.",
            })
    else:
        # Local SQLite
        sqlite_path = env.get("DATABASE", str(ROOT / "data" / "trainer.db"))
        p = Path(sqlite_path)
        try:
            # Check parent directory writable/creatable without mutating DB file
            parent_dir = p.parent
            if parent_dir.exists():
                dir_writable = os.access(str(parent_dir), os.W_OK)
            else:
                dir_writable = os.access(str(parent_dir.parent), os.W_OK)

            if not dir_writable:
                checks.append({
                    "status": "FAIL",
                    "name": "Database Configuration",
                    "message": f"Database directory '{parent_dir}' is not writable.",
                })
            else:
                exists_msg = f"exists ({p.stat().st_size} bytes)" if p.exists() else "will be initialized on first run"
                checks.append({
                    "status": "PASS",
                    "name": "Database Configuration",
                    "message": f"SQLite database path '{sqlite_path}' {exists_msg}.",
                })
        except Exception as exc:
            checks.append({
                "status": "FAIL",
                "name": "Database Configuration",
                "message": f"Error verifying database path: {type(exc).__name__}",
            })

    # Determine exit code
    has_failures = any(c["status"] == "FAIL" for c in checks)
    exit_code = 1 if has_failures else 0

    return checks, exit_code, resolved_mode


def main(argv=None):
    parser = argparse.ArgumentParser(description="AEGIS Environment & Configuration Validator")
    parser.add_argument(
        "--mode",
        choices=["auto", "offline", "lan", "hosted"],
        default="auto",
        help="Deployment mode to validate against (default: auto)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in machine-readable JSON format",
    )
    args = parser.parse_args(argv)

    checks, exit_code, resolved_mode = run_checks(args.mode)

    if args.json:
        output = {
            "mode": resolved_mode,
            "status": "PASS" if exit_code == 0 else "FAIL",
            "checks": checks,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== AEGIS Environment Validator [Mode: {resolved_mode.upper()}] ===")
        pass_count = 0
        warn_count = 0
        fail_count = 0
        for c in checks:
            st = c["status"]
            if st == "PASS":
                pass_count += 1
                symbol = "[PASS]"
            elif st == "WARN":
                warn_count += 1
                symbol = "[WARN]"
            else:
                fail_count += 1
                symbol = "[FAIL]"
            print(f"{symbol} {c['name']}: {c['message']}")

        print("-" * 60)
        print(f"Summary: {pass_count} passed, {warn_count} warnings, {fail_count} failed.")
        if exit_code == 0:
            print("Status: READY - Configuration conforms to AEGIS security and operational specifications.")
        else:
            print("Status: UNREADY - Resolve reported failures before starting AEGIS.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
