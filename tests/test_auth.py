"""Instructor login (app/auth.py): off by default; when a password is set, results need a login
and trainees can still play."""

import pytest

from app import create_app

from test_api import first_hostile, post_session

PROTECTED_API = ["/api/trainees", "/api/sessions", "/api/sessions/1", "/api/sessions/1/export.csv",
                 "/api/analytics/trainee/1", "/api/analytics/unit/4%20GUARDS",
                 "/api/analytics/unit/4%20GUARDS/export.csv"]
PROTECTED_PAGES = ["/dashboard", "/dashboard/session/1"]
OPEN = ["/mission", "/sim", "/help", "/api/scenarios", "/api/rubric", "/api/scenario?id=s1-dawn-recon"]


@pytest.fixture
def locked(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "a.db"), "TESTING": True, "INSTRUCTOR_PASSWORD": "kestrel-7"})
    c = app.test_client()
    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    assert post_session(c, events, unit="4 guards").status_code == 201  # trainees can still save
    return app, c


def test_login_is_off_by_default(client):
    for path in PROTECTED_PAGES[:1] + PROTECTED_API[:2]:
        assert client.get(path).status_code == 200, path
    assert client.get("/login").status_code == 302  # nothing to log in to


def test_results_need_an_instructor_login(locked):
    _, c = locked
    for path in PROTECTED_API:
        r = c.get(path)
        assert r.status_code == 401 and r.get_json()["error"] == "instructor login required", path
    for path in PROTECTED_PAGES:
        r = c.get(path)
        assert r.status_code == 302 and "/login?next=" in r.headers["Location"], path
    for path in OPEN:
        assert c.get(path).status_code == 200, path


def test_login_logout_and_wrong_password(locked):
    _, c = locked
    r = c.post("/login", data={"password": "wrong", "next": "/dashboard"})
    assert r.status_code == 401 and "not right" in r.get_data(as_text=True)
    assert c.get("/api/sessions").status_code == 401

    r = c.post("/login", data={"password": "kestrel-7", "next": "/dashboard/session/1"})
    assert r.status_code == 302 and r.headers["Location"].endswith("/dashboard/session/1")
    for path in PROTECTED_API + PROTECTED_PAGES:
        assert c.get(path).status_code == 200, path
    assert "Log out" in c.get("/dashboard").get_data(as_text=True)

    c.post("/logout")
    assert c.get("/api/sessions").status_code == 401


def test_login_never_redirects_off_site(locked):
    _, c = locked
    for bad in ("https://evil.example/", "//evil.example/x", "javascript:alert(1)"):
        r = c.post("/login", data={"password": "kestrel-7", "next": bad})
        assert r.headers["Location"].endswith("/dashboard"), bad


def test_session_key_is_shared_across_instances(tmp_path):
    """Serverless instances derive the same signing key from the password, so a login made on one
    instance is honoured by another."""
    cfg = {"TESTING": True, "INSTRUCTOR_PASSWORD": "kestrel-7"}
    a = create_app({"DATABASE": str(tmp_path / "a.db"), **cfg})
    b = create_app({"DATABASE": str(tmp_path / "a.db"), **cfg})
    assert a.config["SECRET_KEY"] == b.config["SECRET_KEY"]
    ca = a.test_client()
    ca.post("/login", data={"password": "kestrel-7"})
    cookie = ca.get_cookie("session")
    cb = b.test_client()
    cb.set_cookie("session", cookie.value)
    assert cb.get("/api/sessions").status_code == 200


def test_login_cookie_is_short_lived_and_same_site(locked):
    _, c = locked
    r = c.post("/login", data={"password": "kestrel-7"})
    cookie = r.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
    from email.utils import parsedate_to_datetime
    from datetime import datetime, timezone
    expires = parsedate_to_datetime(cookie.split("Expires=")[1].split(";")[0])
    hours = (expires - datetime.now(timezone.utc)).total_seconds() / 3600
    assert 11.9 < hours <= 12
