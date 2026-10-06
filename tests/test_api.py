import json
import sqlite3

from app import scenario as scen


def post_session(client, events, scenario_id="s1-dawn-recon", callsign="viper-3", unit="4 guards", **extra):
    body = {"callsign": callsign, "unit": unit, "scenario_id": scenario_id, "events": events, **extra}
    return client.post("/api/sessions", json=body)


def first_hostile(scenario_id):
    s = scen.build_scripted(scenario_id)
    return next(c for c in s["contacts"] if c["threat"] == "hostile")


def test_list_and_get_scenarios(client):
    listed = client.get("/api/scenarios").get_json()
    assert len(listed) == 6
    one = client.get("/api/scenario?id=s2-night-loiter").get_json()
    assert one["name"] == "Night Loitering Drone"


def test_procedural_via_api_is_deterministic(client):
    a = client.get("/api/scenario?seed=31337&difficulty=4").get_json()
    b = client.get("/api/scenario?seed=31337&difficulty=4").get_json()
    assert a == b and a["id"] == "proc-31337-d4"


def test_scenario_errors(client):
    assert client.get("/api/scenario?id=nope").status_code == 404
    r = client.get("/api/scenario?seed=1&difficulty=9")
    assert r.status_code == 400 and "difficulty" in r.get_json()["error"]


def test_rubric(client):
    data = client.get("/api/rubric").get_json()
    assert data["weights"] == {"detection": 30, "classification": 30, "engagement": 40}


def test_trainees(client):
    r = client.post("/api/trainees", json={"callsign": " viper-3 ", "unit": "4 guards"})
    assert r.status_code == 201 and r.get_json()["callsign"] == "VIPER-3"
    again = client.post("/api/trainees", json={"callsign": "VIPER-3", "unit": "4 GUARDS"})
    assert again.status_code == 200 and again.get_json()["id"] == r.get_json()["id"]
    assert client.post("/api/trainees", json={"callsign": "", "unit": "X"}).status_code == 400
    assert len(client.get("/api/trainees").get_json()) == 1


def test_submit_score_store_and_read_back(client):
    c = first_hostile("s1-dawn-recon")
    t0 = c["spawn_t"]
    events = [{"t": t0 + 5, "type": "mark", "contact_id": c["id"], "data": {"via": "view"}},
              {"t": t0 + 6, "type": "classify", "contact_id": c["id"], "data": {"class": "RECON_UAS"}},
              {"t": t0 + 20, "type": "respond", "contact_id": c["id"], "data": {"response": "REPORT"}},
              {"t": t0 + 21, "type": "mark", "contact_id": None, "data": {}}]
    r = post_session(client, events, total=100, score=100)  # client-sent scores are ignored
    assert r.status_code == 201
    res = r.get_json()
    assert res["penalties"]["false_alarms"] == 1
    hostile = next(x for x in res["contacts"] if x["id"] == c["id"])
    assert hostile["path"] == ["detection/detected_fast", "classification/exact", "engagement/correct_effective"]
    assert res["total"] == 98.0  # 100 minus one false alarm

    sid = res["session_id"]
    listed = client.get("/api/sessions").get_json()
    assert listed[0]["id"] == sid and listed[0]["total"] == 98.0
    detail = client.get(f"/api/sessions/{sid}").get_json()
    assert len(detail["events"]) == 4
    assert detail["result"]["contacts"][0]["path"] == hostile["path"]
    assert client.get("/api/sessions/999").status_code == 404


def test_procedural_session(client):
    s = scen.generate({"seed": 77, "difficulty": 2})
    r = post_session(client, [], scenario_id=s["id"], params=s["params"])
    assert r.status_code == 201
    assert r.get_json()["scenario"]["id"] == "proc-77-d2"


