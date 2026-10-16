"""Browser checks for swarm avoidance, audio behaviour, motion cues, the comparison chart,
focus rings, a keyboard-only full scenario, and a greyscale render for colour-blind review."""

from pathlib import Path

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


def begin(page, server, query):
    page.goto(f"{server}/sim?callsign=finish&unit=checks&{query}")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.locator("#view").focus()


def test_swarm_keeps_separation_and_spreads_when_engaged(page, server):
    begin(page, server, "id=s6-saturation-swarm&speed=8")
    page.evaluate("""() => {
        const S = window.__sim, A = window.__simApi;
        S.minSep = Infinity; S.spreadBefore = null; S.spreadAfter = null; S.engagedAt = null;
        const spread = (g) => {
            const ms = S.scenario.contacts.filter(c => c.swarm && c.swarm.group === g && A.isAlive(c, S.t))
                .map(c => S.world.meshes.get(c.id).position);
            if (ms.length < 2) return null;
            const cx = ms.reduce((a, p) => a + p.x, 0) / ms.length, cz = ms.reduce((a, p) => a + p.z, 0) / ms.length;
            return ms.reduce((a, p) => a + Math.hypot(p.x - cx, p.z - cz), 0) / ms.length;
        };
        setInterval(() => {
            for (const g of ['A', 'B']) {
                const ms = S.scenario.contacts.filter(c => c.swarm && c.swarm.group === g && A.isAlive(c, S.t))
                    .map(c => S.world.meshes.get(c.id).position);
                for (let i = 0; i < ms.length; i++) for (let j = i + 1; j < ms.length; j++)
                    S.minSep = Math.min(S.minSep, ms[i].distanceTo(ms[j]));
            }
            const lead = S.scenario.contacts.find(c => c.swarm && c.swarm.group === 'A');
            if (S.engagedAt === null && A.isAlive(lead, S.t) && A.range(lead.id) < 1300) {
                S.spreadBefore = spread('A');
                A.mark(lead.id); A.select(lead.id); A.respond('JAM');
                S.engagedAt = S.t;
            }
            if (S.engagedAt !== null && S.spreadAfter === null && S.t > S.engagedAt + 4) S.spreadAfter = spread('A');
        }, 20);
    }""")
    page.wait_for_function("window.__sim.spreadAfter !== null", timeout=60_000)
    min_sep, before, after = page.evaluate("[window.__sim.minSep, window.__sim.spreadBefore, window.__sim.spreadAfter]")
    assert min_sep >= 20, f"members came within {min_sep:.1f} m"
    assert after > before + 15, (before, after)
    assert page.errors == []


def test_audio_cues_and_mute(page, server):
    begin(page, server, "id=s1-dawn-recon&speed=8")
    page.evaluate("""() => {
        const s = window.__sim.sound; s.calls = [];
        const tone = s.tone.bind(s);
        s.tone = (f, ...rest) => { s.calls.push(Math.round(f)); return tone(f, ...rest); };
    }""")
    assert page.evaluate("window.__sim.sound.ctx.state") == "running"
    assert page.evaluate("window.__sim.sound.humGain.gain.value") < 0.01  # no drone yet
    page.wait_for_function("window.__simApi.isAlive(window.__sim.scenario.contacts[0], window.__sim.t) && window.__simApi.range('C1') < 1000", timeout=60_000)
    page.wait_for_timeout(500)
    near = page.evaluate("window.__sim.sound.humGain.gain.value")
    assert near > 0.02, near  # rotor hum rises as the drone closes

    page.evaluate("() => { const A = window.__simApi; A.mark('C1'); A.select('C1'); A.respond('REPORT'); }")
    box = page.locator("#view").bounding_box()
    page.mouse.click(box["x"] + 40, box["y"] + 40)  # empty sky: failure buzz
    calls = page.evaluate("window.__sim.sound.calls")
    assert 1400 in calls and 1046 in calls and 1318 in calls and 220 in calls, calls

    page.keyboard.press("m")
    page.wait_for_timeout(400)
    assert page.evaluate("window.__sim.sound.master.gain.value") < 0.005
    assert "sound off" in page.inner_text("#btn-mute").lower()
    page.keyboard.press("m")
    page.wait_for_timeout(400)
    assert page.evaluate("window.__sim.sound.master.gain.value") > 0.1
    assert page.errors == []


def test_breach_alarm_sounds(page, server):
    begin(page, server, "id=s3-urban-canyon&speed=16")
    page.evaluate("() => { const s = window.__sim.sound; s.calls = []; const tone = s.tone.bind(s); s.tone = (f, ...r) => { s.calls.push(Math.round(f)); return tone(f, ...r); }; }")
    page.wait_for_function("window.__sim.events.some(e => e.type === 'breach')", timeout=60_000)
    calls = page.evaluate("window.__sim.sound.calls")
    assert calls.count(880) == 2 and calls.count(660) == 2, calls  # two-tone alarm


