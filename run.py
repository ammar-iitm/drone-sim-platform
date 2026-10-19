"""Start the Drone Threat Trainer: python run.py [--port 5050] [--lan]

Binds to localhost (127.0.0.1) by default for offline workstation mode.
--lan binds to 0.0.0.0 for classroom/network use. In network mode, INSTRUCTOR_PASSWORD
is required unless explicitly bypassed with --allow-unauthenticated-lan.
"""

import argparse
import os
import sys

from app import create_app

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Drone Threat Trainer")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--lan", action="store_true", help="listen on all network interfaces (0.0.0.0)")
    parser.add_argument("--allow-unauthenticated-lan", action="store_true",
                        help="allow unauthenticated access on local network (isolated classroom only)")
    parser.add_argument("--migrate", action="store_true",
                        help="apply database migrations to expected schema version and exit")
    return parser.parse_args(argv)


def build_app_config(args, env=None):
    if env is None:
        env = os.environ
    config = {}
    if args.lan:
        config["LAN_MODE"] = True
        if args.allow_unauthenticated_lan:
            config["ALLOW_UNAUTHENTICATED_LAN"] = True
        has_pwd = bool(env.get("INSTRUCTOR_PASSWORD"))
        if not has_pwd and not args.allow_unauthenticated_lan:
            raise ValueError(
                "SECURITY ERROR: --lan exposes AEGIS on 0.0.0.0 (all network interfaces).\n"
                "To proceed, either configure INSTRUCTOR_PASSWORD in your environment or "
                "provide --allow-unauthenticated-lan for an isolated classroom network."
            )
        if has_pwd:
            config["INSTRUCTOR_PASSWORD"] = env["INSTRUCTOR_PASSWORD"]
        if not has_pwd and args.allow_unauthenticated_lan:
            print("[WARNING] Running in unauthenticated classroom LAN mode. Training records are visible to anyone on the network.")

        sk = env.get("SECRET_KEY")
        if not sk:
            raise ValueError(
                "SECURITY ERROR: --lan exposes AEGIS on 0.0.0.0 (all network interfaces).\n"
                "A strong SECRET_KEY must be configured in the environment for LAN deployment.\n"
                "Generate a secret with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        from app import validate_hosted_secret_key
        valid, reason = validate_hosted_secret_key(sk)
        if not valid:
            raise ValueError(
                f"SECURITY ERROR: Invalid SECRET_KEY for LAN deployment: {reason}"
            )
        config["SECRET_KEY"] = sk
    return config


def main(argv=None):
    args = parse_args(argv)
    if args.migrate:
        app = create_app()
        from app.db import init_db
        init_db(app)
        print("Database migrations applied successfully.")
        return app, None, None
    try:
        cfg = build_app_config(args)
    except ValueError as exc:
        sys.exit(str(exc))
    app = create_app(cfg if cfg else None)
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    print(f"Drone Threat Trainer on http://{'localhost' if not args.lan else host}:{args.port}/")
    return app, host, args.port


if __name__ == "__main__":
    app, host, port = main()
    if host is not None and port is not None:
        app.run(host=host, port=port, debug=False)
