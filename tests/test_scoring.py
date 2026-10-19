"""Hand-built event logs for every branch of the scoring tree (AVD "Scoring engine")."""

import pytest

from app import rng
from app.scoring import score_session, validate_events

from helpers import contact, ev, scenario


def run(rubric, scen, events, ended_t=None):
    return score_session(scen, validate_events(events, scen, rubric, ended_t=ended_t), rubric, ended_t)


def by_id(result, cid):
    return next(c for c in result["contacts"] if c["id"] == cid)


def sure(rubric, value):
    """Make interception always succeed (1.0) or always fail (0.0)."""
    for model in rubric["responses"]["INTERCEPT"]["effectiveness"]:
        rubric["responses"]["INTERCEPT"]["effectiveness"][model] = value
    return rubric


# A hostile quadcopter: spawns at 0, flies 2000 m -> 40 m at 20 m/s, ends inside the ring at 98 s.
HOSTILE = dict(cid="C1", par=20.0)


# ---------------------------------------------------------------- detection

def test_missed_hostile_breaches_and_scores_zero(rubric):
    r = run(rubric, scenario(contact(**HOSTILE)), [])
    c = by_id(r, "C1")
    assert c["path"] == ["detection/missed", "classification/not_marked", "engagement/breach"]
    assert c["breached"] and r["penalties"]["breaches"] == 1 and r["penalties"]["breach_points"] == 10
    assert r["stages"] == {"detection": 0.0, "classification": 0.0, "engagement": 0.0}
    assert r["total"] == 0.0  # clamped at zero
    assert r["grade"] == "F"


@pytest.mark.parametrize("t,node,points", [
    (5.0, "detected_fast", 1.0),       # 0.25x par
    (10.0, "detected_fast", 1.0),      # exactly 0.5x
    (16.0, "detected_on_par", 0.75),   # 0.8x
    (30.0, "detected_slow", 0.4),      # 1.5x
    (60.0, "detected_very_slow", 0.1), # 3x
])
def test_detection_tiers(rubric, t, node, points):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(t, "mark", "C1")])
    det = by_id(r, "C1")["detection"]
    assert (det["node"], det["points"]) == (node, points)
    assert "par" in det["reason"]


def test_false_alarms_capped(rubric):
    events = [ev(1.0 + i, "mark") for i in range(7)] + [ev(2.0, "mark", "NOPE")]
    r = run(rubric, scenario(contact(**HOSTILE)), events)
    assert r["penalties"]["false_alarms"] == 8
    assert r["penalties"]["false_alarm_points"] == 10


def test_mark_before_spawn_is_false_alarm(rubric):
    r = run(rubric, scenario(contact(cid="C1", spawn=50.0)), [ev(10.0, "mark", "C1")])
    assert r["penalties"]["false_alarms"] == 1
    assert by_id(r, "C1")["detection"]["node"] == "missed"


# ---------------------------------------------------------------- classification

@pytest.mark.parametrize("chosen,node,points,critical", [
    ("RECON_UAS", "exact", 1.0, False),
    ("ARMED_UAS", "same_family", 0.5, False),
    ("BIRD", "critical_misclassification", 0.0, True),
    ("FRIENDLY", "critical_misclassification", 0.0, True),
])
def test_classification_branches(rubric, chosen, node, points, critical):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": chosen})])
    cls = by_id(r, "C1")["classification"]
    assert (cls["node"], cls["points"]) == (node, points)
    assert (r["penalties"]["critical_errors"] == 1) is critical
    if critical:
        assert r["penalties"]["critical_points"] == 25


def test_wrong_family_on_benign_is_not_critical(rubric):
    bird = contact("C2", model="bird", threat="benign", start=800, end=600, speed=10)
    r = run(rubric, scenario(contact(**HOSTILE), bird),
            [ev(3, "mark", "C2"), ev(4, "classify", "C2", **{"class": "FRIENDLY"})])
    assert by_id(r, "C2")["classification"]["node"] == "wrong_family"
    assert r["penalties"]["critical_errors"] == 0


def test_last_classification_counts(rubric):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "BIRD"}),
                                                   ev(8, "classify", "C1", **{"class": "RECON_UAS"})])
    assert by_id(r, "C1")["classification"]["node"] == "exact"
    assert r["penalties"]["critical_errors"] == 0


def test_marked_but_not_classified(rubric):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1")])
    assert by_id(r, "C1")["classification"]["node"] == "not_classified"


