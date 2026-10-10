"""Browser smoke test (AVD "Testing"): load the simulator, play part of a scenario with real
keyboard and mouse input, save a session, and check the dashboard, with every non-local
request blocked. Uses the installed Google Chrome through Playwright.

Run with:  python -m pytest tests/e2e -q
"""

from pathlib import Path

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


def test_play_score_and_review(page, server):
    SHOTS.mkdir(exist_ok=True)
    page.goto(f"{server}/mission")
    page.wait_for_selector(".card")
    assert page.locator(".card").count() == 6
    page.fill("#callsign", "smoke-1")
    page.fill("#unit", "test unit")
    page.uncheck("#vary")  # the standard Dawn Recon, so the drone appears where this test looks
    page.click("button.select[data-id='s1-dawn-recon']")
    page.screenshot(path=SHOTS / "01-mission.png")
    page.click("#launch")

    page.wait_for_selector("#begin")
    page.screenshot(path=SHOTS / "02-briefing.png")
    page.keyboard.press("Enter")

    # Turn right toward bearing ~40 degrees, where the recon quadcopter appears at T+10 s.
    page.locator("#view").focus()
    page.keyboard.down("ArrowRight")
    page.wait_for_timeout(1000)
    page.keyboard.up("ArrowRight")
    page.keyboard.press("s")  # sensor mode: night vision
    page.keyboard.press("s")  # thermal
    page.keyboard.press("s")  # back to EO
    page.wait_for_function("window.__sim.t > 24", timeout=40_000)

    # Click the contact where it is drawn, exactly as a trainee would.
    pos = page.evaluate("""() => {
        const S = window.__sim, m = S.world.meshes.get('C1');
        const v = m.position.clone().project(S.world.camera);
        const r = document.getElementById('view').getBoundingClientRect();
        return {x: r.left + (v.x + 1) / 2 * r.width, y: r.top + (1 - v.y) / 2 * r.height, visible: m.visible, z: v.z};
    }""")
    assert pos["visible"] and pos["z"] < 1
    page.mouse.click(pos["x"], pos["y"])
    page.wait_for_function("window.__sim.marked.has('C1')")
    page.keyboard.press("1")  # classify: recon quadcopter
    page.keyboard.press("r")  # respond: report
    page.wait_for_timeout(1500)
    page.screenshot(path=SHOTS / "03-sim-marked.png")
    fps = int(page.inner_text("#fps"))

    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#again", timeout=15_000)
    page.screenshot(path=SHOTS / "04-score.png", full_page=True)
    text = page.inner_text("#screen-card").lower()
    assert "detection/detected" in text and "classification/exact" in text
    assert "composite score" in text

    session = page.evaluate("fetch('/api/sessions').then(r => r.json())")[0]
    assert session["callsign"] == "SMOKE-1"

    page.goto(f"{server}/dashboard/session/{session['id']}")
    page.wait_for_selector(".timeline li .what")
    page.screenshot(path=SHOTS / "05-session.png", full_page=True)
    page.goto(f"{server}/dashboard")
    page.wait_for_selector("#confusion td")
    page.screenshot(path=SHOTS / "06-dashboard.png", full_page=True)

    assert page.errors == []
    assert page.external == []
    assert fps >= 30, f"frame rate {fps} fps"


def test_radar_console_tracks_and_marking(page, server):
    """Radar: tracks form from sweeps, the console shows a scope and track table, and a
    click on a track marks that contact via the radar."""
    SHOTS.mkdir(exist_ok=True)
    page.goto(f"{server}/sim?callsign=radar-1&unit=test&id=s4-mixed-traffic")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.locator("#view").focus()
    page.keyboard.press("q")
    assert page.is_visible("#radar-big") and page.is_visible("#track-table")
    page.wait_for_function("window.__sim.radar.tracks.size >= 2 && window.__sim.t > 32", timeout=60_000)
    page.wait_for_selector("#track-table tbody tr")
    page.screenshot(path=SHOTS / "07-radar-console.png")

    status = page.inner_text("#radar-status")
    assert "TRK" in status and "30 RPM" in status
    # The radar never shows the true class: no class names in the track table.
    table = page.inner_text("#track-table").lower()
    assert "bird" not in table and "friendly aircraft" not in table and "quadcopter" not in table

    # Click the first track on the big scope, exactly where it is drawn.
    target = page.evaluate("""() => {
        const S = window.__sim, cv = document.getElementById('radar-big');
        const p = S.radar.picks.get(cv).find(p => p.kind === 'track' && p.contactId);
        const r = cv.getBoundingClientRect();
        return {x: r.left + p.x, y: r.top + p.y, id: p.contactId};
    }""")
    page.mouse.click(target["x"], target["y"])
    page.wait_for_function(f"window.__sim.marked.has('{target['id']}')")
    marks = page.evaluate("window.__sim.events.filter(e => e.type === 'mark')")
    assert marks[-1]["contact_id"] == target["id"] and marks[-1]["data"]["via"] == "radar"

    page.keyboard.press("]")
    assert page.evaluate("window.__sim.radar.scale") == 6000
    page.wait_for_timeout(600)
    page.screenshot(path=SHOTS / "08-radar-6km.png")
    page.keyboard.press("q")  # back to the optical view
    assert not page.is_visible("#radar-big") and page.is_visible("#radar")
    sensors = [e["data"]["mode"] for e in page.evaluate("window.__sim.events") if e["type"] == "sensor"]
    assert sensors == ["radar", "eo"]
    assert page.errors == [] and page.external == []
