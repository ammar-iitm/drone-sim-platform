"""Unit tests for Phase 3 Adaptive Training Intelligence (app/adaptive.py)."""

import json
import pytest

from app import adaptive
from test_api import first_hostile


def _make_session(
    scenario_id="s1-dawn-recon",
    total=80.0,
    detection=80.0,
    classification=80.0,
    engagement=80.0,
    grade="SATISFACTORY",
    false_alarms=0,
    breaches=0,
    critical_errors=0,
    contacts=None,
    params=None,
):
    contacts = contacts or []
    result = {
        "scenario": {"id": scenario_id, "params": params or {}},
        "contacts": contacts,
    }
    return {
        "scenario_id": scenario_id,
        "total": total,
        "detection": detection,
        "classification": classification,
        "engagement": engagement,
        "grade": grade,
        "false_alarms": false_alarms,
        "breaches": breaches,
        "critical_errors": critical_errors,
        "result": json.dumps(result),
        "params": json.dumps(params or {}),
    }


def test_new_trainee_zero_history():
    trainee = {"id": 1, "callsign": "RECRUIT-1", "unit": "TEST BN"}
    rec = adaptive.recommend_next_scenario(trainee, [])

    assert rec["policy_version"] == "1.0.0"
    assert rec["trainee"]["callsign"] == "RECRUIT-1"
    assert rec["skill_profile"]["sample_size"] == 0
    assert rec["skill_profile"]["confidence"] == "NONE"
    assert rec["skill_profile"]["mastery_level"] == "NOVICE"

    r = rec["recommendation"]
    assert r["rule_id"] == "REC-01-BASELINE-ONBOARDING"
    assert r["scenario_id"] == "s1-dawn-recon"
    assert r["difficulty"] == 1
    assert "baseline onboarding" in r["rationale"].lower()
    assert len(r["progression_criteria"]) > 10
    assert r["launch_params"]["id"] == "s1-dawn-recon"


def test_incomplete_sessions_excluded():
    trainee = {"id": 2, "callsign": "RECRUIT-2", "unit": "TEST BN"}
    # 2 incomplete sessions + 0 completed sessions
    sessions = [
        _make_session(total=20.0, grade="INCOMPLETE"),
        _make_session(total=15.0, grade="INCOMPLETE"),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)
    assert rec["skill_profile"]["sample_size"] == 0
    assert rec["recommendation"]["rule_id"] == "REC-01-BASELINE-ONBOARDING"


def test_breach_and_engagement_weakness_diagnosis():
    trainee = {"id": 3, "callsign": "DEFENDER-1", "unit": "1 TRG BN"}
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=55.0, engagement=40.0, breaches=1),
        _make_session(scenario_id="s1-dawn-recon", total=60.0, engagement=50.0, breaches=1),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)

    profile = rec["skill_profile"]
    assert profile["sample_size"] == 2
    assert profile["diagnostics"]["breach_rate"] == 1.0
    assert profile["dimensions"]["engagement"]["rating"] == "WEAK"

    r = rec["recommendation"]
    assert r["rule_id"] == "REC-02-ENGAGEMENT-BREACH-RECOVERY"
    assert r["scenario_id"] == "s2-night-loiter"
    assert "breach" in r["rationale"].lower()
    assert r["difficulty"] in (1, 2)


def test_classification_confusion_and_false_alarms():
    trainee = {"id": 4, "callsign": "OBSERVER-2", "unit": "1 TRG BN"}
    contacts = [
        {
            "id": "C1",
            "scored": True,
            "spawn_t": 10.0,
            "true_class": "DECOY",
            "classification": {"chosen": "ARMED_UAS"},
            "detection": {"t": 15.0},
        },
        {
            "id": "C2",
            "scored": True,
            "spawn_t": 20.0,
            "true_class": "BIRD",
            "classification": {"chosen": "RECON_UAS"},
            "detection": {"t": 24.0},
        },
    ]
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=65.0, classification=50.0, false_alarms=2, contacts=contacts),
        _make_session(scenario_id="s1-dawn-recon", total=68.0, classification=55.0, false_alarms=2, contacts=contacts),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)

    profile = rec["skill_profile"]
    assert profile["dimensions"]["classification"]["rating"] == "WEAK"
    assert profile["diagnostics"]["false_alarms_per_session"] == 2.0
    assert len(profile["diagnostics"]["confusion_hotspots"]) > 0

    r = rec["recommendation"]
    assert r["rule_id"] == "REC-03-DISCRIMINATION-AND-RESTRAINT"
    assert r["scenario_id"] == "s4-mixed-traffic"
    assert "discrimination" in r["focus_area"].lower()


def test_detection_latency_weakness():
    trainee = {"id": 5, "callsign": "TRACKER-3", "unit": "1 TRG BN"}
    contacts = [
        {"id": "C1", "scored": True, "spawn_t": 10.0, "true_class": "RECON_UAS", "classification": {"chosen": "RECON_UAS"}, "detection": {"t": 28.0}},
    ]
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=70.0, detection=50.0, contacts=contacts),
        _make_session(scenario_id="s1-dawn-recon", total=68.0, detection=55.0, contacts=contacts),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)

    profile = rec["skill_profile"]
    assert profile["dimensions"]["detection"]["rating"] == "WEAK"
    assert profile["diagnostics"]["mean_time_to_detect_s"] == 18.0

    r = rec["recommendation"]
    assert r["rule_id"] == "REC-04-RAPID-DETECTION-POPUP"
    assert r["scenario_id"] == "s3-urban-canyon"
    assert "detection" in r["focus_area"].lower()


def test_sensor_degradation_sensitivity():
    trainee = {"id": 6, "callsign": "RADAR-4", "unit": "1 TRG BN"}
    # Clean runs high score, degraded runs low score
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=88.0, detection=88.0, classification=88.0, engagement=88.0, params={"degradation": 0}),
        _make_session(scenario_id="s3-urban-canyon", total=85.0, detection=85.0, classification=85.0, engagement=85.0, params={"degradation": 0}),
        _make_session(scenario_id="s5-fog-noise", total=52.0, detection=50.0, classification=50.0, engagement=55.0, params={"degradation": 3}),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)

    profile = rec["skill_profile"]
    assert profile["dimensions"]["environmental_resilience"]["rating"] == "WEAK"

    r = rec["recommendation"]
    assert r["rule_id"] == "REC-05-SENSOR-DEGRADATION-RESILIENCE"
    assert r["scenario_id"] == "s5-fog-noise"
    assert "fog" in r["rationale"].lower()


def test_expert_mastery_and_swarm_or_procedural_progression():
    trainee = {"id": 7, "callsign": "ACE-1", "unit": "ELITE SQUAD"}
    # Consistently high scores across baseline scenarios
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=92.0, detection=95.0, classification=90.0, engagement=90.0),
        _make_session(scenario_id="s2-night-loiter", total=88.0, detection=88.0, classification=88.0, engagement=88.0),
        _make_session(scenario_id="s3-urban-canyon", total=90.0, detection=90.0, classification=90.0, engagement=90.0),
        _make_session(scenario_id="s4-mixed-traffic", total=89.0, detection=89.0, classification=90.0, engagement=88.0),
        _make_session(scenario_id="s5-fog-noise", total=86.0, detection=85.0, classification=88.0, engagement=86.0),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)

    profile = rec["skill_profile"]
    assert profile["mastery_level"] == "EXPERT"
    assert profile["confidence"] == "HIGH"

    # Since s6 is not yet mastered, should recommend s6-saturation-swarm
    r = rec["recommendation"]
    assert r["rule_id"] == "REC-06-SWARM-TRIAGE-MASTERY"
    assert r["scenario_id"] == "s6-saturation-swarm"
    assert r["difficulty"] == 4

    # Now add high-score s6 session
    sessions.append(_make_session(scenario_id="s6-saturation-swarm", total=90.0, detection=90.0, classification=90.0, engagement=90.0, params={"difficulty": 3}))
    rec2 = adaptive.recommend_next_scenario(trainee, sessions)
    r2 = rec2["recommendation"]
    assert r2["rule_id"] == "REC-07-PROCEDURAL-SWARM-ESCALATION"
    assert r2["scenario_kind"] == "procedural"
    assert 1 <= r2["difficulty"] <= 5
    assert "params" in r2["launch_params"]
    assert 1 <= r2["launch_params"]["params"]["difficulty"] <= 5


def test_deterministic_recommendation():
    trainee = {"id": 8, "callsign": "STATIC-1", "unit": "1 TRG BN"}
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=75.0, detection=70.0, classification=75.0, engagement=80.0),
        _make_session(scenario_id="s2-night-loiter", total=78.0, detection=75.0, classification=80.0, engagement=78.0),
    ]
    rec1 = adaptive.recommend_next_scenario(trainee, sessions)
    rec2 = adaptive.recommend_next_scenario(trainee, sessions)

    assert rec1["recommendation"]["rule_id"] == rec2["recommendation"]["rule_id"]
    assert rec1["recommendation"]["scenario_id"] == rec2["recommendation"]["scenario_id"]
    assert rec1["recommendation"]["difficulty"] == rec2["recommendation"]["difficulty"]
    assert rec1["recommendation"]["focus_area"] == rec2["recommendation"]["focus_area"]
    assert rec1["skill_profile"] == rec2["skill_profile"]


