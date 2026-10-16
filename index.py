"""Vercel entrypoint: Vercel's Python runtime serves the Flask `app` defined here.

On Vercel the database must be Postgres (set DATABASE_URL, e.g. from the Neon integration),
because the function's disk does not persist. Locally, use run.py or start.sh instead.
"""

from app import create_app
from app.vercel import DecodePath

app = create_app()
app.wsgi_app = DecodePath(app.wsgi_app)