# ---------------------------------------------------------------- engagement, hostile

def test_correct_timely_effective(rubric):
    sure(rubric, 1.0)
    r = run(rubric, scenario(contact(**HOSTILE)),
            [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}), ev(50, "respond", "C1", response="INTERCEPT")])
    c = by_id(r, "C1")
    assert c["engagement"]["node"] == "correct_effective" and c["engagement"]["points"] == 1.0
    assert c["neutralised_t"] == 50 and not c["breached"]
    assert r["total"] == 100.0 and r["grade"] == "A"


def test_correct_but_failed_roll_is_credited_and_breach_still_penalised(rubric):
    sure(rubric, 0.0)
    r = run(rubric, scenario(contact(**HOSTILE)),
            [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}), ev(50, "respond", "C1", response="INTERCEPT")])
    c = by_id(r, "C1")
    assert c["engagement"]["node"] == "correct_failed_roll" and c["engagement"]["points"] == 0.6
    assert c["breached"] and r["penalties"]["breach_points"] == 10
    assert r["total"] == pytest.approx(30 + 30 + 40 * 0.6 - 10)


def _fail_then_succeed(rubric):
    """A seed and an intercept chance where attempt 1 misses and attempt 2 hits."""
    seed = next(sd for sd in range(1, 500) if rng.roll(sd, "C1", 0) > rng.roll(sd, "C1", 1) + 0.1)
    sure(rubric, (rng.roll(seed, "C1", 0) + rng.roll(seed, "C1", 1)) / 2)
    return seed


def test_timely_successful_retry_scores_full_credit(rubric):
    """Issue #15: a suitable first try that misses, then a retry that stops the drone before
    the late line, earns 100%, not the 60% of someone who gave up after the miss."""
    seed = _fail_then_succeed(rubric)
    r = run(rubric, scenario(contact(**HOSTILE), seed=seed),
            [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}),
             ev(50, "respond", "C1", response="INTERCEPT"), ev(60, "respond", "C1", response="INTERCEPT")])
    c = by_id(r, "C1")
    assert [a["success"] for a in c["attempts"]] == [False, True]
    assert c["engagement"]["node"] == "correct_effective" and c["engagement"]["points"] == 1.0
    assert "attempt 2" in c["engagement"]["reason"] and not c["breached"]
    assert r["total"] == 100.0


def test_late_successful_retry_keeps_the_failed_roll_credit(rubric):
    """The retry has to come before the late line (300 m) to count as timely."""
    seed = _fail_then_succeed(rubric)
    # At 20 m/s from 2000 m, the contact is inside 300 m after about 85 s.
    r = run(rubric, scenario(contact(**HOSTILE), seed=seed),
            [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}),
             ev(50, "respond", "C1", response="INTERCEPT"), ev(90, "respond", "C1", response="INTERCEPT")])
    c = by_id(r, "C1")
    assert [a["success"] for a in c["attempts"]] == [False, True]
    assert c["engagement"]["node"] == "correct_failed_roll" and c["engagement"]["points"] == 0.6


def test_unsuitable_first_choice_is_not_rescued_by_a_retry(rubric):
    """Choosing right the first time is the skill (Night Loiter): jamming a fixed-wing stays 20%
    even if a later intercept stops it."""
    sure(rubric, 1.0)
    r = run(rubric, scenario(contact(model="fixed_wing", **HOSTILE)),
            [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "ARMED_UAS"}),
             ev(40, "respond", "C1", response="JAM"), ev(45, "respond", "C1", response="INTERCEPT")])
    c = by_id(r, "C1")
    assert c["neutralised_t"] is not None
    assert c["engagement"]["node"] == "unsuitable" and c["engagement"]["points"] == 0.2


def test_unsuitable_response(rubric):
    fw = contact("C1", model="fixed_wing", speed=35)
    r = run(rubric, scenario(fw), [ev(5, "mark", "C1"), ev(20, "respond", "C1", response="JAM")])
    # The jam (10% chance) almost surely fails, so the drone breaches; an unsuitable choice that breaches scores 0.
    c = by_id(r, "C1")
    if c["breached"]:
        assert c["engagement"]["node"] == "breach"
    else:
        assert c["engagement"]["node"] == "unsuitable" and c["engagement"]["points"] == 0.2