def test_curriculum_progression_for_balanced_trainee():
    trainee = {"id": 9, "callsign": "CADET-5", "unit": "1 TRG BN"}
    # Passed s1 and s2 cleanly with balanced scores (around 78)
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=78.0, detection=78.0, classification=78.0, engagement=78.0),
        _make_session(scenario_id="s2-night-loiter", total=78.0, detection=78.0, classification=78.0, engagement=78.0),
    ]
    rec = adaptive.recommend_next_scenario(trainee, sessions)
    # Next in sequence is s3-urban-canyon
    assert rec["recommendation"]["rule_id"] == "REC-08-CURRICULUM-PROGRESSION"
    assert rec["recommendation"]["scenario_id"] == "s3-urban-canyon"


# ---------------------------------------------------------------- API Endpoint Integration Tests

def test_adaptive_api_missing_and_invalid_params(client):
    r = client.get("/api/adaptive/recommendation")
    assert r.status_code == 400
    assert "callsign or trainee_id is required" in r.get_json()["error"]

    r = client.get("/api/adaptive/recommendation?trainee_id=invalid")
    assert r.status_code == 400
    assert "trainee_id must be an integer" in r.get_json()["error"]

    r = client.get("/api/adaptive/recommendation?trainee_id=999999")
    assert r.status_code == 404
    assert "unknown trainee_id" in r.get_json()["error"]

    r = client.get("/api/adaptive/recommendation?callsign=")
    assert r.status_code == 400
    assert "callsign is required" in r.get_json()["error"]


def test_adaptive_api_new_trainee_default(client):
    r = client.get("/api/adaptive/recommendation?callsign=RECRUIT-9&unit=1%20TRG%20BN")
    assert r.status_code == 200
    data = r.get_json()
    assert data["policy_version"] == "1.0.0"
    assert data["recommendation"]["rule_id"] == "REC-01-BASELINE-ONBOARDING"
    assert data["recommendation"]["scenario_id"] == "s1-dawn-recon"
    assert data["recommendation"]["difficulty"] == 1
    assert data["skill_profile"]["mastery_level"] == "NOVICE"
    assert data["skill_profile"]["confidence"] == "NONE"
    assert data["skill_profile"]["sample_size"] == 0
    assert "baseline onboarding" in data["recommendation"]["rationale"].lower()


def test_adaptive_api_after_completed_session(client):
    # Register and submit a session for VIPER-1
    c = first_hostile("s1-dawn-recon")
    t0 = c["spawn_t"]
    # Mark and respond, plus 2 false alarms
    events = [
        {"t": t0 + 4, "type": "mark", "contact_id": c["id"], "data": {"via": "view"}},
        {"t": t0 + 5, "type": "classify", "contact_id": c["id"], "data": {"class": "RECON_UAS"}},
        {"t": t0 + 10, "type": "respond", "contact_id": c["id"], "data": {"response": "REPORT"}},
        {"t": t0 + 12, "type": "mark", "contact_id": None, "data": {}},
        {"t": t0 + 14, "type": "mark", "contact_id": None, "data": {}},
    ]
    post_res = client.post("/api/sessions", json={
        "callsign": "VIPER-1",
        "unit": "1 TRG BN",
        "scenario_id": "s1-dawn-recon",
        "events": events
    })
    assert post_res.status_code == 201
    trainee_id = post_res.get_json()["trainee"]["id"]

    # Query recommendation by callsign
    r = client.get("/api/adaptive/recommendation?callsign=VIPER-1&unit=1%20TRG%20BN")
    assert r.status_code == 200
    rec = r.get_json()
    assert rec["skill_profile"]["sample_size"] == 1
    assert rec["skill_profile"]["diagnostics"]["false_alarms_per_session"] == 2.0
    # False alarms triggered Rule 3 (discrimination) -> s4-mixed-traffic
    assert rec["recommendation"]["rule_id"] == "REC-03-DISCRIMINATION-AND-RESTRAINT"
    assert rec["recommendation"]["scenario_id"] == "s4-mixed-traffic"
    assert "false alarm" in rec["recommendation"]["rationale"].lower()

    # Query via /api/adaptive/profile endpoint alias
    p = client.get("/api/adaptive/profile?callsign=VIPER-1&unit=1%20TRG%20BN")
    assert p.status_code == 200
    assert p.get_json()["recommendation"]["rule_id"] == rec["recommendation"]["rule_id"]

    # Query via trainee_id
    r_tid = client.get(f"/api/adaptive/recommendation?trainee_id={trainee_id}")
    assert r_tid.status_code == 200
    assert r_tid.get_json()["trainee"]["callsign"] == "VIPER-1"


def test_adaptive_api_authorization_isolation(tmp_path):
    from app import create_app
    app = create_app({"DATABASE": str(tmp_path / "auth_test.db"), "TESTING": True, "INSTRUCTOR_PASSWORD": "secret-pass"})
    c = app.test_client()

    # Trainees can register session
    c_hostile = first_hostile("s1-dawn-recon")
    events = [{"t": c_hostile["spawn_t"] + 5, "type": "mark", "contact_id": c_hostile["id"], "data": {}}]
    res = c.post("/api/sessions", json={"callsign": "CADET-A", "unit": "1 TRG BN", "scenario_id": "s1-dawn-recon", "events": events})
    assert res.status_code == 201
    trainee_id = res.get_json()["trainee"]["id"]

    # Unauthenticated trainee requesting by callsign in protected mode gets safe baseline onboarding recommendation
    # without leaking historical session records or skill profile (Finding G)
    r_callsign = c.get("/api/adaptive/recommendation?callsign=CADET-A&unit=1%20TRG%20BN")
    assert r_callsign.status_code == 200
    assert r_callsign.get_json()["trainee"]["callsign"] == "CADET-A"
    assert r_callsign.get_json()["skill_profile"]["sample_size"] == 0
    assert r_callsign.get_json()["recommendation"]["rule_id"] == "REC-01-BASELINE-ONBOARDING"

    # Unauthenticated user CANNOT query arbitrary trainee_id without instructor login
    r_unauth_id = c.get(f"/api/adaptive/recommendation?trainee_id={trainee_id}")
    assert r_unauth_id.status_code == 401
    assert r_unauth_id.get_json()["error"] == "instructor login required"

    # Log in as instructor
    login_res = c.post("/login", data={"password": "secret-pass"})
    assert login_res.status_code == 302

    # Now instructor can query by trainee_id and receives full history
    r_auth_id = c.get(f"/api/adaptive/recommendation?trainee_id={trainee_id}")
    assert r_auth_id.status_code == 200
    assert r_auth_id.get_json()["trainee"]["id"] == trainee_id
    assert r_auth_id.get_json()["skill_profile"]["sample_size"] == 1

    # Instructor querying by callsign also receives full history
    r_auth_cs = c.get("/api/adaptive/recommendation?callsign=CADET-A&unit=1%20TRG%20BN")
    assert r_auth_cs.status_code == 200
    assert r_auth_cs.get_json()["skill_profile"]["sample_size"] == 1

    # Local unauthenticated laptop mode preserves normal callsign history retrieval
    app_local = create_app({"DATABASE": str(tmp_path / "auth_test.db"), "TESTING": True})
    c_local = app_local.test_client()
    r_local = c_local.get("/api/adaptive/recommendation?callsign=CADET-A&unit=1%20TRG%20BN")
    assert r_local.status_code == 200
    assert r_local.get_json()["skill_profile"]["sample_size"] == 1


# ---------------------------------------------------------------- Phase 3 Finding Remediation Tests

