import json

import pytest

from app import scenario as scen
from app.geometry import end_time

MODELS = set(scen.BASE_SPEED)
THREATS = {"hostile", "decoy", "benign", "friendly"}


@pytest.mark.parametrize("difficulty", [1, 2, 3, 4, 5])
def test_same_seed_gives_identical_json(difficulty):
    a = scen.generate({"seed": 48213, "difficulty": difficulty})
    b = scen.generate({"seed": 48213, "difficulty": difficulty})
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_same_seed_and_overrides_identical():
    p = {"seed": 9, "difficulty": 4, "time_of_day": "night", "terrain": "urban", "swarm": 12, "degradation": 3}
    assert scen.generate(p) == scen.generate(dict(p))


def test_different_seeds_differ():
    a = scen.generate({"seed": 1, "difficulty": 3})
    b = scen.generate({"seed": 2, "difficulty": 3})
    assert a["contacts"] != b["contacts"]


@pytest.mark.parametrize("difficulty", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("seed", [3, 77, 4242])
def test_difficulty_table_is_respected(difficulty, seed):
    table = scen.DIFFICULTY[difficulty]
    s = scen.generate({"seed": seed, "difficulty": difficulty})
    counts = {t: sum(1 for c in s["contacts"] if c["threat"] == t) for t in THREATS}
    swarm = sum(1 for c in s["contacts"] if c["swarm"])
    assert counts["hostile"] - swarm == table["hostile"]
    assert table["swarm_max"] // 2 <= swarm <= table["swarm_max"]
    assert counts["decoy"] == table["decoy"]
    assert counts["benign"] == table["benign"]
    assert s["environment"]["degradation"] == table["degradation"]
    single = [c for c in s["contacts"] if c["threat"] == "hostile" and not c["swarm"]]
    for c in single:
        assert c["speed_mps"] == pytest.approx(round(scen.BASE_SPEED[c["model"]] * table["speed"], 1))


def test_degradation_sets_environment():
    s = scen.generate({"seed": 5, "degradation": 3})
    env = s["environment"]
    assert (env["visual_range_m"], env["radar_dropout"]) == (900, 0.30)


def test_manual_swarm_up_to_twelve():
    s = scen.generate({"seed": 11, "difficulty": 5, "swarm": 12})
    assert sum(1 for c in s["contacts"] if c["swarm"]) == 12


@pytest.mark.parametrize("bad", [{"seed": "x"}, {"seed": -1}, {"difficulty": 6}, {"swarm": 13},
                                 {"time_of_day": "noon"}, {"terrain": "sea"}, {"degradation": 4}])
def test_invalid_params_rejected(bad):
    with pytest.raises(ValueError):
        scen.generate(bad)


def _check_schema(s):
    assert {"id", "name", "kind", "seed", "objective", "duration_s", "environment", "contacts"} <= set(s)
    env = s["environment"]
    assert env["time_of_day"] in scen.TIMES_OF_DAY and env["terrain"] in scen.TERRAINS
    assert {"terrain_seed", "fog", "noise", "radar_dropout", "visual_range_m"} <= set(env)
    ids = [c["id"] for c in s["contacts"]]
    assert len(ids) == len(set(ids))
    assert any(c["threat"] == "hostile" for c in s["contacts"])
    for c in s["contacts"]:
        assert c["model"] in MODELS and c["threat"] in THREATS
        assert c["true_class"] == scen.TRUE_CLASS[c["model"]]
        assert len(c["waypoints"]) >= 2 and all(len(w) == 3 for w in c["waypoints"])
        assert c["speed_mps"] > 0 and c["par_detect_s"] >= 8
        if c["threat"] == "hostile":
            assert end_time(c) <= s["duration_s"]


def test_six_scripted_scenarios_validate():
    listed = scen.list_scripted()
    assert [x["order"] for x in listed] == [1, 2, 3, 4, 5, 6]
    for item in listed:
        _check_schema(scen.build_scripted(item["id"]))


@pytest.mark.parametrize("seed", range(20))
def test_procedural_scenarios_validate(seed):
    _check_schema(scen.generate({"seed": seed * 7919, "difficulty": seed % 5 + 1}))


def test_scripted_catalogue_matches_prd():
    s = {x["id"]: scen.build_scripted(x["id"]) for x in scen.list_scripted()}
    assert [c["model"] for c in s["s2-night-loiter"]["contacts"]] == ["fixed_wing"]
    mixed = sorted(c["threat"] for c in s["s4-mixed-traffic"]["contacts"])
    assert mixed == ["benign", "benign", "benign", "friendly", "hostile"]
    assert s["s5-fog-noise"]["environment"]["degradation"] == 3
    swarm = s["s6-saturation-swarm"]["contacts"]
    assert sum(1 for c in swarm if c["swarm"]) == 8 and sum(1 for c in swarm if c["threat"] == "decoy") == 2
    assert {c["swarm"]["group"] for c in swarm if c["swarm"]} == {"A", "B"}


@pytest.mark.parametrize("level,expected", [
    (0, {"noise": 0.0, "fog": 0.0, "visual_range_m": 3000, "radar_dropout": 0.0}),
    (1, {"noise": 0.1, "fog": 0.15, "visual_range_m": 2200, "radar_dropout": 0.08}),
    (2, {"noise": 0.25, "fog": 0.35, "visual_range_m": 1500, "radar_dropout": 0.18}),
    (3, {"noise": 0.45, "fog": 0.6, "visual_range_m": 900, "radar_dropout": 0.30}),
])
def test_four_degradation_levels_match_visual_design_table(level, expected):
    env = scen.generate({"seed": 3, "degradation": level})["environment"]
    assert {k: env[k] for k in expected} == expected
