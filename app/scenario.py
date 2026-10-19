"""Scenario generator: scripted scenarios from JSON files, procedural ones from a seed.

This module is the only source of scenario content. The same seed and parameters
always rebuild the same scenario JSON (see tests/test_scenario.py).
"""

import json
import math
import random
from functools import lru_cache
from pathlib import Path

from . import geometry

SCENARIO_DIR = Path(__file__).resolve().parent / "scenarios"

TIMES_OF_DAY = ("day", "dusk", "night")  # procedural choices (changing this changes every seed)
LIGHTING = TIMES_OF_DAY + ("dawn",)      # every valid time_of_day; scripted scenarios may also use dawn
TERRAINS = ("rural", "urban")

# AVD difficulty table. Swarm members are counted on top of the hostile contacts.
DIFFICULTY = {
    1: {"hostile": 1, "swarm_max": 0, "decoy": 0, "benign": 1, "friendly": 0, "degradation": 0, "speed": 1.0},
    2: {"hostile": 2, "swarm_max": 0, "decoy": 1, "benign": 2, "friendly": 0, "degradation": 0, "speed": 1.1},
    3: {"hostile": 3, "swarm_max": 3, "decoy": 2, "benign": 3, "friendly": 1, "degradation": 1, "speed": 1.2},
    4: {"hostile": 5, "swarm_max": 5, "decoy": 3, "benign": 3, "friendly": 1, "degradation": 2, "speed": 1.3},
    5: {"hostile": 8, "swarm_max": 8, "decoy": 4, "benign": 4, "friendly": 1, "degradation": 3, "speed": 1.4},
}

# Visual Design doc degradation table.
DEGRADATION = {
    0: {"noise": 0.0, "fog": 0.0, "visual_range_m": 3000, "radar_dropout": 0.0},
    1: {"noise": 0.1, "fog": 0.15, "visual_range_m": 2200, "radar_dropout": 0.08},
    2: {"noise": 0.25, "fog": 0.35, "visual_range_m": 1500, "radar_dropout": 0.18},
    3: {"noise": 0.45, "fog": 0.6, "visual_range_m": 900, "radar_dropout": 0.30},
}

BASE_SPEED = {
    "quadcopter": 15.0, "hexacopter": 12.0, "fixed_wing": 35.0,
    "balloon": 4.0, "bird": 12.0, "friendly_aircraft": 55.0,
}

# Range at which a trained observer can usually pick each contact out by eye.
ACQUIRE_RANGE_M = {
    "quadcopter": 1200, "hexacopter": 1500, "fixed_wing": 2000,
    "balloon": 1800, "bird": 800, "friendly_aircraft": 3000,
}

TRUE_CLASS = {
    "quadcopter": "RECON_UAS", "hexacopter": "ARMED_UAS", "fixed_wing": "ARMED_UAS",
    "balloon": "DECOY", "bird": "BIRD", "friendly_aircraft": "FRIENDLY",
}

LIMITS = {
    "difficulty": (1, 5), "degradation": (0, 3), "swarm": (0, 12),
    "hostile": (0, 12), "decoy": (0, 8), "benign": (0, 8), "friendly": (0, 3),
}
MAX_SEED = 2**31 - 1


# ---------------------------------------------------------------- parameters

def normalise_params(raw):
    """Validate procedural parameters. Missing values stay None and are filled from
    the seed and the difficulty table at generation time. Raises ValueError."""
    raw = raw or {}
    params = {}
    try:
        params["seed"] = int(raw.get("seed", 1))
    except (TypeError, ValueError):
        raise ValueError("seed must be an integer")
    if not 0 <= params["seed"] <= MAX_SEED:
        raise ValueError(f"seed must be between 0 and {MAX_SEED}")

    for key, (lo, hi) in LIMITS.items():
        value = raw.get(key)
        if value in (None, ""):
            params[key] = None if key != "difficulty" else 2
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{key} must be an integer")
        if not lo <= value <= hi:
            raise ValueError(f"{key} must be between {lo} and {hi}")
        params[key] = value

    for key, allowed in (("time_of_day", TIMES_OF_DAY), ("terrain", TERRAINS)):
        value = raw.get(key)
        if value in (None, ""):
            params[key] = None
        elif value in allowed:
            params[key] = value
        else:
            raise ValueError(f"{key} must be one of {', '.join(allowed)}")
    return params


# ---------------------------------------------------------------- helpers

def _xz(bearing_deg, range_m):
    """Bearing is clockwise from north; north is -z, east is +x."""
    b = math.radians(bearing_deg)
    return math.sin(b) * range_m, -math.cos(b) * range_m


def _wp(bearing_deg, range_m, alt):
    x, z = _xz(bearing_deg, range_m)
    return [round(x, 1), round(alt, 1), round(z, 1)]