def test_motion_cues_differ_by_type(page, server):
    begin(page, server, "id=s4-mixed-traffic&speed=4")
    page.wait_for_function("window.__sim.t > 46", timeout=60_000)
    stats = page.evaluate("""() => new Promise((resolve) => {
        const S = window.__sim, A = window.__simApi, ids = { bird: 'C1', friendly: 'C3', quad: 'C4' };
        const dev = { bird: [], friendly: [], quad: [] }, wing = new Set(), nav = new Set();
        const pathPos = (c, t) => {
            let left = (t - c.spawn_t) * c.speed_mps; const w = c.waypoints;
            for (let i = 0; i < w.length - 1; i++) {
                const d = Math.hypot(w[i+1][0]-w[i][0], w[i+1][1]-w[i][1], w[i+1][2]-w[i][2]);
                if (left <= d) { const f = left / d; return [0, 1, 2].map(k => w[i][k] + (w[i+1][k]-w[i][k]) * f); }
                left -= d;
            }
            return null;
        };
        let n = 0;
        const timer = setInterval(() => {
            for (const [k, id] of Object.entries(ids)) {
                const c = A.contactById(id), m = S.world.meshes.get(id);
                if (!A.isAlive(c, S.t)) continue;
                const p = pathPos(c, S.t);
                if (p) dev[k].push(Math.hypot(m.position.x - p[0], m.position.y - p[1], m.position.z - p[2]));
            }
            const b = S.world.meshes.get('C1');
            if (b.userData.wings) wing.add(b.userData.wings[0].rotation.z.toFixed(2));
            nav.add(S.world.meshes.get('C3').userData.nav.visible);
            if (++n > 60) {
                clearInterval(timer);
                const max = (a) => a.length ? Math.max(...a) : null;
                resolve({ bird: max(dev.bird), friendly: max(dev.friendly), quad: max(dev.quad), wing: wing.size, nav: [...nav] });
            }
        }, 50);
    })""")
    assert stats["bird"] > 3 and stats["quad"] is not None and stats["bird"] > stats["quad"], stats   # erratic bird
    assert stats["friendly"] is not None and stats["friendly"] < 0.5, stats                          # steady aircraft
    assert stats["wing"] > 5, stats                                                                  # wings flap
    assert set(stats["nav"]) == {True, False}, stats                                                 # nav light blinks


