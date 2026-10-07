#!/usr/bin/env sh
# Start the Drone Threat Trainer on macOS or Linux.
#   ./start.sh            first run creates .venv and installs requirements (needs internet once)
#   ./start.sh --demo     also seeds a demo cohort if there is no database yet
# Any other arguments go to run.py, for example ./start.sh --port 8000 --lan
# NO_BROWSER=1 ./start.sh skips opening the browser.
set -e
cd "$(dirname "$0")"

DEMO=0
if [ "$1" = "--demo" ]; then DEMO=1; shift; fi
PORT=5050
prev=""
for arg in "$@"; do
  if [ "$prev" = "--port" ]; then PORT="$arg"; fi
  prev="$arg"
done

if [ ! -x .venv/bin/python ]; then
  PY="${PYTHON:-python3}"
  if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "Python 3.10 or newer is needed (found: $("$PY" --version 2>&1)). Set PYTHON=/path/to/python3." >&2
    exit 1
  fi
  echo "First run: creating .venv and installing requirements..."
  "$PY" -m venv .venv
  .venv/bin/python -m pip install --quiet --upgrade pip
  .venv/bin/python -m pip install --quiet -r requirements.txt
fi

if [ "$DEMO" = "1" ] && [ ! -f data/trainer.db ]; then
  .venv/bin/python scripts/seed_demo.py
fi

URL="http://localhost:$PORT/mission"
if [ -z "$NO_BROWSER" ]; then
  ( sleep 2; (command -v open >/dev/null && open "$URL") || (command -v xdg-open >/dev/null && xdg-open "$URL") || true ) >/dev/null 2>&1 &
fi
exec .venv/bin/python run.py "$@"
