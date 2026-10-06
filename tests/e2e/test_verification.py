"""Browser checks for the remaining checklist items: controls, false alarms, breaches, sensor
modes, degradation, radar behaviour, instructor settings, seed reuse, dashboard interaction,
the Urban Canyon and Fog and Noise learning objectives, and the contact silhouettes."""

import json
from pathlib import Path

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


def begin(page, server, query):
    page.goto(f"{server}/sim?callsign=verify&unit=checks&{query}")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.locator("#view").focus()


def finish_and_result(page):
    page.wait_for_selector("#again", timeout=60_000)
    sid = page.evaluate("fetch('/api/sessions').then(r => r.json())")[0]["id"]
    return page.evaluate(f"fetch('/api/sessions/{sid}').then(r => r.json())")


def test_look_and_zoom_by_mouse_and_keyboard(page, server):
    begin(page, server, "id=s4-mixed-traffic")
    box = page.locator("#view").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    yaw0 = page.evaluate("window.__sim.yaw")
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx - 300, cy + 60, steps=12)
    page.mouse.up()
    yaw1 = page.evaluate("window.__sim.yaw")
    assert yaw1 > yaw0 + 20  # dragging left turns the view right ("grab the world")
    page.keyboard.down("ArrowLeft")
    page.wait_for_timeout(500)
    page.keyboard.up("ArrowLeft")
    assert page.evaluate("window.__sim.yaw") < yaw1 - 10
    page.mouse.move(cx, cy)
    page.mouse.wheel(0, -200)
    page.wait_for_timeout(100)
    assert page.evaluate("[window.__sim.zoomIdx, window.__sim.world.camera.fov]") == [1, 30]
    page.keyboard.press("+")
    assert page.evaluate("window.__sim.world.camera.fov") == 15
    page.keyboard.press("-")
    page.keyboard.press("-")
    assert page.evaluate("window.__sim.world.camera.fov") == 60
    page.wait_for_function("document.getElementById('zoom').textContent === 'ZOOM 1x'")  # HUD redraws next frame
    assert page.errors == []


def test_false_alarm_and_breach(page, server):
    begin(page, server, "id=s3-urban-canyon&speed=16")
    box = page.locator("#view").bounding_box()
    page.mouse.click(box["x"] + 60, box["y"] + 60)  # empty sky
    page.wait_for_function("window.__sim.events.some(e => e.type === 'mark' && e.contact_id === null)")
    page.wait_for_function("window.__sim.events.some(e => e.type === 'breach')", timeout=60_000)
    assert page.is_visible("#alert") and "breach" in page.inner_text("#alert").lower()
    detail = finish_and_result(page)
    pen = detail["result"]["penalties"]
    assert pen["false_alarms"] == 1 and pen["breaches"] == 1
    assert page.errors == []


def test_sensor_modes_differ_and_switch_fast(page, server):
    begin(page, server, "id=s4-mixed-traffic")
    page.wait_for_timeout(1500)
    shots, filters, times = {}, {}, {}
    for mode in ("eo", "nv", "thermal"):
        if mode != "eo":
            times[mode] = page.evaluate("""() => new Promise((resolve) => {
                const t0 = performance.now();
                document.dispatchEvent(new KeyboardEvent('keydown', { key: 's' }));
                requestAnimationFrame(() => requestAnimationFrame(() => resolve(performance.now() - t0)));
            })""")
        page.wait_for_timeout(300)
        filters[mode] = page.evaluate("getComputedStyle(document.getElementById('gl')).filter")
        shots[mode] = page.locator("#view").screenshot(path=SHOTS / f"10-sensor-{mode}.png")
    assert len(set(filters.values())) == 3
    assert len({s for s in shots.values()}) == 3
    assert all(ms < 1000 for ms in times.values()), times
    assert page.inner_text("#sensor-readout") == "THERMAL"


def test_four_degradation_levels_in_the_view(page, server):
    expected = {0: 3000, 1: 2200, 2: 1500, 3: 900}
    for level, vis in expected.items():
        begin(page, server, f"seed=99&difficulty=2&degradation={level}")
        page.wait_for_timeout(400)
        far, env = page.evaluate("[window.__sim.world.scene.fog.far, window.__sim.scenario.environment]")
        assert env["visual_range_m"] == vis and abs(far - vis * 1.05) < 1e-6
        assert (env["noise"] > 0) == (level > 0) and (env["radar_dropout"] > 0) == (level > 0)
        if level == 3:
            page.locator("#view").screenshot(path=SHOTS / "11-degradation-3.png")
    assert page.errors == []