def test_comparison_chart_and_focus_rings(page, server):
    for callsign in ("cmp-1", "cmp-2"):
        page.request.post(f"{server}/api/sessions", data={"callsign": callsign, "unit": "compare",
                          "scenario_id": "s1-dawn-recon", "events": [{"t": 20, "type": "mark", "contact_id": "C1", "data": {}}]})
    page.goto(f"{server}/dashboard")
    page.wait_for_selector("#compare-table", state="attached")
    page.select_option("#unit", "COMPARE")
    page.wait_for_function("Chart.getChart(document.getElementById('compare')).data.labels.length === 2")
    box = page.locator("#compare").bounding_box()
    page.mouse.move(box["x"] + box["width"] * 0.3, box["y"] + box["height"] * 0.3)
    page.wait_for_timeout(300)
    assert page.evaluate("Chart.getChart(document.getElementById('compare')).tooltip.getActiveElements().length") >= 1
    panel = page.locator(".panel", has=page.locator("#compare"))
    panel.locator("button[data-view='table']").click()
    assert page.locator("#compare-table tbody tr").count() == 2

    page.keyboard.press("Tab")
    for _ in range(25):
        style = page.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
            const s = getComputedStyle(e); return [e.tagName, s.outlineStyle, parseFloat(s.outlineWidth)]; }""")
        if style:
            assert style[1] != "none" and style[2] >= 2, style
        page.keyboard.press("Tab")


def test_keyboard_only_full_scenario(page, server):
    begin(page, server, "id=s1-dawn-recon&speed=8")
    page.keyboard.press("q")
    page.wait_for_function("window.__sim.radar.tracks.size > 0", timeout=60_000)
    page.keyboard.press(" ")
    page.keyboard.press("1")
    page.keyboard.press("r")
    page.wait_for_selector("#again", timeout=60_000)  # the scenario runs to its natural end
    sid = page.evaluate("fetch('/api/sessions').then(r => r.json())")[0]["id"]
    c = page.evaluate(f"fetch('/api/sessions/{sid}').then(r => r.json())")["result"]["contacts"][0]
    assert c["path"] == ["detection/" + c["detection"]["node"], "classification/exact", "engagement/correct_effective"]
    assert c["detection"]["node"].startswith("detected")
    assert page.errors == []


def test_greyscale_render_for_colour_blind_review(page, server):
    begin(page, server, "id=s4-mixed-traffic&speed=8")
    page.wait_for_function("['C1','C2','C3','C4'].every(id => window.__simApi.isAlive(window.__simApi.contactById(id), window.__sim.t))", timeout=60_000)
    page.evaluate("""() => {
        const A = window.__simApi;
        A.mark('C1'); A.classify('BIRD');        // benign: grey square
        A.mark('C3'); A.classify('FRIENDLY');    // friendly: blue circle
        A.mark('C4'); A.classify('RECON_UAS');   // hostile: red triangle
        A.mark('C2');                            // unknown: amber diamond
    }""")
    page.keyboard.press("q")
    page.wait_for_timeout(2500)
    page.add_style_tag(content="html { filter: grayscale(1) !important; }")
    page.wait_for_timeout(300)
    page.screenshot(path=SHOTS / "13-greyscale-markers.png")
    badges = page.locator("#contacts .badge").all_inner_texts()
    assert sorted(b.strip() for b in badges) == ["BENIGN", "FRIENDLY", "HOSTILE", "UNKNOWN"]


def test_quality_levels_and_auto_step_down(page, server):
    begin(page, server, "seed=7&difficulty=5&swarm=12&degradation=0&terrain=urban&quality=low")
    low = page.evaluate("[window.__sim.world.renderer.getPixelRatio(), window.__sim.world.scenery.map(s => [s.mesh.count, s.total])]")
    assert low[0] <= 0.75
    assert all(abs(c - round(t * 0.35)) <= 1 for c, t in low[1])
    assert "LOW" in page.inner_text("#quality")

    begin(page, server, "seed=7&difficulty=5&swarm=12&degradation=0&terrain=urban")
    assert "AUTO" in page.inner_text("#quality") and "HIGH" in page.inner_text("#quality")
    page.evaluate("for (let i = 0; i < 5; i++) window.__sim.autoQuality(20)")
    assert page.evaluate("window.__sim.world.quality") == "high"           # 2.5 s of low fps: no change yet
    page.evaluate("window.__sim.autoQuality(20)")
    assert page.evaluate("window.__sim.world.quality") == "medium"         # 3 s: one step down
    page.evaluate("for (let i = 0; i < 6; i++) window.__sim.autoQuality(60)")
    assert page.evaluate("window.__sim.world.quality") == "medium"         # never steps back up
    page.evaluate("for (let i = 0; i < 6; i++) window.__sim.autoQuality(20)")
    assert page.evaluate("window.__sim.world.quality") == "low"
    page.evaluate("for (let i = 0; i < 12; i++) window.__sim.autoQuality(20)")
    assert page.evaluate("window.__sim.world.quality") == "minimum"        # and stops at minimum
    page.wait_for_function("document.getElementById('quality').textContent.includes('MINIMUM')")
    lowest = page.evaluate("[window.__sim.world.renderer.getPixelRatio(), window.__sim.world.scenery.map(s => [s.mesh.count, s.total])]")
    assert lowest[0] <= 0.5
    assert all(abs(c - max(1, round(t * 0.2))) <= 1 for c, t in lowest[1])

    assert page.errors == []


def test_help_page_shows_live_rubric(page, server):
    page.goto(f"{server}/help")
    page.wait_for_selector("#t-responses tbody tr")
    text = page.inner_text("main").lower()
    for phrase in ("quick start", "threat markers", "detected fast", "critical misclassification",
                   "restraint", "grade a", "fixed wing", "intercept (hard kill) chance"):
        assert phrase in text, phrase
    assert page.locator("#t-responses tbody tr").count() == 6
    rubric = page.evaluate("fetch('/api/rubric').then(r => r.json())")
    assert f"× {rubric['weights']['engagement']}" in page.inner_text("#flow")
    assert page.errors == [] and page.external == []


def test_unsaved_session_is_kept_and_resent(page, server):
    begin(page, server, "id=s1-dawn-recon&speed=16")
    page.wait_for_function("window.__sim.t > 15")
    # Simulate the server being unreachable for the save.
    page.route("**/api/sessions", lambda r: r.abort() if r.request.method == "POST" else r.continue_())
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#retry")
    assert "kept in this browser" in page.inner_text("#screen-card")
    assert len(page.evaluate("JSON.parse(localStorage.getItem('dtt.unsent'))")) == 1
    before = len(page.evaluate("fetch('/api/sessions').then(r => r.json())"))
    page.unroute("**/api/sessions")

    page.goto(f"{server}/mission")
    page.wait_for_selector("#unsent:not([hidden])")
    assert "1 session not yet saved" in page.inner_text("#unsent-text")
    page.click("#unsent-send")
    page.wait_for_function("document.getElementById('unsent-text').textContent.includes('All saved sessions sent')")
    assert "session" in page.inner_text("#unsent-result").lower()
    assert len(page.evaluate("fetch('/api/sessions').then(r => r.json())")) == before + 1
    assert page.evaluate("JSON.parse(localStorage.getItem('dtt.unsent'))") == []