def environment_for(time_of_day, terrain, terrain_seed, degradation, overrides=None):
    env = {"time_of_day": time_of_day, "terrain": terrain, "terrain_seed": terrain_seed,
           "degradation": degradation, **DEGRADATION[degradation]}
    env.update(overrides or {})
    return env


def par_detect(contact, visual_range_m):
    """Par time to detect: time until a trained observer could pick the contact out
    (its acquisition range, cut by the visual range), plus a margin to react."""
    acquire = min(ACQUIRE_RANGE_M[contact["model"]], visual_range_m * 0.75)
    t_vis = geometry.first_time_within(contact, acquire)
    if t_vis is None:
        t_vis = contact["spawn_t"] + 0.5 * (geometry.end_time(contact) - contact["spawn_t"])
    par = min(90.0, max(8.0, t_vis - contact["spawn_t"] + 8.0))
    return round(par * 2) / 2


def expand_swarm(group, rng_seed):
    """Turn a swarm group into members that follow the leader path with formation offsets."""
    rng = random.Random(rng_seed)
    wps = group["waypoints"]
    dx, dz = wps[1][0] - wps[0][0], wps[1][2] - wps[0][2]
    norm = math.hypot(dx, dz) or 1.0
    dx, dz = dx / norm, dz / norm
    px, pz = -dz, dx
    spacing = group.get("spacing_m", 30)
    members = []
    for i in range(group["count"]):
        row, col = divmod(i, 3)
        lat = (col - 1) * spacing
        back = row * spacing
        ox, oz = px * lat - dx * back, pz * lat - dz * back
        oy = 8 if i % 2 else 0
        member_wps = [[round(w[0] + ox, 1), round(w[1] + oy, 1), round(w[2] + oz, 1)] for w in wps]
        members.append({
            "model": group.get("model", "quadcopter"),
            "threat": "hostile",
            "spawn_t": round(group["spawn_t"] + i * group.get("stagger_s", 0.6), 1),
            "speed_mps": group["speed_mps"],
            "waypoints": member_wps,
            "swarm": {"group": group["swarm"], "index": i, "size": group["count"]},
            "wobble_seed": rng.randrange(1, MAX_SEED),
        })
    return members


def _finish(scenario):
    """Sort, number, add classes and par times, and stretch the duration to fit hostile paths."""
    env = scenario["environment"]
    contacts = sorted(scenario["contacts"], key=lambda c: (c["spawn_t"], c.get("order", 0)))
    for n, c in enumerate(contacts, start=1):
        c.pop("order", None)
        c["id"] = c.get("id") or f"C{n}"
        c["true_class"] = c.get("true_class") or TRUE_CLASS[c["model"]]
        c.setdefault("swarm", None)
        c.setdefault("wobble_seed", 1000 + n)
        if "par_detect_s" not in c:
            c["par_detect_s"] = par_detect(c, env["visual_range_m"])
    scenario["contacts"] = contacts
    hostile_end = max((geometry.end_time(c) for c in contacts if c["threat"] == "hostile"), default=0)
    scenario["duration_s"] = max(scenario.get("duration_s", 0), math.ceil(hostile_end + 10))
    return scenario


# ---------------------------------------------------------------- scripted

