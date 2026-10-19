"""E2E browser tests for Phase 3 Adaptive Training Intelligence.

Verifies end-to-end adaptive workflow in the real browser:
- Callsign entry triggers adaptive recommendation lookup
- Scripted recommendations display Curriculum Tier X (not runtime difficulty)
- Procedural recommendations display Difficulty X (not curriculum tier)
- 'Accept Recommendation' applies parameters and selects scenario
- Dashboard renders multi-dimensional skill profiles and formatted confusion hotspots
- Empty confusion hotspot list gracefully falls back to 'None'
- No '[object Object]' is ever rendered in the DOM
- Scenario launch continues to work across scripted and procedural workflows
"""

import json
import sqlite3
from pathlib import Path

SHOTS = Path(__file__).resolve().parents[2] / "test-results"


def _insert_session(db_path, callsign, unit, scenario_id, total, grade, result_dict, started_at="2026-10-17T10:00:00Z"):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT OR IGNORE INTO trainees (callsign, unit) VALUES (?, ?)", (callsign, unit))
    t_id = conn.execute("SELECT id FROM trainees WHERE callsign = ? AND unit = ?", (callsign, unit)).fetchone()[0]
    conn.execute(
        "INSERT INTO sessions (trainee_id, scenario_id, scenario_name, seed, params, started_at, duration_s, "
        "total, detection, classification, engagement, grade, false_alarms, breaches, critical_errors, result) "
        "VALUES (?, ?, ?, 0, '{}', ?, 60.0, ?, ?, ?, ?, ?, 0, 0, 0, ?)",
        (t_id, scenario_id, scenario_id, started_at, total,
         result_dict.get("stages", {}).get("detection", total),
         result_dict.get("stages", {}).get("classification", total),
         result_dict.get("stages", {}).get("engagement", total),
         grade, json.dumps(result_dict))
    )
    conn.commit()
    conn.close()


def test_mission_adaptive_recommendation_and_acceptance(page, server, db_path):
    SHOTS.mkdir(exist_ok=True)
    page.goto(f"{server}/mission")
    page.wait_for_selector(".card")
    page.wait_for_selector("#adaptive-panel")

    # 1. Initial state before entering callsign
    assert page.is_visible("#adaptive-prompt")
    assert not page.is_visible("#adaptive-card")

    # 2. Scripted scenario recommendation (Tier label assertion)
    page.fill("#callsign", "E2E-RECRUIT")
    page.fill("#unit", "1 TRG BN")

    page.wait_for_selector("#adaptive-card:not([hidden])", timeout=10_000)
    assert page.is_visible("#adaptive-scen-name")
    rec_text = page.inner_text("#adaptive-scen-name").upper()
    assert "DAWN RECON PASS" in rec_text
    # Must display Curriculum Tier 1, NOT Difficulty 1
    assert "[CURRICULUM TIER 1]" in rec_text
    assert "DIFFICULTY" not in rec_text
    assert page.inner_text("#adaptive-mastery").upper().startswith("NOVICE")

    # Click 'Accept Recommendation' for scripted scenario
    page.click("#btn-accept-rec")
    selected_name = page.inner_text("#selected-name")
    assert "DAWN RECON PASS" in selected_name
    assert not page.is_disabled("#launch")

    page.screenshot(path=SHOTS / "05-adaptive-mission-scripted.png")

    # Launch scripted scenario and verify briefing
    page.click("#launch")
    page.wait_for_selector("#begin", timeout=15_000)
    briefing = page.inner_text("#screen-card")
    assert "DAWN RECON PASS" in briefing.upper()
    assert page.errors == []

    # 3. Procedural scenario recommendation (Difficulty label and parameter assertion)
    # Seed high-mastery sessions to unlock procedural recommendation REC-07
    prodigy_res = {
        "total": 95.0,
        "grade": "A",
        "stages": {"detection": 95.0, "classification": 95.0, "engagement": 95.0},
        "penalties": {"false_alarms": 0, "breaches": 0, "critical_errors": 0},
        "contacts": [],
    }
    for sc_id in ("s1-dawn-recon", "s2-night-loiter", "s3-urban-canyon", "s6-saturation-swarm"):
        _insert_session(db_path, "E2E-PRODIGY", "1 TRG BN", sc_id, 95.0, "A", prodigy_res)

    page.goto(f"{server}/mission")
    page.wait_for_selector("#adaptive-panel")
    with page.expect_response(lambda r: "api/adaptive/recommendation" in r.url and "E2E-PRODIGY" in r.url):
        page.fill("#callsign", "E2E-PRODIGY")
        page.fill("#unit", "1 TRG BN")

    page.wait_for_selector("#adaptive-card:not([hidden])", timeout=10_000)
    proc_rec_text = page.inner_text("#adaptive-scen-name").upper()
    # Must display runtime Difficulty, NOT Curriculum Tier
    assert "[DIFFICULTY 4]" in proc_rec_text
    assert "CURRICULUM TIER" not in proc_rec_text

    # Click 'Accept Recommendation' for procedural scenario
    page.click("#btn-accept-rec")
    page.wait_for_timeout(500)

    # Verify procedural parameters were applied to form inputs
    assert page.input_value("#difficulty") == "4"
    assert page.input_value("#terrain") == "urban"
    assert page.input_value("#time_of_day") == "night"

    # Verify preview and selected name updated to procedural
    selected_proc = page.inner_text("#selected-name").upper()
    assert "DIFFICULTY 4" in selected_proc
    assert not page.is_disabled("#launch")

    page.screenshot(path=SHOTS / "05-adaptive-mission-procedural.png")

    # Launch procedural scenario
    page.click("#launch")
    page.wait_for_selector("#begin", timeout=15_000)
    proc_briefing = page.inner_text("#screen-card").upper()
    assert "DIFFICULTY 4" in proc_briefing
    assert page.errors == []


