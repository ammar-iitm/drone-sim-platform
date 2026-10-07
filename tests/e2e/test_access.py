"""Quality gates: keyboard-only run, reduced motion, minimum text size, frame rate with a swarm."""

import pytest

from pathlib import Path

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


def focus_until(page, element_id, limit=120):
    for _ in range(limit):
        if page.evaluate("document.activeElement && document.activeElement.id") == element_id:
            return True
        page.keyboard.press("Tab")
    return False


def test_keyboard_only_run(page, server):
    page.goto(f"{server}/mission")
    page.wait_for_selector(".card")
    assert focus_until(page, "callsign")
    page.keyboard.type("keys-1")
    page.keyboard.press("Tab")
    page.keyboard.type("keyboard unit")
    # Tab to the Mixed Traffic card and select it with Enter.
    for _ in range(60):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.dataset && document.activeElement.dataset.id") == "s4-mixed-traffic":
            break
    page.keyboard.press("Enter")
    assert focus_until(page, "launch")
    page.keyboard.press("Enter")

    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.keyboard.press("q")                       # radar console
    page.wait_for_function("window.__sim.radar.tracks.size > 0", timeout=60_000)
    page.keyboard.press(" ")                       # mark the closest unmarked track
    page.wait_for_function("window.__sim.marked.size === 1")
    page.keyboard.press("4")                       # classify
    page.keyboard.press("t")                       # respond: track only
    page.keyboard.press("Tab")                     # cycle marked contacts
    page.keyboard.press("m")                       # mute toggle
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#again")
    assert page.evaluate("document.activeElement.id") == "again"
    events = page.evaluate("fetch('/api/sessions').then(r => r.json()).then(s => fetch('/api/sessions/' + s[0].id)).then(r => r.json())")["events"]
    assert [e["type"] for e in events if e["type"] in ("mark", "classify", "respond")] == ["mark", "classify", "respond"]
    assert page.errors == [] and page.external == []


@pytest.mark.parametrize("page", [{"reduced_motion": "reduce"}], indirect=True)
def test_reduced_motion_respected(page, server):
    page.goto(f"{server}/sim?callsign=rm&unit=test&id=s4-mixed-traffic&speed=8")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.wait_for_function("window.__sim.t > 20")
    assert page.evaluate("window.__sim.radar.reducedMotion") is True
    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches") is True
    assert page.errors == []


TEXT_AUDIT = """() => {
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('[hidden]')) continue;
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    if (el.closest('.sr-only')) continue;
    // Captions may be 12 px: section labels, column headers, hot-key hints, chip names, tags.
    const caption = !!(el.closest('th, kbd, .key, .tag, .rail-foot, .rail-head') ||
      (el.closest('.label') && !el.closest('.label.data')) || (el.closest('.chip') && el.tagName !== 'STRONG'));
    out.push({ size: parseFloat(cs.fontSize), caption, text: el.textContent.trim().slice(0, 40) });
  }
  return out;
}"""


def test_text_sizes(page, server):
    # One session so the dashboard and review pages have content.
    page.goto(f"{server}/sim?callsign=txt&unit=audit&id=s1-dawn-recon&speed=16")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.wait_for_timeout(800)
    sim = page.evaluate(TEXT_AUDIT)
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#again")
    sid = page.evaluate("fetch('/api/sessions').then(r => r.json())")[0]["id"]
    pages = {"sim": sim}
    for name, path, sel in [("mission", "/mission", ".card"), ("dashboard", "/dashboard", "#confusion td"),
                            ("session", f"/dashboard/session/{sid}", ".timeline li")]:
        page.goto(server + path)
        page.wait_for_selector(sel)
        pages[name] = page.evaluate(TEXT_AUDIT)
    for name, items in pages.items():
        assert items, name
        smallest = min(i["size"] for i in items)
        assert smallest >= 12, (name, [i for i in items if i["size"] < 12][:5])
        # Lead decision 2026-10-07: everything that is not a caption is at least 14 px.
        small_data = [i for i in items if i["size"] < 14 and not i["caption"]]
        assert small_data == [], (name, small_data[:8])


def test_swarm_of_twelve_frame_rate(page, server):
    page.goto(f"{server}/sim?callsign=fps&unit=test&seed=7&difficulty=5&swarm=12&degradation=0&speed=4")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.wait_for_function("""() => {
      const S = window.__sim, A = window.__simApi;
      return S.scenario.contacts.filter((c) => c.swarm && A.isAlive(c, S.t) && A.range(c.id) < 2500).length >= 12;
    }""", timeout=90_000)
    # Face the swarm so every member is drawn.
    page.evaluate("""() => {
      const S = window.__sim, A = window.__simApi;
      const c = S.scenario.contacts.find((c) => c.swarm && A.isAlive(c, S.t));
      const m = S.world.meshes.get(c.id).position;
      S.yaw = (Math.atan2(m.x, -m.z) * 180 / Math.PI + 360) % 360;
    }""")
    page.wait_for_timeout(2500)
    visible = page.evaluate("[...window.__sim.world.meshes.values()].filter((m) => m.visible).length")
    fps = int(page.inner_text("#fps"))
    page.screenshot(path=SHOTS / "09-swarm-12.png")
    assert visible >= 12
    assert fps >= 30, f"{fps} fps with {visible} contacts drawn"
