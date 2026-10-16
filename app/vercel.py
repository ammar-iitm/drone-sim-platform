"""Adjustments that only apply when the app runs on Vercel (used by index.py)."""

from urllib.parse import unquote


class DecodePath:
    """Vercel's Python runtime hands Flask PATH_INFO still percent-encoded ("/unit/4%20GUARDS"),
    where WSGI servers normally decode it, so every route with a space in a path segment would
    miss. Decode it once here, the way a WSGI server would: percent-escapes become raw bytes
    held as latin-1 characters, and Werkzeug then reads them as UTF-8."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if "%" in path:
            environ["PATH_INFO"] = unquote(path, encoding="latin-1")
        return self.wsgi_app(environ, start_response)