def test_unsuitable_without_breach_scores_twenty(rubric):
    # Session ends before the contact arrives, so there is no breach.
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(20, "respond", "C1", response="TAKE_COVER")],
            ended_t=60)
    eng = by_id(r, "C1")["engagement"]
    assert (eng["node"], eng["points"]) == ("unsuitable", 0.2)


def test_late_response(rubric):
    sure(rubric, 1.0)
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(92, "respond", "C1", response="INTERCEPT")])
    eng = by_id(r, "C1")["engagement"]
    assert (eng["node"], eng["points"]) == ("late", 0.2)


def test_no_response_without_breach(rubric):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1")], ended_t=60)
    eng = by_id(r, "C1")["engagement"]
    assert (eng["node"], eng["points"]) == ("no_response", 0.0)
    assert r["penalties"]["breaches"] == 0


def test_track_only_is_no_response(rubric):
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(6, "respond", "C1", response="TRACK")], ended_t=60)
    assert by_id(r, "C1")["engagement"]["node"] == "no_response"


def test_scenario_override_accepts_report(rubric):
    flyby = contact("C1", end=500, expected_responses=["REPORT", "JAM", "INTERCEPT"])
    r = run(rubric, scenario(flyby), [ev(5, "mark", "C1"), ev(20, "respond", "C1", response="REPORT")])
    eng = by_id(r, "C1")["engagement"]
    assert (eng["node"], eng["points"]) == ("correct_effective", 1.0)
    assert not by_id(r, "C1")["breached"]  # path ends outside the ring


def test_out_of_range_intercept_is_weakened(rubric):
    sure(rubric, 0.8)
    c = contact(**HOSTILE)
    from app.scoring import effectiveness
    assert effectiveness(rubric, "INTERCEPT", c, 10) == pytest.approx(0.8 * 0.25)  # ~1800 m, beyond 1500 m
    assert effectiveness(rubric, "INTERCEPT", c, 40) == pytest.approx(0.8)         # ~1200 m, in range
    assert effectiveness(rubric, "TRACK", c, 40) == 0.0                            # does not engage


def test_server_reruns_the_roll(rubric):
    """The roll comes from the scenario seed, so the outcome is fixed and reproducible."""
    s = scenario(contact(**HOSTILE), seed=12345)
    events = [ev(5, "mark", "C1"), ev(50, "respond", "C1", response="INTERCEPT")]
    r = run(rubric, s, events)
    att = by_id(r, "C1")["attempts"][0]
    assert att["roll"] == pytest.approx(round(rng.roll(12345, "C1", 0), 4))
    assert att["success"] == (rng.roll(12345, "C1", 0) < att["effectiveness"])


# ---------------------------------------------------------------- non-hostile contacts

def test_restraint_on_bird(rubric):
    bird = contact("C2", model="bird", threat="benign", start=800, end=600, speed=10)
    r = run(rubric, scenario(contact(**HOSTILE), bird), [ev(3, "mark", "C2"), ev(4, "respond", "C2", response="TRACK")])
    eng = by_id(r, "C2")["engagement"]
    assert (eng["node"], eng["points"]) == ("restraint", 1.0)


def test_unnecessary_engagement_of_decoy(rubric):
    balloon = contact("C2", model="balloon", threat="decoy", start=1500, end=600, speed=4)
    r = run(rubric, scenario(contact(**HOSTILE), balloon), [ev(3, "mark", "C2"), ev(4, "respond", "C2", response="INTERCEPT")])
    assert by_id(r, "C2")["engagement"]["node"] == "unnecessary_engagement"
    assert r["penalties"]["critical_errors"] == 0


def test_friendly_engaged_is_critical(rubric):
    friend = contact("C2", model="friendly_aircraft", threat="friendly", start=3000, end=1000, speed=55)
    r = run(rubric, scenario(contact(**HOSTILE), friend), [ev(3, "mark", "C2"), ev(4, "respond", "C2", response="JAM")])
    c = by_id(r, "C2")
    assert c["engagement"]["node"] == "friendly_engaged" and "friendly_engaged" in c["critical"]
    assert r["penalties"]["critical_points"] == 25


def test_unmarked_non_hostile_not_scored(rubric):
    bird = contact("C2", model="bird", threat="benign", start=800, end=600, speed=10)
    r = run(rubric, scenario(contact(**HOSTILE), bird), [])
    assert by_id(r, "C2")["scored"] is False
    assert len([c for c in r["contacts"] if c["scored"]]) == 1


# ---------------------------------------------------------------- totals, weights, purity

