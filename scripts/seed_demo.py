"""Seed a demo cohort so the dashboard shows real trends.

Every session goes through POST /api/sessions, so all scores come from the real
scoring engine. Trainees improve over their sessions at different rates.

    python scripts/seed_demo.py            # adds the cohort to data/trainer.db
    python scripts/seed_demo.py --reset    # deletes data/trainer.db first
"""

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import ROOT, create_app, geometry, scenario as scen  # noqa: E402
from app.scoring import load_rubric  # noqa: E402

COHORT = {
    "4 GUARDS": [("VIPER-3", 0.35, 0.12), ("HAWK-1", 0.55, 0.08), ("RAVEN-7", 0.25, 0.15), ("ATLAS-2", 0.6, 0.04)],
    "21 SIKH": [("KESTREL-4", 0.45, 0.1), ("ORION-9", 0.3, 0.13)],
}
PLAN = ["s1-dawn-recon", "s4-mixed-traffic", "s2-night-loiter", "s5-fog-noise", "s3-urban-canyon", "s6-saturation-swarm"]
WRONG = {"RECON_UAS": ["ARMED_UAS", "BIRD"], "ARMED_UAS": ["RECON_UAS", "FRIENDLY"], "DECOY": ["RECON_UAS"],
         "BIRD": ["RECON_UAS"], "FRIENDLY": ["ARMED_UAS"]}


def synth_events(s, skill, rnd, rubric):
    """A plausible trainee: better skill means faster marks, better calls and better responses."""
    events = []
    for c in s["contacts"]:
        hostile = c["threat"] == "hostile"
        if rnd.random() > (0.55 + 0.45 * skill if hostile else 0.35):
            continue
        t_mark = c["spawn_t"] + c["par_detect_s"] * rnd.uniform(0.3, 2.6 - 1.8 * skill)
        if t_mark >= geometry.end_time(c) - 2:
            continue
        events.append({"t": round(t_mark, 2), "type": "mark", "contact_id": c["id"], "data": {"via": "view"}})
        chosen = c["true_class"] if rnd.random() < 0.45 + 0.5 * skill else rnd.choice(WRONG[c["true_class"]])
        events.append({"t": round(t_mark + rnd.uniform(1, 4), 2), "type": "classify", "contact_id": c["id"],
                       "data": {"class": chosen}})
        if hostile:
            expected = c.get("expected_responses") or rubric["expected_responses"][c["model"]]
            resp = rnd.choice(expected) if rnd.random() < 0.4 + 0.55 * skill else rnd.choice(["JAM", "TAKE_COVER", "REPORT"])
            t_close = geometry.first_time_within(c, rnd.uniform(700, 1400)) or t_mark + 5
            t_resp = max(t_mark + 3, t_close) + rnd.uniform(0, 12 * (1 - skill))
            if t_resp < geometry.end_time(c) - 1:
                events.append({"t": round(t_resp, 2), "type": "respond", "contact_id": c["id"], "data": {"response": resp}})
        elif rnd.random() < 0.25 * (1 - skill):
            events.append({"t": round(t_mark + 5, 2), "type": "respond", "contact_id": c["id"], "data": {"response": "JAM"}})
    for _ in range(rnd.choice([0, 0, 1, 2]) if skill < 0.7 else 0):
        events.append({"t": round(rnd.uniform(5, s["duration_s"] - 5), 2), "type": "mark", "contact_id": None, "data": {}})
    return sorted(events, key=lambda e: e["t"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--sessions", type=int, default=5)
    args = parser.parse_args()
    db_path = ROOT / "data" / "trainer.db"
    if args.reset:
        for suffix in ("", "-wal", "-shm"):
            Path(str(db_path) + suffix).unlink(missing_ok=True)
    app = create_app()
    client = app.test_client()
    rubric = load_rubric(ROOT / "rubric.json")
    rnd = random.Random(2026)
    count = 0
    for unit, people in COHORT.items():
        for callsign, start_skill, gain in people:
            for n in range(args.sessions):
                skill = min(0.97, start_skill + gain * n + rnd.uniform(-0.05, 0.05))
                sid = PLAN[(n + len(callsign)) % len(PLAN)]
                s = scen.build_scripted(sid)
                body = {"callsign": callsign, "unit": unit, "scenario_id": sid, "events": synth_events(s, skill, rnd, rubric)}
                res = client.post("/api/sessions", json=body)
                assert res.status_code == 201, res.get_json()
                count += 1
    print(f"Seeded {count} sessions for {sum(len(p) for p in COHORT.values())} trainees in {len(COHORT)} units into {db_path}")


if __name__ == "__main__":
    main()