def test_radar_latency_and_noise(page, server):
    begin(page, server, "id=s4-mixed-traffic&speed=4")
    page.wait_for_function("window.__sim.radar.tracks.has('C3')", timeout=60_000)  # the friendly aircraft
    samples = []
    for _ in range(8):
        page.wait_for_timeout(300)
        samples.append(page.evaluate("""() => {
            const S = window.__sim, tr = S.radar.tracks.get('C3');
            if (!tr) return null;
            const c = S.scenario.contacts.find(c => c.id === 'C3');
            const w = c.waypoints, d = Math.hypot(w[1][0]-w[0][0], w[1][1]-w[0][1], w[1][2]-w[0][2]);
            const f = (tr.t - c.spawn_t) * c.speed_mps / d;
            const x = w[0][0] + (w[1][0]-w[0][0]) * f, z = w[0][2] + (w[1][2]-w[0][2]) * f;
            return { t: tr.t, now: S.t, err: Math.hypot(tr.x - x, tr.z - z) };
        }"""))
    samples = [s for s in samples if s]
    update_times = sorted({round(s["t"], 2) for s in samples})
    gaps = [b - a for a, b in zip(update_times, update_times[1:])]
    assert gaps and all(abs(g - round(g / 2) * 2) < 0.2 for g in gaps)      # updates once per 2 s sweep
    assert max(s["now"] - s["t"] for s in samples) > 0.5                     # the picture lags reality
    assert all(0 < s["err"] < 250 for s in samples)                          # noisy, but on the target


def test_instructor_settings_and_seed_reuse(page, server):
    page.goto(f"{server}/mission")
    page.wait_for_selector(".card")
    page.fill("#callsign", "instructor-1")
    page.fill("#unit", "checks")
    page.fill("#seed", "777")
    page.locator("#difficulty").fill("4")
    page.select_option("#time_of_day", "night")
    page.select_option("#terrain", "urban")
    page.select_option("#degradation", "2")
    for name, value in {"swarm": "6", "hostile": "2", "decoy": "1", "benign": "1", "friendly": "0"}.items():
        page.fill(f"#{name}", value)
    page.click("#use-proc")
    page.wait_for_function("document.getElementById('selected-name').textContent.includes('NIGHT, URBAN')")
    page.click("#launch")
    page.wait_for_selector("#begin")
    first = page.evaluate("window.__sim.scenario")
    p = first["params"]
    assert (p["seed"], p["difficulty"], p["time_of_day"], p["terrain"], p["degradation"]) == (777, 4, "night", "urban", 2)
    counts = {t: sum(1 for c in first["contacts"] if c["threat"] == t) for t in ("hostile", "decoy", "benign", "friendly")}
    assert counts == {"hostile": 8, "decoy": 1, "benign": 1, "friendly": 0}  # 2 hostiles + swarm of 6
    page.keyboard.press("Enter")
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#again")
    assert "seed 777" in page.inner_text("#screen-card").lower()
    page.click("#again")
    page.wait_for_selector("#begin")
    again = page.evaluate("window.__sim.scenario")
    assert json.dumps(again, sort_keys=True) == json.dumps(first, sort_keys=True)


def test_dashboard_sorting_tables_and_tooltips(page, server):
    for n, cls in enumerate(["RECON_UAS", "BIRD", "RECON_UAS"]):
        body = {"callsign": "dash-1", "unit": "sorters", "scenario_id": "s1-dawn-recon",
                "events": [{"t": 15 + n * 10, "type": "mark", "contact_id": "C1", "data": {}},
                           {"t": 16 + n * 10, "type": "classify", "contact_id": "C1", "data": {"class": cls}}]}
        page.request.post(f"{server}/api/sessions", data=body)
    page.goto(f"{server}/dashboard")
    page.wait_for_selector("#sessions tbody tr")
    page.select_option("#unit", "SORTERS")
    page.wait_for_function("document.querySelector('#progress-name').textContent === 'DASH-1'")
    page.click("#sessions button[data-sort='total']")
    asc = [float(x) for x in page.locator("#sessions tbody tr td:nth-child(3)").all_inner_texts()]
    page.click("#sessions button[data-sort='total']")
    desc = [float(x) for x in page.locator("#sessions tbody tr td:nth-child(3)").all_inner_texts()]
    assert asc == sorted(asc) and desc == sorted(desc, reverse=True) and len(asc) == 3

    panel = page.locator(".panel", has=page.locator("#progress"))
    panel.locator("button[data-view='table']").click()
    assert page.is_visible("#progress-table") and not page.is_visible("#progress")
    assert page.locator("#progress-table tbody tr").count() == 3
    panel.locator("button[data-view='chart']").click()

    box = page.locator("#progress").bounding_box()
    page.mouse.move(box["x"] + box["width"] * 0.4, box["y"] + box["height"] * 0.4)
    page.wait_for_timeout(300)
    active = page.evaluate("Chart.getChart(document.getElementById('progress')).tooltip.getActiveElements().length")
    assert active >= 3  # one per series at the hovered session
    assert page.errors == []


