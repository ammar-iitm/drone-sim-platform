"""Shared browser-test fixtures: a live server on a temporary database and the installed Chrome.
Every non-local request is blocked and recorded, and console errors are collected."""

import threading
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")
from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    app = create_app({"DATABASE": str(tmp_path_factory.mktemp("e2e") / "e2e.db")})
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="chrome", headless=True)
        except Exception as exc:  # pragma: no cover - depends on the machine
            pytest.skip(f"Chrome not available: {exc}")
        yield b
        b.close()


@pytest.fixture
def page(browser, server, request):
    opts = getattr(request, "param", {})
    ctx = browser.new_context(**{"viewport": {"width": 1600, "height": 960}, **opts})  # a test may override the size
    pg = ctx.new_page()
    pg.errors, pg.external = [], []
    pg.on("console", lambda m: m.type == "error" and pg.errors.append(m.text))
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))

    def route(r):
        if r.request.url.startswith(server):
            r.continue_()
        else:
            pg.external.append(r.request.url)
            r.abort()

    pg.route("**/*", route)
    yield pg
    ctx.close()


