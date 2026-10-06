"""Builders for hand-made scenarios and event logs used by the scoring tests."""


def contact(cid, model="quadcopter", threat="hostile", spawn=0.0, speed=20.0, start=2000.0, end=40.0,
            alt=100.0, par=20.0, **extra):
    """A contact flying straight in from the north towards the post."""
    true = {"quadcopter": "RECON_UAS", "hexacopter": "ARMED_UAS", "fixed_wing": "ARMED_UAS",
            "balloon": "DECOY", "bird": "BIRD", "friendly_aircraft": "FRIENDLY"}[model]
    c = {"id": cid, "model": model, "true_class": true, "threat": threat, "spawn_t": spawn,
         "speed_mps": speed, "waypoints": [[0, alt, -start], [0, alt, -end]], "par_detect_s": par,
         "swarm": None, "wobble_seed": 1}
    c.update(extra)
    return c


def scenario(*contacts, duration=200, seed=7):
    return {"id": "test", "name": "Test", "kind": "scripted", "seed": seed, "params": None, "objective": "",
            "duration_s": duration,
            "environment": {"time_of_day": "day", "terrain": "rural", "terrain_seed": 1, "degradation": 0,
                            "noise": 0, "fog": 0, "visual_range_m": 3000, "radar_dropout": 0},
            "contacts": list(contacts)}


def ev(t, etype, cid=None, **data):
    return {"t": t, "type": etype, "contact_id": cid, "data": data}