def test_finding_h_evidence_validation_rejects_invalid_json_and_grades():
    """Finding H: evaluate_trainee_skills strictly excludes non-dict JSON, unverified/incomplete/missing grades, and malformed fields."""
    trainee = {"id": 10, "callsign": "EVIDENCE-TEST", "unit": "1 TRG BN"}

    # 1. Non-dict JSON records (42, []) must not raise AttributeError and must be excluded
    bad_json_sessions = [
        {"scenario_id": "s1-dawn-recon", "total": 90.0, "detection": 90.0, "classification": 90.0, "engagement": 90.0, "grade": "A", "result": 42},
        {"scenario_id": "s1-dawn-recon", "total": 90.0, "detection": 90.0, "classification": 90.0, "engagement": 90.0, "grade": "A", "result": "42"},
        {"scenario_id": "s1-dawn-recon", "total": 90.0, "detection": 90.0, "classification": 90.0, "engagement": 90.0, "grade": "A", "result": []},
        {"scenario_id": "s1-dawn-recon", "total": 90.0, "detection": 90.0, "classification": 90.0, "engagement": 90.0, "grade": "A", "result": "[]"},
    ]
    profile_bad_json = adaptive.evaluate_trainee_skills(bad_json_sessions)
    assert profile_bad_json["sample_size"] == 0
    assert profile_bad_json["mastery_level"] == "NOVICE"

    # 2. UNVERIFIED, missing, empty, or unrecognized grade sessions must be completely excluded
    unverified_sessions = [
        _make_session(total=95.0, grade="UNVERIFIED"),
        _make_session(total=95.0, grade=None),
        _make_session(total=95.0, grade=""),
        _make_session(total=95.0, grade="NOT_A_VALID_GRADE"),
        _make_session(total=95.0, grade="INCOMPLETE"),
        {**_make_session(total=95.0, grade="A"), "session_status": "unverified"},
        {**_make_session(total=95.0, grade="A"), "session_status": "interrupted"},
        {**_make_session(total=95.0, grade="A"), "session_status": "rejected"},
    ]
    profile_unverified = adaptive.evaluate_trainee_skills(unverified_sessions)
    assert profile_unverified["sample_size"] == 0

    # 3. Corrupt numeric fields (NaN, inf, strings, booleans, out-of-range) are EXCLUDED (not coerced to zero)
    corrupt_numeric_sessions = [
        {
            "scenario_id": "s1-dawn-recon",
            "total": float("nan"),
            "detection": True,  # boolean must be rejected
            "classification": float("inf"),
            "engagement": "invalid-string",
            "false_alarms": -10,
            "breaches": True,
            "critical_errors": None,
            "grade": "A",
            "result": json.dumps({"scenario": {"id": "s1-dawn-recon"}, "stages": {"detection": 80.0, "classification": 80.0, "engagement": 80.0}}),
        },
        {
            "scenario_id": "s1-dawn-recon",
            "total": -10.0,  # out of [0, 100]
            "detection": 80.0,
            "classification": 80.0,
            "engagement": 80.0,
            "grade": "A",
            "result": json.dumps({"scenario": {"id": "s1-dawn-recon"}}),
        },
        {
            "scenario_id": "s1-dawn-recon",
            "total": 150.0,  # out of [0, 100]
            "detection": 80.0,
            "classification": 80.0,
            "engagement": 80.0,
            "grade": "A",
            "result": json.dumps({"scenario": {"id": "s1-dawn-recon"}}),
        },
    ]
    profile_corrupt = adaptive.evaluate_trainee_skills(corrupt_numeric_sessions)
    # Zero qualifying sessions remain; falls back to stable novice profile
    assert profile_corrupt["sample_size"] == 0
    assert profile_corrupt["mastery_level"] == "NOVICE"
    assert profile_corrupt["average_score"] is None

    # 4. Valid historical sessions omitting newer optional fields are supported safely
    legacy_sessions = [
        {
            "scenario_id": "s1-dawn-recon",
            "total": 85.0,
            "detection": 80.0,
            "classification": 85.0,
            "engagement": 90.0,
            "grade": "B",
            "false_alarms": 0,
            "breaches": 0,
            "critical_errors": 0,
            # Valid result dict but predates degradation and session_status fields
            "result": json.dumps({
                "scenario": {"id": "s1-dawn-recon", "name": "Dawn Recon Pass"},
                "stages": {"detection": 80.0, "classification": 85.0, "engagement": 90.0},
                "total": 85.0,
            }),
        }
    ]
    profile_legacy = adaptive.evaluate_trainee_skills(legacy_sessions)
    assert profile_legacy["sample_size"] == 1
    assert profile_legacy["average_score"] == 85.0
    assert profile_legacy["dimensions"]["engagement"]["score"] == 90.0

    # 5. An invalid session for s1-dawn-recon cannot unlock curriculum progression
    trainee = {"id": 10, "callsign": "CURRIC-1", "unit": "1 TRG BN"}
    mixed_sessions = [
        # Corrupt / invalid-grade session for s1
        {
            "scenario_id": "s1-dawn-recon",
            "total": 90.0,
            "detection": 90.0,
            "classification": 90.0,
            "engagement": 90.0,
            "grade": "INVALID_GRADE",
            "result": json.dumps({"scenario": {"id": "s1-dawn-recon"}}),
        },
        # Valid session for s2
        _make_session(scenario_id="s2-night-loiter", total=85.0, detection=85.0, classification=85.0, engagement=85.0, grade="B"),
    ]
    # S1 was never legitimately completed with a valid grade, so s1-dawn-recon must still be recommended
    rec_curric = adaptive.recommend_next_scenario(trainee, mixed_sessions)
    assert rec_curric["skill_profile"]["sample_size"] == 1
    assert rec_curric["recommendation"]["scenario_id"] == "s1-dawn-recon"


def test_finding_b_configurable_rubric_thresholds():
    """Finding B: Adaptive thresholds honor configuration passed in rubric JSON and reject contradictory values."""
    trainee = {"id": 11, "callsign": "THRESH-1", "unit": "1 TRG BN"}

    # 1. Contradictory thresholds (weak >= strong) must be rejected
    contradictory_rubric = {
        "adaptive": {
            "weak_threshold": 90.0,
            "strong_threshold": 80.0,
        }
    }
    with pytest.raises(ValueError, match="Contradictory adaptive thresholds"):
        adaptive.recommend_next_scenario(trainee, [], contradictory_rubric)

    # 2. Contradictory MTTD latency thresholds (strong >= weak) must be rejected
    contradictory_mttd = {
        "adaptive": {
            "mttd_weak_s": 10.0,
            "mttd_strong_s": 16.0,
        }
    }
    with pytest.raises(ValueError, match="Contradictory detection latency thresholds"):
        adaptive.recommend_next_scenario(trainee, [], contradictory_mttd)

    # 3. Contradictory mastery thresholds (practitioner >= expert) must be rejected
    contradictory_mastery = {
        "adaptive": {
            "practitioner_score": 85.0,
            "expert_score": 80.0,
        }
    }
    with pytest.raises(ValueError, match="Contradictory mastery thresholds"):
        adaptive.recommend_next_scenario(trainee, [], contradictory_mastery)

    # 4. Invalid types (boolean, NaN, infinite, non-numeric) must be rejected
    with pytest.raises(ValueError, match="Invalid boolean value"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"weak_threshold": True}})
    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"weak_threshold": float("nan")}})

    # 5. Supported threshold customizations predictably alter ratings and rule selection
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=78.0, detection=70.0, classification=85.0, engagement=85.0, grade="B"),
        _make_session(scenario_id="s2-night-loiter", total=78.0, detection=70.0, classification=85.0, engagement=85.0, grade="B"),
    ]

    # Baseline with default rubric (weak_threshold = 65.0): detection score 70.0 is SATISFACTORY
    default_rubric = {
        "grade_bands": [{"min": 70, "grade": "C"}, {"min": 80, "grade": "B"}],
        "adaptive": {
            "weak_threshold": 65.0,
            "detection_weak_score": 65.0,
            "strong_threshold": 80.0,
        }
    }
    rec_default = adaptive.recommend_next_scenario(trainee, sessions, default_rubric)
    assert rec_default["skill_profile"]["dimensions"]["detection"]["rating"] == "SATISFACTORY"
    assert rec_default["recommendation"]["rule_id"] != "REC-04-RAPID-DETECTION-POPUP"

    # Customized rubric raising detection_weak_score / weak_threshold to 75.0 -> score 70.0 is now WEAK
    strict_rubric = {
        "grade_bands": [{"min": 70, "grade": "C"}, {"min": 80, "grade": "B"}],
        "adaptive": {
            "weak_threshold": 75.0,
            "detection_weak_score": 75.0,
            "strong_threshold": 85.0,
        }
    }
    rec_strict = adaptive.recommend_next_scenario(trainee, sessions, strict_rubric)
    assert rec_strict["skill_profile"]["dimensions"]["detection"]["rating"] == "WEAK"
    assert rec_strict["recommendation"]["rule_id"] == "REC-04-RAPID-DETECTION-POPUP"