@lru_cache(maxsize=None)
def _scripted_raw():
    items = {}
    for path in sorted(SCENARIO_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        items[data["id"]] = data
    return items


def list_scripted():
    out = []
    for data in sorted(_scripted_raw().values(), key=lambda d: d["order"]):
        env = data["environment"]
        out.append({
            "id": data["id"], "order": data["order"], "name": data["name"],
            "objective": data["objective"], "time_of_day": env["time_of_day"],
            "terrain": env["terrain"], "degradation": env.get("degradation", 0),
            "threat_summary": data.get("threat_summary", ""),
        })
    return out


# How far a scripted scenario may vary between runs, so trainees cannot learn it by rote.
# A scenario file can narrow these with a "vary" block; Urban Canyon sets rotate_deg to 0
# because its route is threaded between buildings that do not rotate with it.
VARY_DEFAULTS = {"rotate_deg": 30, "shift_s": [-4, 8], "jitter_s": 4}


def parse_vary(value):
    """A variant number from 1 to MAX_SEED, or None for the canonical scenario."""
    if value in (None, "", 0, "0"):
        return None
    if isinstance(value, bool):
        raise ValueError("vary must be an integer")
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError("vary must be an integer") from None
    if not 1 <= n <= MAX_SEED:
        raise ValueError(f"vary must be between 1 and {MAX_SEED}")
    return n


def _apply_variant(raw, vary):
    """Rotate every approach by one angle, shift the start, jitter each contact's spawn time and
    reseed the response rolls. Relative geometry (axes, swarm formations, the threat mix) is kept,
    so each scenario still teaches the same thing."""
    cfg = {**VARY_DEFAULTS, **raw.get("vary", {})}
    rng = random.Random(f"{raw['id']}:{vary}")
    turn = rng.uniform(-cfg["rotate_deg"], cfg["rotate_deg"])
    shift = rng.uniform(*cfg["shift_s"])
    for entry in raw["contacts"]:
        jitter = rng.uniform(-cfg["jitter_s"], cfg["jitter_s"])
        entry["spawn_t"] = round(max(2.0, entry["spawn_t"] + shift + jitter), 1)
        for w in entry["waypoints"]:
            w["brg"] = (w["brg"] + turn) % 360
    raw["seed"] = rng.randrange(1, MAX_SEED)
    raw["duration_s"] += max(0, math.ceil(shift + cfg["jitter_s"]))


def build_scripted(scenario_id, vary=None):
    raw = _scripted_raw().get(scenario_id)
    if raw is None:
        raise KeyError(scenario_id)
    raw = json.loads(json.dumps(raw))  # deep copy
    vary = parse_vary(vary)
    if vary is not None:
        _apply_variant(raw, vary)
    env_in = raw["environment"]
    env = environment_for(env_in["time_of_day"], env_in["terrain"], env_in["terrain_seed"],
                          env_in.get("degradation", 0),
                          {k: v for k, v in env_in.items()
                           if k not in ("time_of_day", "terrain", "terrain_seed", "degradation")})
    contacts = []
    for i, entry in enumerate(raw["contacts"]):
        # Hand-written files give waypoints as {"brg", "rng", "alt"}; convert to x, y, z.
        entry["waypoints"] = [_wp(w["brg"], w["rng"], w["alt"]) if isinstance(w, dict) else w
                              for w in entry["waypoints"]]
        if "swarm" in entry and "count" in entry:
            contacts.extend(expand_swarm(entry, raw["seed"] * 31 + i))
        else:
            contacts.append(entry)
    scenario = {
        "id": raw["id"], "name": raw["name"], "kind": "scripted", "seed": raw["seed"],
        "params": {"vary": vary} if vary is not None else None, "objective": raw["objective"], "duration_s": raw["duration_s"],
        "environment": env, "contacts": contacts,
    }
    return _finish(scenario)


# ---------------------------------------------------------------- procedural

def _hostile_path(rng, model, axis, speed_mult):
    bearing = axis + rng.uniform(-20, 20)
    if model == "fixed_wing":
        r0 = rng.uniform(2600, 3000)
        arc = rng.choice((-1, 1)) * rng.uniform(15, 35)
        wps = [_wp(bearing, r0, 230), _wp(bearing + arc, 1300, 200),
               _wp(bearing + arc / 3, 500, 140), _wp(bearing, rng.uniform(15, 50), 12)]
    else:
        r0 = rng.uniform(1800, 2600)
        alt = rng.uniform(60, 150) if model == "quadcopter" else rng.uniform(80, 140)
        wps = [_wp(bearing, r0, alt), _wp(bearing + rng.uniform(-15, 15), r0 * 0.5, alt * 0.9),
               _wp(bearing + rng.uniform(-10, 10), rng.uniform(20, 60), 25)]
    return wps, round(BASE_SPEED[model] * speed_mult, 1)


def generate(raw_params):
    """Build a procedural scenario. Deterministic for a given set of parameters."""
    p = normalise_params(raw_params)
    seed, difficulty = p["seed"], p["difficulty"]
    table = DIFFICULTY[difficulty]
    rng = random.Random(seed)

    # Always draw these so the random stream is the same whether or not they are overridden.
    drawn_tod = rng.choice(TIMES_OF_DAY)
    drawn_terrain = rng.choice(TERRAINS)
    terrain_seed = rng.randrange(1, MAX_SEED)
    drawn_swarm = rng.randint(max(0, table["swarm_max"] // 2), table["swarm_max"]) if table["swarm_max"] else 0

    resolved = {
        "seed": seed, "difficulty": difficulty,
        "time_of_day": p["time_of_day"] or drawn_tod,
        "terrain": p["terrain"] or drawn_terrain,
        "degradation": table["degradation"] if p["degradation"] is None else p["degradation"],
        "swarm": drawn_swarm if p["swarm"] is None else p["swarm"],
        "hostile": table["hostile"] if p["hostile"] is None else p["hostile"],
        "decoy": table["decoy"] if p["decoy"] is None else p["decoy"],
        "benign": table["benign"] if p["benign"] is None else p["benign"],
        "friendly": table["friendly"] if p["friendly"] is None else p["friendly"],
    }
    if resolved["hostile"] == 0 and resolved["swarm"] == 0:
        resolved["hostile"] = 1

    env = environment_for(resolved["time_of_day"], resolved["terrain"], terrain_seed, resolved["degradation"])
    speed_mult = table["speed"]
    duration = 150 + 30 * difficulty

    two_axes = (resolved["swarm"] >= 4 and difficulty >= 4) or rng.random() < 0.3
    axis0 = rng.uniform(0, 360)
    axes = [axis0, (axis0 + rng.uniform(70, 160)) % 360] if two_axes else [axis0]

    contacts = []
    order = 0
    for i in range(resolved["hostile"]):
        model = rng.choices(("quadcopter", "hexacopter", "fixed_wing"), weights=(5, 3, 2))[0]
        wps, speed = _hostile_path(rng, model, axes[i % len(axes)], speed_mult)
        spawn = rng.uniform(8, 20) if i == 0 else rng.uniform(10, duration * 0.55)
        order += 1
        contacts.append({"order": order, "model": model, "threat": "hostile", "spawn_t": round(spawn, 1),
                         "speed_mps": speed, "waypoints": wps, "wobble_seed": rng.randrange(1, MAX_SEED)})

    if resolved["swarm"]:
        sizes = [resolved["swarm"]] if len(axes) == 1 else [
            math.ceil(resolved["swarm"] / 2), resolved["swarm"] // 2]
        for g, size in enumerate(s for s in sizes if s):
            wps, speed = _hostile_path(rng, "quadcopter", axes[g % len(axes)], speed_mult)
            group = {"swarm": chr(ord("A") + g), "count": size, "model": "quadcopter",
                     "spawn_t": round(rng.uniform(20, duration * 0.4), 1), "speed_mps": speed,
                     "waypoints": wps, "spacing_m": 30}
            for m in expand_swarm(group, rng.randrange(1, MAX_SEED)):
                order += 1
                m["order"] = order
                contacts.append(m)

    for _ in range(resolved["decoy"]):
        b = rng.uniform(0, 360)
        wps = [_wp(b, rng.uniform(1400, 2000), rng.uniform(200, 450)),
               _wp(b + rng.uniform(-25, 25), rng.uniform(350, 650), rng.uniform(150, 350))]
        order += 1
        contacts.append({"order": order, "model": "balloon", "threat": "decoy",
                         "spawn_t": round(rng.uniform(0, duration * 0.5), 1),
                         "speed_mps": BASE_SPEED["balloon"], "waypoints": wps,
                         "wobble_seed": rng.randrange(1, MAX_SEED)})

    for _ in range(resolved["benign"]):
        b = rng.uniform(0, 360)
        wps = [_wp(b + rng.uniform(-40, 40), rng.uniform(450, 1400), rng.uniform(25, 90)) for _ in range(4)]
        order += 1
        contacts.append({"order": order, "model": "bird", "threat": "benign",
                         "spawn_t": round(rng.uniform(0, duration * 0.5), 1),
                         "speed_mps": round(rng.uniform(10, 14), 1), "waypoints": wps,
                         "wobble_seed": rng.randrange(1, MAX_SEED)})

    for _ in range(resolved["friendly"]):
        b = rng.uniform(0, 360)
        wps = [_wp(b, 3200, rng.uniform(500, 800)), _wp(b + 180 + rng.uniform(-35, 35), 3200, 650)]
        order += 1
        contacts.append({"order": order, "model": "friendly_aircraft", "threat": "friendly",
                         "spawn_t": round(rng.uniform(5, duration * 0.5), 1),
                         "speed_mps": BASE_SPEED["friendly_aircraft"], "waypoints": wps,
                         "wobble_seed": rng.randrange(1, MAX_SEED)})

    total_threats = resolved["hostile"] + resolved["swarm"]
    scenario = {
        "id": f"proc-{seed}-d{difficulty}",
        "name": f"Generated: {resolved['time_of_day']}, {resolved['terrain']}, difficulty {difficulty}",
        "kind": "procedural", "seed": seed, "params": resolved,
        "objective": (f"Mixed practice: {total_threats} hostile drone(s)"
                      f"{' including a swarm of ' + str(resolved['swarm']) if resolved['swarm'] else ''}, "
                      f"{resolved['decoy']} decoy(s), {resolved['benign']} bird(s), "
                      f"{resolved['friendly']} friendly aircraft. Sensor degradation level {resolved['degradation']}."),
        "duration_s": duration, "environment": env, "contacts": contacts,
    }
    return _finish(scenario)


def get_scenario(scenario_id=None, params=None):
    """Rebuild a scenario from what a client is allowed to send: a scripted id, or procedural params."""
    if scenario_id and str(scenario_id).lower() != "procedural" and not str(scenario_id).startswith("proc-"):
        vary = params.get("vary") if isinstance(params, dict) else None
        return build_scripted(scenario_id, vary)
    return generate(params or {})