def test_dashboard_adaptive_training_profile(page, server, db_path):
    SHOTS.mkdir(exist_ok=True)
    # 1. Play brief session for E2E-PILOT so dashboard has basic clean trainee data
    page.goto(f"{server}/sim?callsign=E2E-PILOT&unit=1%20TRG%20BN&id=s1-dawn-recon&speed=16")
    page.wait_for_selector("#begin")
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    page.wait_for_selector("#again", timeout=20_000)

    # 2. Seed synthetic session for E2E-CONFUSED with explicit classification confusion
    confused_res = {
        "total": 70.0,
        "grade": "C",
        "stages": {"detection": 75.0, "classification": 60.0, "engagement": 75.0},
        "penalties": {"false_alarms": 0, "breaches": 0, "critical_errors": 0},
        "contacts": [
            {
                "scored": True,
                "spawn_t": 10.0,
                "true_class": "RECON_UAS",
                "detection": {"t": 12.0},
                "classification": {"chosen": "BIRD"},
            }
        ],
    }
    _insert_session(db_path, "E2E-CONFUSED", "1 TRG BN", "s1-dawn-recon", 70.0, "C", confused_res)

    # 3. Navigate to dashboard
    page.goto(f"{server}/dashboard")
    page.wait_for_selector("#adaptive-dash-panel", timeout=15_000)
    page.wait_for_selector("#adaptive-dims .panel", timeout=15_000)

    # Verify all four skill dimensions are rendered
    assert page.is_visible("#adaptive-dash-panel")
    assert page.is_visible("#adaptive-dims")
    dims_text = page.inner_text("#adaptive-dims").upper()
    assert "DETECTION" in dims_text
    assert "CLASSIFICATION" in dims_text
    assert "ENGAGEMENT" in dims_text
    assert "ENV. RESILIENCE" in dims_text

    # 4. Verify formatted confusion hotspot on E2E-CONFUSED
    page.select_option("#trainee", label="E2E-CONFUSED (1)")
    page.wait_for_timeout(800)

    confused_dims = page.inner_text("#adaptive-dims")
    assert "RECON_UAS -> BIRD (1)" in confused_dims
    assert "[object Object]" not in page.content()

    # Verify recommendation target displays curriculum tier label
    target_rec = page.inner_text("#adaptive-dash-target").upper()
    assert "[CURRICULUM TIER" in target_rec

    # 5. Switch to E2E-PILOT to verify empty confusion hotspot fallback ('Confusion: None')
    page.select_option("#trainee", label="E2E-PILOT (1)")
    page.wait_for_timeout(800)

    clean_notes = page.inner_text("#adaptive-dims").upper()
    assert "CONFUSION: NONE" in clean_notes
    assert "[object Object]" not in page.content()

    page.screenshot(path=SHOTS / "06-adaptive-dashboard.png")
    assert page.errors == []