def test_finding_i_and_k_determinism_and_difficulty_type():
    """Findings I & K: Recommendation is deterministic across repeated calls and distinguishes curriculum tier from procedural difficulty."""
    trainee = {"id": 12, "callsign": "DETERM-1", "unit": "1 TRG BN"}
    sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=82.0, detection=80.0, classification=85.0, engagement=82.0, grade="B"),
        _make_session(scenario_id="s2-night-loiter", total=84.0, detection=82.0, classification=86.0, engagement=84.0, grade="B"),
    ]

    rec1 = adaptive.recommend_next_scenario(trainee, sessions)
    rec2 = adaptive.recommend_next_scenario(trainee, sessions)

    # Core decisions are identical
    r1 = rec1["recommendation"]
    r2 = rec2["recommendation"]
    assert r1["rule_id"] == r2["rule_id"]
    assert r1["scenario_id"] == r2["scenario_id"]
    assert r1["scenario_kind"] == r2["scenario_kind"]
    assert r1["difficulty"] == r2["difficulty"]
    assert r1["difficulty_type"] == "curriculum_tier"
    assert r1["launch_params"] == r2["launch_params"]
    assert r1["rationale"] == r2["rationale"]
    assert r1["progression_criteria"] == r2["progression_criteria"]
    assert rec1["skill_profile"] == rec2["skill_profile"]

    # Procedural recommendation has difficulty_type == "parameter"
    expert_sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
        _make_session(scenario_id="s2-night-loiter", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
        _make_session(scenario_id="s3-urban-canyon", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
        _make_session(scenario_id="s4-mixed-traffic", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
        _make_session(scenario_id="s5-fog-noise", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
        _make_session(scenario_id="s6-saturation-swarm", total=90.0, detection=90.0, classification=90.0, engagement=90.0, grade="A"),
    ]
    rec_proc = adaptive.recommend_next_scenario(trainee, expert_sessions)
    assert rec_proc["recommendation"]["scenario_kind"] == "procedural"
    assert rec_proc["recommendation"]["difficulty_type"] == "parameter"
    assert rec_proc["recommendation"]["launch_params"]["params"]["difficulty"] == rec_proc["recommendation"]["difficulty"]


def test_finding_a1_explicit_session_statuses_and_legacy_support():
    """Finding A1: Allows legacy records omitting status, but strictly requires 'completed' when an explicit status is present."""
    # 1. Genuinely legacy records omitting status fields are accepted
    legacy_record = _make_session(scenario_id="s1-dawn-recon", total=85.0, grade="B")
    legacy_record.pop("session_status", None)
    profile_legacy = adaptive.evaluate_trainee_skills([legacy_record])
    assert profile_legacy["sample_size"] == 1
    assert profile_legacy["mastery_level"] in ("NOVICE", "PRACTITIONER")

    # 2. Present explicit 'completed' status is accepted
    completed_record = {**_make_session(scenario_id="s1-dawn-recon", total=85.0, grade="B"), "session_status": "completed"}
    assert adaptive.evaluate_trainee_skills([completed_record])["sample_size"] == 1

    # 3. Present explicit non-completed statuses in top-level session are rejected
    non_completed_statuses = ["failed", "abandoned", "interrupted", "rejected", "unverified", "unknown", "in_progress", True, 123]
    for bad_status in non_completed_statuses:
        bad_rec = {**_make_session(scenario_id="s1-dawn-recon", total=85.0, grade="B"), "session_status": bad_status}
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0, f"Status {bad_status!r} must be excluded from qualifying sample"

    # 4. Present explicit non-completed statuses in parsed result metadata are rejected
    for bad_status in ["interrupted", "unverified", "rejected", "failed", "abandoned"]:
        bad_res = json.loads(legacy_record["result"])
        bad_res["session_status"] = bad_status
        bad_rec = {**legacy_record, "result": json.dumps(bad_res)}
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0, f"Result session_status {bad_status!r} must be excluded"


def test_finding_a2_rejects_invalid_penalty_measurements_without_coercion():
    """Finding A2: Distinguishes genuinely absent penalties from malformed/negative values, rejecting invalid evidence without coercing to zero."""
    trainee = {"id": 20, "callsign": "PENALTY-GUARD", "unit": "1 TRG BN"}

    # 1. Valid baseline session
    base = _make_session(scenario_id="s1-dawn-recon", total=85.0, detection=85.0, classification=85.0, engagement=85.0, grade="B")

    # 2. Genuinely absent optional fields (legacy records) default to 0 and are accepted
    legacy_absent = dict(base)
    legacy_absent.pop("false_alarms", None)
    legacy_absent.pop("breaches", None)
    legacy_absent.pop("critical_errors", None)
    res_no_pen = json.loads(legacy_absent["result"])
    res_no_pen.pop("penalties", None)
    legacy_absent["result"] = json.dumps(res_no_pen)
    prof_legacy = adaptive.evaluate_trainee_skills([legacy_absent])
    assert prof_legacy["sample_size"] == 1
    assert prof_legacy["diagnostics"]["false_alarms_per_session"] == 0.0
    assert prof_legacy["diagnostics"]["total_breaches"] == 0

    # 3. Present but malformed/negative false_alarms must be excluded (not coerced to zero)
    bad_fa_values = [-1, -10, True, False, "invalid", "2.5", 2.5, float("nan"), float("inf")]
    for val in bad_fa_values:
        bad_rec = dict(base, false_alarms=val)
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0, f"false_alarms={val!r} must not qualify as evidence"

    # 4. Present but malformed/negative breaches must be excluded
    bad_br_values = [-1, -5, True, False, "corrupt", "3.14", 3.14, float("nan"), float("inf")]
    for val in bad_br_values:
        bad_rec = dict(base, breaches=val)
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0, f"breaches={val!r} must not qualify as evidence"

    # 5. Present but malformed/negative critical_errors must be excluded
    bad_cr_values = [-1, -2, True, False, "err", 1.5, float("nan")]
    for val in bad_cr_values:
        bad_rec = dict(base, critical_errors=val)
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0, f"critical_errors={val!r} must not qualify as evidence"

    # 6. Invalid penalty records cannot advance curriculum progression
    # Pair an invalid-penalty s1 session with a valid s2 session; s1 must NOT be marked completed
    mixed = [
        dict(base, false_alarms=-5),  # invalid s1
        _make_session(scenario_id="s2-night-loiter", total=85.0, grade="B"),  # valid s2
    ]
    rec = adaptive.recommend_next_scenario(trainee, mixed)
    assert rec["skill_profile"]["sample_size"] == 1
    # s1 is still recommended because the invalid session cannot count as completing s1
    assert rec["recommendation"]["scenario_id"] == "s1-dawn-recon"


def test_finding_a3_guarded_against_malformed_nested_json():
    """Finding A3: Malformed nested JSON structures in result do not raise unhandled exceptions."""
    trainee = {"id": 21, "callsign": "NESTED-GUARD", "unit": "1 TRG BN"}

    # Top-level scenario_id is missing, and parsed_res['scenario'] is a string, int, list, or None
    malformed_scenarios = [
        "s1-dawn-recon",  # string instead of dict: parsed_res.get('scenario', {}).get('id') would raise AttributeError
        123,
        ["s1-dawn-recon"],
        None,
        True,
    ]
    for malformed_scen in malformed_scenarios:
        bad_rec = {
            "total": 85.0,
            "detection": 85.0,
            "classification": 85.0,
            "engagement": 85.0,
            "grade": "B",
            "result": json.dumps({
                "scenario": malformed_scen,
                "stages": {"detection": 85.0, "classification": 85.0, "engagement": 85.0},
            }),
        }
        # Must execute without uncaught AttributeError or TypeError, safely excluding the record
        prof = adaptive.evaluate_trainee_skills([bad_rec])
        assert prof["sample_size"] == 0
        rec = adaptive.recommend_next_scenario(trainee, [bad_rec])
        assert rec["skill_profile"]["sample_size"] == 0


def test_finding_b1_integer_config_rejects_silent_truncation():
    """Finding B1: _val_int strictly rejects fractional numbers, booleans, and non-integers without silent truncation."""
    trainee = {"id": 22, "callsign": "CONFIG-INT", "unit": "1 TRG BN"}

    # Fractional floats must not be silently truncated to int
    with pytest.raises(ValueError, match="Fractional number not allowed"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"hotspots_weak_count": 3.5}})

    # Fractional strings must not be parsed
    with pytest.raises(ValueError, match="Non-integer value"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"hotspots_weak_count": "3.5"}})

    # Booleans must be rejected
    with pytest.raises(ValueError, match="Invalid boolean value"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"hotspots_weak_count": True}})

    # NaN / Inf must be rejected
    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"hotspots_weak_count": float("nan")}})

    # Negative below min_val must be rejected
    with pytest.raises(ValueError, match="below minimum allowed"):
        adaptive.recommend_next_scenario(trainee, [], {"adaptive": {"hotspots_weak_count": 0}})

    # Valid exact integer float (3.0), integer string ("3"), and int (3) are accepted
    cfg1 = adaptive._get_adaptive_config({"adaptive": {"hotspots_weak_count": 3.0}})
    assert cfg1["hotspots_weak_count"] == 3
    cfg2 = adaptive._get_adaptive_config({"adaptive": {"hotspots_weak_count": "4"}})
    assert cfg2["hotspots_weak_count"] == 4
    cfg3 = adaptive._get_adaptive_config({"adaptive": {"hotspots_weak_count": 5}})
    assert cfg3["hotspots_weak_count"] == 5


def test_finding_b2_hotspot_threshold_semantics_and_configurable_cutoffs():
    """Finding B2: hotspots_weak_count and hotspots_remediation_count govern skill rating and recommendation independently."""
    trainee = {"id": 23, "callsign": "HOTSPOT-SEM", "unit": "1 TRG BN"}

    # Create a session with 2 distinct confusion hotspots
    # Pair 1: RECON_UAS -> BIRD (2 occurrences)
    # Pair 2: ARMED_UAS -> DECOY (1 occurrence)
    session_with_2_hotspots = _make_session(
        scenario_id="s1-dawn-recon",
        total=80.0,
        detection=85.0,
        classification=75.0,  # satisfactory score on classification
        engagement=85.0,
        grade="B",
    )
    res_dict = json.loads(session_with_2_hotspots["result"])
    res_dict["contacts"] = [
        {"scored": True, "spawn_t": 1.0, "true_class": "RECON_UAS", "detection": {"t": 3.0}, "classification": {"chosen": "BIRD"}},
        {"scored": True, "spawn_t": 5.0, "true_class": "RECON_UAS", "detection": {"t": 7.0}, "classification": {"chosen": "BIRD"}},
        {"scored": True, "spawn_t": 10.0, "true_class": "ARMED_UAS", "detection": {"t": 12.0}, "classification": {"chosen": "DECOY"}},
    ]
    session_with_2_hotspots["result"] = json.dumps(res_dict)

    # Policy 1: Default rubric (hotspots_weak_count=3, hotspots_remediation_count=2)
    # 2 hotspots < hotspots_weak_count (3) -> classification rating is NOT WEAK (SATISFACTORY)
    # But 2 hotspots >= hotspots_remediation_count (2) -> triggers REC-03 discrimination remediation
    prof_default = adaptive.evaluate_trainee_skills([session_with_2_hotspots])
    assert len(prof_default["diagnostics"]["confusion_hotspots"]) == 2
    assert prof_default["dimensions"]["classification"]["rating"] == "SATISFACTORY"

    rec_default = adaptive.recommend_next_scenario(trainee, [session_with_2_hotspots])
    assert rec_default["recommendation"]["rule_id"] == "REC-03-DISCRIMINATION-AND-RESTRAINT"

    # Policy 2: Custom rubric setting hotspots_remediation_count=3
    # 2 hotspots < 3 -> REC-03 does NOT trigger on hotspots alone
    custom_rubric_lenient_rec = {
        "grade_bands": [{"min": 70, "grade": "C"}, {"min": 80, "grade": "B"}],
        "adaptive": {
            "classification_weak_score": 68.0,
            "false_alarm_rate_weak": 1.25,
            "hotspots_weak_count": 3,
            "hotspots_remediation_count": 3,
        }
    }
    rec_lenient = adaptive.recommend_next_scenario(trainee, [session_with_2_hotspots], custom_rubric_lenient_rec)
    assert rec_lenient["recommendation"]["rule_id"] != "REC-03-DISCRIMINATION-AND-RESTRAINT"

    # Policy 3: Custom rubric setting hotspots_weak_count=2
    # 2 hotspots >= 2 -> classification rating becomes WEAK
    custom_rubric_strict_prof = {
        "grade_bands": [{"min": 70, "grade": "C"}, {"min": 80, "grade": "B"}],
        "adaptive": {
            "hotspots_weak_count": 2,
        }
    }
    prof_strict = adaptive.evaluate_trainee_skills([session_with_2_hotspots], custom_rubric_strict_prof)
    assert prof_strict["dimensions"]["classification"]["rating"] == "WEAK"


