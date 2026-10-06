"""Start the Drone Threat Trainer: python run.py [--port 5050] [--lan]

Binds to localhost by default. --lan exposes the app on the local network
without authentication, for an instructor screen in the same room.
"""

import argparse

from app import create_app

parser = argparse.ArgumentParser(description="Drone Threat Trainer")
parser.add_argument("--port", type=int, default=5050)
parser.add_argument("--lan", action="store_true", help="listen on all interfaces (unauthenticated)")
args = parser.parse_args()

app = create_app()
host = "0.0.0.0" if args.lan else "127.0.0.1"
print(f"Drone Threat Trainer on http://{'localhost' if not args.lan else host}:{args.port}/")
app.run(host=host, port=args.port, debug=False)