def test_weights_come_from_rubric(rubric):
    events = [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"})]
    s = scenario(contact(**HOSTILE))
    base = run(rubric, s, events, ended_t=60)
    assert base["weighted"] == pytest.approx(60.0)
    rubric["weights"] = {"detection": 50, "classification": 50, "engagement": 0}
    changed = run(rubric, s, events, ended_t=60)
    assert changed["weighted"] == pytest.approx(100.0)


def test_total_clamped_to_100_and_0(rubric):
    sure(rubric, 1.0)
    rubric["penalties"]["breach"] = 500
    r = run(rubric, scenario(contact(**HOSTILE)), [])
    assert r["total"] == 0.0


def test_every_scored_stage_has_reason_and_node(rubric):
    sure(rubric, 0.5)
    s = scenario(contact(**HOSTILE), contact("C2", model="bird", threat="benign", start=800, end=600, speed=10))
    r = run(rubric, s, [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "ARMED_UAS"}),
                        ev(30, "respond", "C1", response="JAM"), ev(9, "mark", "C2"), ev(9.5, "mark")])
    for c in r["contacts"]:
        if c["scored"]:
            for stage in ("detection", "classification", "engagement"):
                assert c[stage]["node"] and c[stage]["reason"]
            assert len(c["path"]) == 3
    noted = [n for item in r["timeline"] for n in item["notes"]]
    assert all(n["reason"] for n in noted)
    assert any(n["node"] == "false_alarm" for n in noted)


def test_scoring_is_pure(rubric):
    s = scenario(contact(**HOSTILE))
    events = [ev(5, "mark", "C1"), ev(40, "respond", "C1", response="JAM")]
    assert run(rubric, s, events) == run(rubric, s, events)


# ---------------------------------------------------------------- validation

@pytest.mark.parametrize("bad", [
    [ev(-1, "mark", "C1")],
    [ev(10_000, "mark", "C1")],
    [ev(1, "shoot", "C1")],
    [ev(1, "classify", "C1", **{"class": "UFO"})],
    [ev(1, "respond", "C1", response="NUKE")],
    [ev(1, "respond", "C9", response="JAM")],
    [{"t": "soon", "type": "mark"}],
    [{"t": True, "type": "mark"}],
    "not a list",
    [ev(1, "mark")] * 5001,
])
def test_bad_events_rejected(rubric, bad):
    with pytest.raises(ValueError):
        validate_events(bad, scenario(contact(**HOSTILE)), rubric)


def test_take_cover_is_right_when_the_drone_stays_out_of_reach(rubric):
    """Issue #14, R8 (ATP 3-01.81): when the threat stays outside the range of every suitable
    response (jam 2,000 m, intercept 1,500 m), taking cover scores full engagement credit."""
    far = contact("C1", start=4000.0, end=2500.0, par=20.0)
    r = run(rubric, scenario(far), [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}),
                                    ev(8, "respond", "C1", response="TAKE_COVER")])
    c = by_id(r, "C1")
    assert c["engagement"]["node"] == "correct_passive" and c["engagement"]["points"] == 1.0
    assert "2000 m" in c["engagement"]["reason"]


def test_take_cover_is_unsuitable_when_the_drone_comes_in_range(rubric):
    """The same choice against a drone that later closes in (and could have been engaged) stays 20%."""
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}),
                                                   ev(8, "respond", "C1", response="TAKE_COVER")])
    assert by_id(r, "C1")["engagement"]["node"] in ("unsuitable", "breach")
    assert by_id(r, "C1")["engagement"]["points"] <= 0.2


def test_cover_first_then_engaging_in_range_is_scored_on_the_engagement(rubric):
    sure(rubric, 1.0)
    r = run(rubric, scenario(contact(**HOSTILE)), [ev(5, "mark", "C1"), ev(6, "classify", "C1", **{"class": "RECON_UAS"}),
                                                   ev(8, "respond", "C1", response="TAKE_COVER"),
                                                   ev(50, "respond", "C1", response="INTERCEPT")])
    assert by_id(r, "C1")["engagement"]["node"] == "correct_effective"


def test_relabelled_responses(rubric):
    """Issue #14, R6: soft kill and hard kill, the terms in India's counter-drone guidelines."""
    assert rubric["responses"]["JAM"]["label"] == "Jam (soft kill)"
    assert rubric["responses"]["INTERCEPT"]["label"] == "Intercept (hard kill)"