def test_edge_case_explicit_null_and_invalid_statuses():
    """Verify that absent status fields are tolerated for legacy records,
    while explicitly present null, non-string, or non-completed statuses are rejected.
    Both top-level and nested result statuses are verified and must not contradict.
    """
    valid_base = _make_session(grade="A", total=85.0)

    # 1. Genuinely absent status in both top-level and result (legacy record) qualifies
    s_legacy = dict(valid_base)
    assert "session_status" not in s_legacy and "status" not in s_legacy
    assert len(adaptive.get_qualifying_sessions([s_legacy])) == 1

    # 2. Explicit null top-level session_status or status is rejected
    s_null_ss = dict(valid_base, session_status=None)
    assert len(adaptive.get_qualifying_sessions([s_null_ss])) == 0

    s_null_st = dict(valid_base, status=None)
    assert len(adaptive.get_qualifying_sessions([s_null_st])) == 0

    # 3. Explicit null in nested result metadata is rejected
    res_null_ss = json.loads(valid_base["result"])
    res_null_ss["session_status"] = None
    s_res_null = dict(valid_base, result=json.dumps(res_null_ss))
    assert len(adaptive.get_qualifying_sessions([s_res_null])) == 0

    res_null_st = json.loads(valid_base["result"])
    res_null_st["status"] = None
    s_res_null2 = dict(valid_base, result=json.dumps(res_null_st))
    assert len(adaptive.get_qualifying_sessions([s_res_null2])) == 0

    # 4. Invalid non-string statuses (int, bool, list) rejected
    s_int_st = dict(valid_base, session_status=123)
    assert len(adaptive.get_qualifying_sessions([s_int_st])) == 0
    s_bool_st = dict(valid_base, status=True)
    assert len(adaptive.get_qualifying_sessions([s_bool_st])) == 0

    # 5. Non-completed explicit statuses rejected
    for bad_status in ("failed", "abandoned", "interrupted", "rejected", "unverified", "unknown", "in_progress"):
        s_bad = dict(valid_base, session_status=bad_status)
        assert len(adaptive.get_qualifying_sessions([s_bad])) == 0, f"Expected {bad_status} to be rejected"

    # 6. Valid explicit 'completed' status qualifies
    s_completed = dict(valid_base, session_status="completed")
    assert len(adaptive.get_qualifying_sessions([s_completed])) == 1

    # 7. Contradictory evidence: top-level completed, but nested failed or null -> rejected
    res_failed = json.loads(valid_base["result"])
    res_failed["status"] = "failed"
    s_contra = dict(valid_base, session_status="completed", result=json.dumps(res_failed))
    assert len(adaptive.get_qualifying_sessions([s_contra])) == 0

    res_null = json.loads(valid_base["result"])
    res_null["status"] = None
    s_contra2 = dict(valid_base, session_status="completed", result=json.dumps(res_null))
    assert len(adaptive.get_qualifying_sessions([s_contra2])) == 0


def test_edge_case_missing_versus_explicit_null_and_malformed_penalties():
    """Verify that genuinely missing penalty fields default to 0 for legacy records,
    while explicitly present null, boolean, string, negative, fractional, or contradictory penalties are rejected.
    """
    valid_base = _make_session(grade="A", total=85.0)

    # 1. Genuinely absent penalties in both top-level and result qualifies with 0 penalties
    s_absent = dict(valid_base)
    del s_absent["false_alarms"]
    del s_absent["breaches"]
    del s_absent["critical_errors"]
    q_absent = adaptive.get_qualifying_sessions([s_absent])
    assert len(q_absent) == 1
    assert q_absent[0]["false_alarms"] == 0
    assert q_absent[0]["breaches"] == 0
    assert q_absent[0]["critical_errors"] == 0

    # 2. Explicit null top-level penalty values rejected
    for pen_key in ("false_alarms", "breaches", "critical_errors"):
        s_null = dict(valid_base, **{pen_key: None})
        assert len(adaptive.get_qualifying_sessions([s_null])) == 0, f"Expected {pen_key}=None to be rejected"

    # 3. Explicit null in nested result penalties rejected
    for pen_key in ("false_alarms", "breaches", "critical_errors"):
        res = json.loads(valid_base["result"])
        res["penalties"] = {pen_key: None}
        s_nest_null = dict(valid_base, result=json.dumps(res))
        assert len(adaptive.get_qualifying_sessions([s_nest_null])) == 0, f"Expected nested {pen_key}=None to be rejected"

    # 4. Explicit null penalties container rejected
    res_null_pen = json.loads(valid_base["result"])
    res_null_pen["penalties"] = None
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, result=json.dumps(res_null_pen))])) == 0

    # 5. Malformed penalties: booleans, numeric strings, negatives, fractionals, NaN, inf rejected
    for bad_val in (True, False, "0", "2", -1, 1.5, float("nan"), float("inf"), [0]):
        s_bad_fa = dict(valid_base, false_alarms=bad_val)
        assert len(adaptive.get_qualifying_sessions([s_bad_fa])) == 0, f"Expected {bad_val!r} false_alarms to be rejected"
        s_bad_br = dict(valid_base, breaches=bad_val)
        assert len(adaptive.get_qualifying_sessions([s_bad_br])) == 0, f"Expected {bad_val!r} breaches to be rejected"
        s_bad_cr = dict(valid_base, critical_errors=bad_val)
        assert len(adaptive.get_qualifying_sessions([s_bad_cr])) == 0, f"Expected {bad_val!r} critical_errors to be rejected"

    # 6. Precedence and consistency: top-level and nested must agree
    # Consistent: top=2, nested=2 -> accepted
    res_pen2 = json.loads(valid_base["result"])
    res_pen2["penalties"] = {"false_alarms": 2, "breaches": 1, "critical_errors": 0}
    s_consistent = dict(valid_base, false_alarms=2, breaches=1, critical_errors=0, result=json.dumps(res_pen2))
    q_cons = adaptive.get_qualifying_sessions([s_consistent])
    assert len(q_cons) == 1
    assert q_cons[0]["false_alarms"] == 2
    assert q_cons[0]["breaches"] == 1

    # Contradictory: top=0, nested=3 -> rejected
    res_pen_contra = json.loads(valid_base["result"])
    res_pen_contra["penalties"] = {"false_alarms": 3}
    s_contra = dict(valid_base, false_alarms=0, result=json.dumps(res_pen_contra))
    assert len(adaptive.get_qualifying_sessions([s_contra])) == 0