def test_urban_canyon_window_is_short(page, server):
    begin(page, server, "id=s3-urban-canyon")
    page.keyboard.press("p")
    stats = page.evaluate("""() => {
        const S = window.__sim, A = window.__simApi;
        const c = S.scenario.contacts[0];
        const wins = []; let cur = null, total = 0, seen = 0;
        for (let t = c.spawn_t; ; t += 0.25) {
            const los = A.lineOfSight(c.id, t);
            if (los === null) break;
            total += 0.25;
            if (los) { seen += 0.25; if (!cur) { cur = [t - c.spawn_t, t - c.spawn_t]; wins.push(cur); } cur[1] = t - c.spawn_t; }
            else cur = null;
        }
        return { seen, total, wins, par: c.par_detect_s };
    }""")
    # Hidden behind buildings most of the way: a brief mid-route window and a short final one.
    assert stats["seen"] < 0.35 * stats["total"], stats
    assert len(stats["wins"]) >= 2 and all(b - a <= 8 for a, b in stats["wins"]), stats
    # Marking in the first window can earn the fast tier (within half of par).
    assert stats["wins"][0][0] <= 0.5 * stats["par"], stats


def test_fog_and_noise_needs_radar(page, server):
    begin(page, server, "id=s5-fog-noise&speed=16")
    page.evaluate("""() => {
        const S = window.__sim, A = window.__simApi;
        S.firstTrack = {}; S.firstVisual = {};
        setInterval(() => {
            for (const c of S.scenario.contacts) {
                if (!A.isAlive(c, S.t)) continue;
                if (S.radar.tracks.has(c.id)) S.firstTrack[c.id] ??= S.t;
                // Optical: close enough that fog hides less than half the contrast.
                const fog = S.world.scene.fog;
                if (A.range(c.id) <= (fog.near + fog.far) / 2) S.firstVisual[c.id] ??= S.t;
            }
        }, 30);
    }""")
    page.wait_for_function("Object.keys(window.__sim.firstVisual).length === 2", timeout=60_000)
    track, visual = page.evaluate("[window.__sim.firstTrack, window.__sim.firstVisual]")
    for cid in ("C1", "C2"):
        assert cid in track and track[cid] + 10 < visual[cid], (cid, track, visual)


def test_contact_silhouettes(page, server):
    page.goto(f"{server}/mission")
    counts = page.evaluate("""async () => {
        const { World } = await import('/static/js/sim/world.js');
        document.body.innerHTML = '<canvas id="c" style="width:1200px;height:260px;display:block;background:#bcd3e6"></canvas>';
        const models = ['quadcopter', 'hexacopter', 'fixed_wing', 'balloon', 'bird', 'friendly_aircraft'];
        const contacts = models.map((m, i) => ({ id: 'M' + i, model: m, wobble_seed: i + 1, waypoints: [[0, 0, 0], [0, 0, 1]] }));
        const env = { time_of_day: 'day', terrain: 'urban', terrain_seed: 1, fog: 0, visual_range_m: 3000 };
        const w = new World(document.getElementById('c'), { environment: env, contacts });
        w.resize(1200, 260);
        w.scene.fog = null;
        w.camera.position.set(0, 300, 0);
        w.camera.lookAt(0, 300, -10);
        const out = [];
        models.forEach((m, i) => {
            const mesh = w.meshes.get('M' + i);
            const size = { quadcopter: 0.9, hexacopter: 1.6, fixed_wing: 3, balloon: 2.8, bird: 0.9, friendly_aircraft: 16 }[m];
            mesh.visible = true;
            mesh.scale.setScalar(2.2 / size);
            mesh.position.set(-7.5 + i * 3, 299.6, -8);
            mesh.rotation.set(0.5, 0.6, 0);
            let verts = 0;
            mesh.traverse((o) => { if (o.geometry) verts += o.geometry.attributes.position.count; });
            out.push([m, verts]);
        });
        w.render();
        return out;
    }""")
    page.locator("#c").screenshot(path=SHOTS / "12-silhouettes.png")
    verts = dict(counts)
    assert len(verts) == 6 and len(set(verts.values())) == 6  # six distinct geometries
