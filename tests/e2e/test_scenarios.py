"""Play all six scripted scenarios end to end (checklist "Scenarios") at x16 fast-forward,
both the standard version and a varied run.

A scripted trainee in the page calls the same decision functions the keyboard and mouse
call (window.__simApi), making the choices each scenario is meant to test. The server
then scores the saved session and we check the decision-tree outcome.
"""

from pathlib import Path

import pytest

SHOTS = Path(__file__).resolve().parents[2] / "test-results"

BOT = """(cfg) => {
  const S = window.__sim, A = window.__simApi, seen = new Map();
  setInterval(() => {
    if (S.phase !== 'running') return;
    for (const c of S.scenario.contacts) {
      if (!A.isAlive(c, S.t)) continue;
      const hostile = c.threat === 'hostile';
      if (!hostile && !cfg.nonHostile) continue;
      const r = A.range(c.id);
      const st = seen.get(c.id) || { tries: 0, last: -99 };
      seen.set(c.id, st);
      if (!S.marked.has(c.id)) {
        const visible = cfg.radarOnly ? S.radar.tracks.has(c.id) : r < (cfg.markRange || 1400);
        if (!visible) continue;
        A.mark(c.id);
        A.classify(c.true_class);
      }
      const plan = hostile ? cfg.plan[c.model] || cfg.plan.default : cfg.nonHostile[c.threat];
      if (!plan || st.tries >= plan.length || r > 1300 || S.t - st.last < 2) continue;
      if (hostile && r < 400) continue;
      A.select(c.id);
      A.respond(plan[st.tries]);
      st.tries += 1;
      st.last = S.t;
      if (S.status.get(c.id).neutralisedT !== null) st.tries = plan.length;
    }
  }, 40);
}"""

INTERCEPT3 = ["INTERCEPT", "INTERCEPT", "INTERCEPT"]

CASES = {
    "s1-dawn-recon": {"plan": {"default": ["REPORT"]}},
    "s2-night-loiter": {"plan": {"default": ["JAM", "INTERCEPT", "INTERCEPT"]}},
    "s3-urban-canyon": {"plan": {"default": INTERCEPT3}, "markRange": 900},
    "s4-mixed-traffic": {"plan": {"default": INTERCEPT3}, "nonHostile": {"benign": ["TRACK"], "friendly": ["JAM"]}},
    "s5-fog-noise": {"plan": {"default": INTERCEPT3}, "radarOnly": True},
    "s6-saturation-swarm": {"plan": {"default": INTERCEPT3}, "nonHostile": {"decoy": ["TRACK"]}},
}


def play(page, server, scenario_id, cfg, vary=None):
    extra = f"&vary={vary}" if vary else ""
    page.goto(f"{server}/sim?callsign=bot&unit=e2e&id={scenario_id}&speed=16{extra}")
    page.wait_for_selector("#begin")
    briefing = page.inner_text("#screen-card")
    page.keyboard.press("Enter")
    page.evaluate(BOT, cfg)
    page.wait_for_selector("#again", timeout=90_000)
    sid = page.evaluate("fetch('/api/sessions').then(r => r.json())")[0]["id"]
    detail = page.evaluate(f"fetch('/api/sessions/{sid}').then(r => r.json())")
    return briefing, detail


@pytest.mark.parametrize("vary", [None, 4242], ids=["standard", "variant"])
@pytest.mark.parametrize("scenario_id", list(CASES))
def test_scenario_plays_end_to_end(page, server, scenario_id, vary):
    """Each learning objective holds in the standard scenario and in a varied run."""
    briefing, detail = play(page, server, scenario_id, CASES[scenario_id], vary)
    assert detail["params"] == ({"vary": vary} if vary else None)
    result = detail["result"]
    by_threat = lambda t: [c for c in result["contacts"] if c["threat"] == t]  # noqa: E731
    hostiles = by_threat("hostile")

    assert "learning objective" in briefing.lower()
    assert all(len(c["path"]) == 3 for c in hostiles)
    assert page.errors == [] and page.external == []

    if scenario_id == "s1-dawn-recon":
        assert hostiles[0]["engagement"]["node"] == "correct_effective"
        assert result["total"] >= 80
    elif scenario_id == "s2-night-loiter":
        c = hostiles[0]
        assert c["attempts"][0]["response"] == "JAM" and c["attempts"][0]["effectiveness"] <= 0.1
        assert c["engagement"]["node"] in ("unsuitable", "breach")
        assert "Intercept" in c["engagement"]["reason"] or c["engagement"]["node"] == "breach"
    elif scenario_id == "s3-urban-canyon":
        assert hostiles[0]["detection"]["node"].startswith("detected")
    elif scenario_id == "s4-mixed-traffic":
        friendly = by_threat("friendly")[0]
        assert friendly["engagement"]["node"] == "friendly_engaged"
        assert result["penalties"]["critical_errors"] >= 1
        assert all(b["engagement"]["node"] == "restraint" for b in by_threat("benign") if b["scored"])
    elif scenario_id == "s5-fog-noise":
        marks = [e for e in detail["events"] if e["type"] == "mark"]
        assert marks and all(e["data"].get("via") == "radar" for e in marks)
        assert all(c["detection"]["node"].startswith("detected") for c in hostiles)
    elif scenario_id == "s6-saturation-swarm":
        assert len(hostiles) == 8
        assert sum(c["detection"]["node"].startswith("detected") for c in hostiles) >= 6
        assert all(d["engagement"]["node"] == "restraint" for d in by_threat("decoy") if d["scored"])


def test_session_replay(page, server):
    """AAR replay: the review page rebuilds the scenario the trainee flew (here a variant), plays
    it back on a map, and clicking an event jumps the replay to that moment."""
    _, detail = play(page, server, "s2-night-loiter", CASES["s2-night-loiter"], vary=31)
    page.goto(f"{server}/dashboard/session/{detail['id']}")
    page.wait_for_function("window.__replay")
    rp = page.evaluate("({ n: window.__replay.contacts.length, vary: window.__replay.scenario.params,"
                       " end: window.__replay.duration })")
    assert rp["vary"] == {"vary": 31} and rp["n"] == len(detail["result"]["contacts"]) and rp["end"] > 0

    jam = next(e for e in detail["result"]["timeline"] if e["type"] == "respond")
    page.locator(f"#timeline li[data-t='{jam['t']}']").first.click()
    assert page.evaluate("window.__replay.t") == pytest.approx(jam["t"])
    assert "JAM" in page.inner_text(".replay-caption").upper()

    page.locator("[data-act=play]").click()
    page.wait_for_timeout(600)
    assert page.evaluate("window.__replay.t") > jam["t"]       # playing moves time forward
    page.keyboard.press("Space")                               # Space pauses
    t = page.evaluate("window.__replay.t")
    page.wait_for_timeout(300)
    assert page.evaluate("window.__replay.t") == t
    page.locator(".replay-scrub").fill("0")
    assert page.evaluate("window.__replay.t") == 0
    assert page.errors == [] and page.external == []
    page.locator("#replay").screenshot(path=SHOTS / "14-replay.png")