def test_edge_case_numeric_score_type_policy_and_null_scores():
    """Verify that score fields strictly enforce numeric types (rejecting numeric strings,
    booleans, explicit nulls, NaN, inf, and out-of-range values) and enforce consistency.
    """
    valid_base = _make_session(grade="A", total=85.0, detection=85.0, classification=85.0, engagement=85.0)

    # 1. Numeric strings such as "85.0" and "0" must be rejected under strict numeric-input policy
    for s_val in ("85.0", "0", "100.0", "50", "95.5"):
        s_str_tot = dict(valid_base, total=s_val)
        assert len(adaptive.get_qualifying_sessions([s_str_tot])) == 0, f"Expected total={s_val!r} to be rejected"
        s_str_det = dict(valid_base, detection=s_val)
        assert len(adaptive.get_qualifying_sessions([s_str_det])) == 0, f"Expected detection={s_val!r} to be rejected"
        s_str_cls = dict(valid_base, classification=s_val)
        assert len(adaptive.get_qualifying_sessions([s_str_cls])) == 0, f"Expected classification={s_val!r} to be rejected"
        s_str_eng = dict(valid_base, engagement=s_val)
        assert len(adaptive.get_qualifying_sessions([s_str_eng])) == 0, f"Expected engagement={s_val!r} to be rejected"

    # 2. Booleans rejected
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=True)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, detection=False)])) == 0

    # 3. Explicit null scores rejected
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=None)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, detection=None)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, classification=None)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, engagement=None)])) == 0

    # 4. Nested explicit null or string scores rejected
    res_null_tot = json.loads(valid_base["result"])
    res_null_tot["total"] = None
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, result=json.dumps(res_null_tot))])) == 0

    res_str_det = json.loads(valid_base["result"])
    res_str_det["stages"] = {"detection": "85.0", "classification": 85.0, "engagement": 85.0}
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, result=json.dumps(res_str_det))])) == 0

    # 5. Out-of-range and non-finite scores rejected
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=-0.1)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=100.1)])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=float("nan"))])) == 0
    assert len(adaptive.get_qualifying_sessions([dict(valid_base, total=float("inf"))])) == 0

    # 6. Supported numeric types: int, float, Decimal are accepted
    from decimal import Decimal
    s_int = dict(valid_base, total=85, detection=80, classification=90, engagement=85)
    assert len(adaptive.get_qualifying_sessions([s_int])) == 1

    s_dec = dict(valid_base, total=Decimal("85.5"), detection=Decimal("80.0"), classification=Decimal("90.0"), engagement=Decimal("85.0"))
    assert len(adaptive.get_qualifying_sessions([s_dec])) == 1

    # 7. Contradictory scores between top-level and nested rejected
    res_contra = json.loads(valid_base["result"])
    res_contra["total"] = 40.0
    s_contra = dict(valid_base, total=90.0, result=json.dumps(res_contra))
    assert len(adaptive.get_qualifying_sessions([s_contra])) == 0


def test_edge_case_invalid_evidence_mixed_with_valid_history_and_curriculum_gate():
    """Verify that invalid records mixed with valid history do not increase sample size,
    alter mastery/confidence, or unlock curriculum stages.
    """
    trainee = {"id": 99, "callsign": "GATE-TESTER", "unit": "1 TRG BN"}

    # 2 genuinely valid sessions with high scores (85.0)
    valid_sessions = [
        _make_session(scenario_id="s1-dawn-recon", total=85.0, detection=85.0, classification=85.0, engagement=85.0, grade="A"),
        _make_session(scenario_id="s2-night-loiter", total=85.0, detection=85.0, classification=85.0, engagement=85.0, grade="A"),
    ]

    # Baseline skill evaluation with only 2 sessions
    base_prof = adaptive.evaluate_trainee_skills(valid_sessions)
    assert base_prof["sample_size"] == 2
    assert base_prof["confidence"] == "LOW"
    assert base_prof["mastery_level"] == "NOVICE"

    # Baseline recommendation: with only 2 sessions, cannot reach EXPERT or REC-06
    base_rec = adaptive.recommend_next_scenario(trainee, valid_sessions)
    assert base_rec["recommendation"]["rule_id"] != "REC-06-SWARM-TRIAGE-MASTERY"

    # Add 4 invalid sessions with various malformed edge cases:
    # - Session with string score "95.0"
    # - Session with explicit null penalty breaches=None
    # - Session with explicit null session_status=None
    # - Session with contradictory top/nested scores (top=90, nest=20)
    res_contra = json.loads(valid_sessions[0]["result"])
    res_contra["total"] = 20.0

    invalid_sessions = [
        dict(_make_session(scenario_id="s1-dawn-recon", grade="A", total="95.0")),
        dict(_make_session(scenario_id="s1-dawn-recon", grade="A", total=90.0), breaches=None),
        dict(_make_session(scenario_id="s1-dawn-recon", grade="A", total=90.0), session_status=None),
        dict(_make_session(scenario_id="s1-dawn-recon", grade="A", total=90.0), result=json.dumps(res_contra)),
    ]

    mixed_history = valid_sessions + invalid_sessions
    assert len(mixed_history) == 6  # 2 valid + 4 invalid

    # Evaluate mixed history: invalid sessions MUST NOT affect sample size or metrics
    mixed_prof = adaptive.evaluate_trainee_skills(mixed_history)
    assert mixed_prof["sample_size"] == 2, "Invalid sessions must not increase sample size"
    assert mixed_prof["confidence"] == "LOW", "Invalid sessions must not elevate confidence"
    assert mixed_prof["mastery_level"] == "NOVICE", "Invalid sessions must not elevate mastery"
    assert mixed_prof["average_score"] == 85.0, "Invalid sessions must not alter average score"

    # Curriculum gating: invalid sessions MUST NOT unlock REC-06 (which requires >=3 qualifying sessions)
    mixed_rec = adaptive.recommend_next_scenario(trainee, mixed_history)
    assert mixed_rec["skill_profile"]["sample_size"] == 2
    assert mixed_rec["recommendation"]["rule_id"] != "REC-06-SWARM-TRIAGE-MASTERY"

    # Now add a 3rd genuinely valid session
    third_valid = _make_session(scenario_id="s3-urban-canyon", total=85.0, detection=85.0, classification=85.0, engagement=85.0, grade="A")
    unlocked_history = mixed_history + [third_valid]

    unlocked_rec = adaptive.recommend_next_scenario(trainee, unlocked_history)
    assert unlocked_rec["skill_profile"]["sample_size"] == 3
    # With 3 valid sessions averaging 85.0 (>= expert_score 82.0), REC-06 is legitimately unlocked!
    assert unlocked_rec["recommendation"]["rule_id"] == "REC-06-SWARM-TRIAGE-MASTERY"
    assert unlocked_rec["recommendation"]["scenario_id"] == "s6-saturation-swarm"