def test_bad_input_rejected_and_database_untouched(client, app):
    before = client.get("/api/sessions").get_json()
    bad_bodies = [
        {"callsign": "A", "unit": "B", "scenario_id": "s1-dawn-recon", "events": [{"t": -5, "type": "mark"}]},
        {"callsign": "A", "unit": "B", "scenario_id": "s1-dawn-recon", "events": "x"},
        {"callsign": "A", "unit": "B", "scenario_id": "missing", "events": []},
        {"callsign": "", "unit": "B", "scenario_id": "s1-dawn-recon", "events": []},
        {"callsign": "A", "unit": "B", "scenario_id": "s1-dawn-recon", "events": [], "ended_t": "late"},
        {"callsign": "A", "unit": "B", "scenario_id": "proc-1-d1", "params": {"seed": "zz"}, "events": []},
    ]
    for body in bad_bodies:
        r = client.post("/api/sessions", json=body)
        assert r.status_code in (400, 404), body
        assert "error" in r.get_json()
    assert client.post("/api/sessions", data="not json", content_type="application/json").status_code == 400
    assert client.get("/api/sessions").get_json() == before
    conn = sqlite3.connect(app.config["DATABASE"])
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_analytics_shapes(client):
    for unit, callsign, cls in [("4 GUARDS", "VIPER-3", "RECON_UAS"), ("4 GUARDS", "VIPER-3", "BIRD"),
                                ("4 GUARDS", "HAWK-1", "RECON_UAS")]:
        c = first_hostile("s1-dawn-recon")
        post_session(client, [{"t": c["spawn_t"] + 5, "type": "mark", "contact_id": c["id"], "data": {}},
                              {"t": c["spawn_t"] + 6, "type": "classify", "contact_id": c["id"], "data": {"class": cls}}],
                     callsign=callsign, unit=unit)
    trainees = client.get("/api/trainees?unit=4 guards").get_json()
    viper = next(t for t in trainees if t["callsign"] == "VIPER-3")
    a = client.get(f"/api/analytics/trainee/{viper['id']}").get_json()
    assert len(a["sessions"]) == 2 and len(a["series"]["detection"]) == 2 and len(a["rolling"]["total"]) == 2
    assert a["confusion"]["counts"]["RECON_UAS"]["BIRD"] == 1
    assert a["confusion"]["counts"]["RECON_UAS"]["RECON_UAS"] == 1
    u = client.get("/api/analytics/unit/4 guards").get_json()
    assert u["sessions"] == 3 and u["weakest_skill"] in ("detection", "classification", "engagement")
    assert len(u["weakest_trainees"]) == 2
    assert client.get("/api/analytics/unit/nobody").status_code == 404
    assert client.get("/api/analytics/trainee/999").status_code == 404


def test_pages_render(client):
    for path in ("/mission", "/sim", "/dashboard", "/dashboard/session/1"):
        assert client.get(path).status_code == 200, path
    assert client.get("/").status_code == 302


def test_csv_exports(client):
    import csv, io
    c = first_hostile("s4-mixed-traffic")
    sid = post_session(client, [{"t": c["spawn_t"] + 3, "type": "mark", "contact_id": c["id"], "data": {}}],
                       scenario_id="s4-mixed-traffic", callsign="csv-1", unit="alpha").get_json()["session_id"]
    r = client.get(f"/api/sessions/{sid}/export.csv")
    assert r.status_code == 200 and r.mimetype == "text/csv"
    assert 'filename="session-' in r.headers["Content-Disposition"]
    rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True))))
    assert len(rows) == 5 and {row["contact"] for row in rows} >= {c["id"]}
    hostile = next(row for row in rows if row["contact"] == c["id"])
    assert hostile["detection_node"].startswith("detected") and hostile["path"].count(">") == 2

    u = client.get("/api/analytics/unit/alpha/export.csv")
    assert u.status_code == 200
    unit_rows = list(csv.DictReader(io.StringIO(u.get_data(as_text=True))))
    assert len(unit_rows) == 1 and unit_rows[0]["callsign"] == "CSV-1"
    assert client.get("/api/sessions/999/export.csv").status_code == 404
    assert client.get("/api/analytics/unit/nobody/export.csv").status_code == 404