def test_contact_level_evidence_validation_and_diagnosis_protection():
    """Verify that contact-level evidence validation strictly enforces boolean scored,
    finite numeric non-negative timestamps without defaulting spawn_t to zero,
    and valid rubric classification vocabulary. Proves malformed contacts cannot
    fabricate latency or confusion hotspots or distort recommendations in mixed histories.
    """
    trainee = {"id": 105, "callsign": "CONTACT-VALIDATOR", "unit": "1 TRG BN"}

    # Construct session with isolated valid contact + myriad malformed contacts
    contacts = [
        # Genuinely valid contact: spawn_t=10.0, det_t=14.0 -> delta=4.0; DECOY -> ARMED_UAS confusion
        {
            "id": "C_VALID_1",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 14.0},
            "true_class": "DECOY",
            "classification": {"chosen": "ARMED_UAS"},
        },
        # Malformed scored: string "false" (must not be treated as truthy!)
        {
            "id": "C_BAD_SCORED_1",
            "scored": "false",
            "spawn_t": 1.0,
            "detection": {"t": 95.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "BIRD"},
        },
        # Malformed scored: string "true" (must require exact boolean True)
        {
            "id": "C_BAD_SCORED_2",
            "scored": "true",
            "spawn_t": 1.0,
            "detection": {"t": 99.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "BIRD"},
        },
        # Malformed scored: integer 1
        {
            "id": "C_BAD_SCORED_3",
            "scored": 1,
            "spawn_t": 1.0,
            "detection": {"t": 88.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "BIRD"},
        },
        # Missing spawn_t: None (must NOT default to 0.0, which would fabricate 18.0 - 0 = 18.0s latency)
        {
            "id": "C_NULL_SPAWN",
            "scored": True,
            "spawn_t": None,
            "detection": {"t": 18.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # String spawn_t
        {
            "id": "C_STR_SPAWN",
            "scored": True,
            "spawn_t": "10.0",
            "detection": {"t": 20.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Negative spawn_t
        {
            "id": "C_NEG_SPAWN",
            "scored": True,
            "spawn_t": -5.0,
            "detection": {"t": 20.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Non-finite spawn_t (NaN / Inf)
        {
            "id": "C_NAN_SPAWN",
            "scored": True,
            "spawn_t": float("nan"),
            "detection": {"t": 20.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Malformed detection object: string instead of dict
        {
            "id": "C_STR_DET",
            "scored": True,
            "spawn_t": 10.0,
            "detection": "fast_detection",
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Malformed detection timestamp: non-numeric string
        {
            "id": "C_BAD_DET_T",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": "fast"},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Chronology inversion: detection before spawn (impossible)
        {
            "id": "C_EARLY_DET",
            "scored": True,
            "spawn_t": 25.0,
            "detection": {"t": 10.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Unexpected true_class not in vocabulary (e.g. UFO)
        {
            "id": "C_ALIEN_TRUE",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 15.0},
            "true_class": "UFO_SWARM",
            "classification": {"chosen": "BIRD"},
        },
        # Unexpected chosen class not in vocabulary (e.g. DRAGON)
        {
            "id": "C_ALIEN_CHOSEN",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 15.0},
            "true_class": "BIRD",
            "classification": {"chosen": "MYTHICAL_DRAGON"},
        },
    ]

    sess1 = _make_session(
        scenario_id="s1-dawn-recon",
        total=85.0,
        detection=85.0,
        classification=85.0,
        engagement=85.0,
        grade="A",
        contacts=contacts,
    )

    # 1. Single session diagnostic assertions
    prof1 = adaptive.evaluate_trainee_skills([sess1])
    assert prof1["sample_size"] == 1
    # Only C_VALID_1 should be counted for latency: 14.0 - 10.0 = 4.0s
    assert prof1["diagnostics"]["mean_time_to_detect_s"] == 4.0
    # Only C_VALID_1 confusion should be recorded: DECOY -> ARMED_UAS
    assert prof1["diagnostics"]["confusion_hotspots"] == [{"pattern": "DECOY -> ARMED_UAS", "count": 1}]

    # 2. Mixed history protection test:
    # A second clean session without confusion and with fast detection
    sess2_clean = _make_session(
        scenario_id="s1-dawn-recon",
        total=85.0,
        detection=85.0,
        classification=85.0,
        engagement=85.0,
        grade="A",
        contacts=[
            {"scored": True, "spawn_t": 5.0, "detection": {"t": 7.0}, "true_class": "RECON_UAS", "classification": {"chosen": "RECON_UAS"}},
        ],
    )

    prof_mixed = adaptive.evaluate_trainee_skills([sess1, sess2_clean])
    assert prof_mixed["sample_size"] == 2
    # Latency: (4.0 + 2.0) / 2 = 3.0s
    assert prof_mixed["diagnostics"]["mean_time_to_detect_s"] == 3.0
    # Detection rating remains STRONG (fast detection, high score)
    assert prof_mixed["dimensions"]["detection"]["rating"] == "STRONG"
    # Confusion hotspots still only contains valid pair, count 1
    assert prof_mixed["diagnostics"]["confusion_hotspots"] == [{"pattern": "DECOY -> ARMED_UAS", "count": 1}]

    # 3. Recommendation decision is NOT hijacked by malformed contacts
    # Should NOT trigger REC-04 (rapid detection popup) or REC-03 (restraint) from corrupt contact noise
    rec_mixed = adaptive.recommend_next_scenario(trainee, [sess1, sess2_clean])
    assert rec_mixed["recommendation"]["rule_id"] != "REC-04-RAPID-DETECTION-POPUP"
    assert rec_mixed["recommendation"]["rule_id"] != "REC-03-DISCRIMINATION-AND-RESTRAINT"


def test_session_bounded_contact_timestamp_validation_and_diagnosis_protection():
    """Verify that spawn and detection timestamps are strictly bounded by the actual session timeline.

    Proves:
    - Valid spawn and detection pairs within the session are accepted for detection latency.
    - Spawn time after the session ends is rejected from latency calculation.
    - Detection time after the session ends is rejected from latency calculation.
    - Detection timestamps within [0, 10000] range but outside session timeline are rejected.
    - Early-terminated sessions (with ended_t) bound timestamps by min(ended_t, duration_s) + tol.
    - Legacy results without ended_t bound timestamps by authoritative scenario duration + tol.
    - Legacy results without ended_t and without resolvable scenario duration do NOT calculate latency.
    - Classification confusion evidence remains independent for valid labels even when timing is invalid.
    - Mixed history proves corrupt/impossible timestamps cannot distort mean detection latency,
      skill ratings (e.g. falsely degrading detection to WEAK), or alter scenario recommendations (REC-04).
    """
    trainee = {"id": 105, "callsign": "BOUND-1", "unit": "1 TRG BN"}

    # 1. Early-terminated session (ended_t = 30.0, scenario s1-dawn-recon duration = 170.0, tol = 0.5)
    # Session boundary is min(30.0, 170.0) + 0.5 = 30.5s.
    early_contacts = [
        # Valid contact within early session: spawn 8.0, det 13.0 -> latency 5.0s
        {
            "id": "C_VALID_EARLY",
            "scored": True,
            "spawn_t": 8.0,
            "detection": {"t": 13.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Spawn after session end: spawn 32.0 > 30.5s -> rejected from latency
        {
            "id": "C_SPAWN_AFTER_END",
            "scored": True,
            "spawn_t": 32.0,
            "detection": {"t": 34.0},
            "true_class": "ARMED_UAS",
            "classification": {"chosen": "ARMED_UAS"},
        },
        # Detection after session end: spawn 15.0 <= 30.5, but det 33.0 > 30.5s -> rejected from latency
        {
            "id": "C_DET_AFTER_END",
            "scored": True,
            "spawn_t": 15.0,
            "detection": {"t": 33.0},
            "true_class": "DECOY",
            "classification": {"chosen": "DECOY"},
        },
        # Timestamp in [0, 10000] but far outside early session: spawn 10.0, det 150.0 -> rejected from latency
        # Has valid classification confusion: BIRD -> DECOY (must be preserved!)
        {
            "id": "C_DET_IN_RANGE_BUT_OUTSIDE_EARLY",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 150.0},
            "true_class": "BIRD",
            "classification": {"chosen": "DECOY"},
        },
    ]

    res_early = {
        "scenario": {"id": "s1-dawn-recon", "params": {}},
        "ended_t": 30.0,
        "contacts": early_contacts,
    }
    sess_early = {
        "scenario_id": "s1-dawn-recon",
        "total": 85.0,
        "detection": 85.0,
        "classification": 85.0,
        "engagement": 85.0,
        "grade": "A",
        "ended_t": 30.0,
        "false_alarms": 0,
        "breaches": 0,
        "critical_errors": 0,
        "result": json.dumps(res_early),
    }

    prof_early = adaptive.evaluate_trainee_skills([sess_early])
    assert prof_early["sample_size"] == 1
    # Only C_VALID_EARLY should be counted: 13.0 - 8.0 = 5.0s
    assert prof_early["diagnostics"]["mean_time_to_detect_s"] == 5.0
    # Classification confusion from C_DET_IN_RANGE_BUT_OUTSIDE_EARLY is preserved independently!
    assert prof_early["diagnostics"]["confusion_hotspots"] == [{"pattern": "BIRD -> DECOY", "count": 1}]

    # 2. Legacy session without ended_t (scenario s1-dawn-recon, authoritative duration = 170.0s, tol = 0.5s)
    # Session boundary is 170.0 + 0.5 = 170.5s.
    legacy_contacts = [
        # Valid contact within scenario duration: spawn 20.0, det 26.0 -> latency 6.0s
        {
            "id": "C_VALID_LEGACY",
            "scored": True,
            "spawn_t": 20.0,
            "detection": {"t": 26.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Spawn after scenario duration: spawn 180.0 > 170.5s -> rejected from latency
        {
            "id": "C_SPAWN_AFTER_LEGACY_DUR",
            "scored": True,
            "spawn_t": 180.0,
            "detection": {"t": 185.0},
            "true_class": "ARMED_UAS",
            "classification": {"chosen": "ARMED_UAS"},
        },
        # Detection after scenario duration: spawn 160.0 <= 170.5, but det 175.0 > 170.5s -> rejected from latency
        {
            "id": "C_DET_AFTER_LEGACY_DUR",
            "scored": True,
            "spawn_t": 160.0,
            "detection": {"t": 175.0},
            "true_class": "ARMED_UAS",
            "classification": {"chosen": "ARMED_UAS"},
        },
        # Timestamp in [0, 10000] (e.g. 8500.0s) outside scenario timeline -> rejected from latency
        # If accepted, 8500 - 10 = 8490s latency would corrupt MTTD!
        # Valid confusion: ARMED_UAS -> RECON_UAS
        {
            "id": "C_DET_MASSIVE_OUT_OF_BOUNDS",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 8500.0},
            "true_class": "ARMED_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
    ]

    res_legacy = {
        "scenario": {"id": "s1-dawn-recon", "params": {}},
        # Omit ended_t (legacy result)
        "contacts": legacy_contacts,
    }
    sess_legacy = {
        "scenario_id": "s1-dawn-recon",
        "total": 85.0,
        "detection": 85.0,
        "classification": 85.0,
        "engagement": 85.0,
        "grade": "A",
        "false_alarms": 0,
        "breaches": 0,
        "critical_errors": 0,
        "result": json.dumps(res_legacy),
    }

    prof_legacy = adaptive.evaluate_trainee_skills([sess_legacy])
    assert prof_legacy["sample_size"] == 1
    # Only C_VALID_LEGACY should be counted: 26.0 - 20.0 = 6.0s (not 8490s!)
    assert prof_legacy["diagnostics"]["mean_time_to_detect_s"] == 6.0
    # Independent confusion pair preserved
    assert prof_legacy["diagnostics"]["confusion_hotspots"] == [{"pattern": "ARMED_UAS -> RECON_UAS", "count": 1}]

    # 3. Unresolvable legacy session without ended_t AND unknown scenario duration
    # Cannot establish reliable timeline -> detection latency calculation is safely skipped
    res_unknown = {
        "scenario": {"id": "nonexistent-custom-scenario", "params": {}},
        "contacts": [
            {"scored": True, "spawn_t": 10.0, "detection": {"t": 15.0}, "true_class": "RECON_UAS", "classification": {"chosen": "RECON_UAS"}},
        ],
    }
    sess_unknown = {
        "scenario_id": "nonexistent-custom-scenario",
        "total": 85.0,
        "detection": 85.0,
        "classification": 85.0,
        "engagement": 85.0,
        "grade": "A",
        "false_alarms": 0,
        "breaches": 0,
        "critical_errors": 0,
        "result": json.dumps(res_unknown),
    }
    prof_unknown = adaptive.evaluate_trainee_skills([sess_unknown])
    assert prof_unknown["sample_size"] == 1
    assert prof_unknown["diagnostics"]["mean_time_to_detect_s"] is None

    # 4. Mixed history protection test:
    # Trainee has both the early session and the legacy session (plus impossible timestamps)
    prof_mixed = adaptive.evaluate_trainee_skills([sess_early, sess_legacy])
    assert prof_mixed["sample_size"] == 2
    # Latency across valid contacts only: (5.0 + 6.0) / 2 = 5.5s
    assert prof_mixed["diagnostics"]["mean_time_to_detect_s"] == 5.5
    # Detection rating remains STRONG (5.5s is well below mttd_strong_s = 10.0s and score is 85.0)
    assert prof_mixed["dimensions"]["detection"]["rating"] == "STRONG"
    # Confusion hotspots contain both valid observations from the sessions
    patterns = {h["pattern"] for h in prof_mixed["diagnostics"]["confusion_hotspots"]}
    assert patterns == {"BIRD -> DECOY", "ARMED_UAS -> RECON_UAS"}

    # Recommendation is NOT distorted by out-of-bounds timestamps:
    # Must NOT trigger REC-04 (rapid detection remediation due to high latency)
    rec_mixed = adaptive.recommend_next_scenario(trainee, [sess_early, sess_legacy])
    assert rec_mixed["recommendation"]["rule_id"] != "REC-04-RAPID-DETECTION-POPUP"


def test_session_end_tolerance_configuration_validation_and_rejection():
    """Verify that rubric geometry.session_end_tolerance_s is strictly validated.

    Proves:
    - Existing valid tolerance of 0.5 is accepted.
    - Zero tolerance (0.0) is permitted and bounds timestamps to exact session_end.
    - Negative tolerance is rejected with ValueError.
    - NaN and positive/negative infinity are rejected with ValueError.
    - The string 'Infinity' is rejected with ValueError (never disables session bound).
    - Very large tolerance (> 10.0s) is rejected with ValueError.
    - Nonnumeric strings are rejected with ValueError.
    - Booleans are rejected with ValueError.
    - In the contact-diagnostic path, invalid tolerance configurations fail fast with ValueError,
      guaranteeing an invalid configuration can never allow an out-of-session timestamp to generate latency.
    - A normal finite tolerance (0.5) with a detection timestamp after session end is safely excluded from latency.
    """
    sess = {
        "scenario_id": "s1-dawn-recon",
        "total": 80.0,
        "detection": 80.0,
        "classification": 80.0,
        "engagement": 80.0,
        "grade": "SATISFACTORY",
        "false_alarms": 0,
        "breaches": 0,
        "critical_errors": 0,
    }
    res = {
        "scenario": {"id": "s1-dawn-recon", "params": {}},
        "ended_t": 30.0,
        "contacts": [],
    }

    # 1. Existing valid tolerance of 0.5 (finite float)
    rubric_05 = {"geometry": {"session_end_tolerance_s": 0.5}}
    session_end, tol = adaptive._resolve_session_end(sess, res, rubric_05)
    assert tol == 0.5
    assert session_end == 30.0

    # 2. Zero tolerance permitted by contract (0.0 <= tol <= 10.0)
    rubric_zero = {"geometry": {"session_end_tolerance_s": 0.0}}
    session_end_z, tol_z = adaptive._resolve_session_end(sess, res, rubric_zero)
    assert tol_z == 0.0
    assert session_end_z == 30.0

    # 3. Numeric string "0.5" rejected by strict numeric policy
    rubric_str_05 = {"geometry": {"session_end_tolerance_s": "0.5"}}
    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive._resolve_session_end(sess, res, rubric_str_05)

    # 4. Numeric bytes b"0.5" rejected by strict numeric policy
    rubric_bytes_05 = {"geometry": {"session_end_tolerance_s": b"0.5"}}
    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive._resolve_session_end(sess, res, rubric_bytes_05)

    # 5. String "Infinity" rejected
    rubric_inf_str = {"geometry": {"session_end_tolerance_s": "Infinity"}}
    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive._resolve_session_end(sess, res, rubric_inf_str)

    # 6. Non-numeric string rejected
    rubric_str = {"geometry": {"session_end_tolerance_s": "unbounded"}}
    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive._resolve_session_end(sess, res, rubric_str)

    # 7. Boolean True rejected (subclass of int in Python)
    rubric_bool_true = {"geometry": {"session_end_tolerance_s": True}}
    with pytest.raises(ValueError, match="Invalid boolean value"):
        adaptive._resolve_session_end(sess, res, rubric_bool_true)

    rubric_bool_false = {"geometry": {"session_end_tolerance_s": False}}
    with pytest.raises(ValueError, match="Invalid boolean value"):
        adaptive._resolve_session_end(sess, res, rubric_bool_false)

    # 8. NaN and positive/negative infinity rejected
    rubric_nan = {"geometry": {"session_end_tolerance_s": float("nan")}}
    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive._resolve_session_end(sess, res, rubric_nan)

    rubric_inf = {"geometry": {"session_end_tolerance_s": float("inf")}}
    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive._resolve_session_end(sess, res, rubric_inf)

    rubric_neginf = {"geometry": {"session_end_tolerance_s": float("-inf")}}
    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive._resolve_session_end(sess, res, rubric_neginf)

    # 9. Negative tolerance values (< 0.0) rejected
    rubric_neg = {"geometry": {"session_end_tolerance_s": -0.5}}
    with pytest.raises(ValueError, match="below minimum allowed"):
        adaptive._resolve_session_end(sess, res, rubric_neg)

    rubric_neg_tiny = {"geometry": {"session_end_tolerance_s": -0.0001}}
    with pytest.raises(ValueError, match="below minimum allowed"):
        adaptive._resolve_session_end(sess, res, rubric_neg_tiny)

    # 10. Values above 10.0 (> 10.0s) rejected
    rubric_above_10 = {"geometry": {"session_end_tolerance_s": 10.001}}
    with pytest.raises(ValueError, match="exceeds maximum allowed"):
        adaptive._resolve_session_end(sess, res, rubric_above_10)

    rubric_huge = {"geometry": {"session_end_tolerance_s": 100.0}}
    with pytest.raises(ValueError, match="exceeds maximum allowed"):
        adaptive._resolve_session_end(sess, res, rubric_huge)

    # 11. Preserves default 0.5 when setting is omitted or None
    _, tol_none_rubric = adaptive._resolve_session_end(sess, res, None)
    assert tol_none_rubric == 0.5

    _, tol_empty_geo = adaptive._resolve_session_end(sess, res, {"geometry": {}})
    assert tol_empty_geo == 0.5

    _, tol_none_val = adaptive._resolve_session_end(sess, res, {"geometry": {"session_end_tolerance_s": None}})
    assert tol_none_val == 0.5

    # 9. Contact-diagnostic path assertions:
    # A session with contacts whose detection timestamps are relative to ended_t = 30.0
    test_contacts = [
        # Exactly at session end (t = 30.0s)
        {
            "id": "C_AT_END",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 30.0},
            "true_class": "RECON_UAS",
            "classification": {"chosen": "RECON_UAS"},
        },
        # Within 0.5s tolerance (30.3 <= 30.5) but outside 0.0 tolerance (30.3 > 30.0)
        {
            "id": "C_IN_TOL_ONLY",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 30.3},
            "true_class": "ARMED_UAS",
            "classification": {"chosen": "ARMED_UAS"},
        },
        # Outside 0.5s tolerance (31.0 > 30.5)
        {
            "id": "C_AFTER_TOL",
            "scored": True,
            "spawn_t": 10.0,
            "detection": {"t": 31.0},
            "true_class": "DECOY",
            "classification": {"chosen": "DECOY"},
        },
    ]

    res_diag = {
        "scenario": {"id": "s1-dawn-recon", "params": {}},
        "ended_t": 30.0,
        "contacts": test_contacts,
    }
    sess_diag = {
        "scenario_id": "s1-dawn-recon",
        "total": 85.0,
        "detection": 85.0,
        "classification": 85.0,
        "engagement": 85.0,
        "grade": "A",
        "ended_t": 30.0,
        "false_alarms": 0,
        "breaches": 0,
        "critical_errors": 0,
        "result": json.dumps(res_diag),
    }

    # Under standard 0.5s tolerance: C_AT_END (20.0s) and C_IN_TOL_ONLY (20.3s) are accepted; C_AFTER_TOL is rejected
    prof_05 = adaptive.evaluate_trainee_skills([sess_diag], rubric_05)
    assert prof_05["diagnostics"]["mean_time_to_detect_s"] == round((20.0 + 20.3) / 2, 1)

    # Under 0.0 zero tolerance: only C_AT_END (20.0s) is accepted; C_IN_TOL_ONLY and C_AFTER_TOL are rejected
    prof_zero = adaptive.evaluate_trainee_skills([sess_diag], rubric_zero)
    assert prof_zero["diagnostics"]["mean_time_to_detect_s"] == 20.0

    # Under invalid configurations: evaluate_trainee_skills fails fast with ValueError,
    # ensuring no out-of-session timestamp can ever generate detection latency.
    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_inf_str)

    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_str_05)

    with pytest.raises(ValueError, match="String or bytes value not permitted"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_bytes_05)

    with pytest.raises(ValueError, match="Invalid NaN or infinite value"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_nan)

    with pytest.raises(ValueError, match="below minimum allowed"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_neg)

    with pytest.raises(ValueError, match="exceeds maximum allowed"):
        adaptive.evaluate_trainee_skills([sess_diag], rubric_huge)
