"""Scoring engine: a pure function of (scenario, event log, rubric).

Every contact goes down three stages (detection, classification, engagement) and each
stage records the decision-tree node it reached, the points earned and a plain reason.
The browser never sends a score; the server recomputes everything, including the
response success rolls, from the scenario seed.
"""

import hashlib
import json
import math
from pathlib import Path

from . import geometry, rng

EVENT_TYPES = {"mark", "classify", "respond", "sensor", "breach"}
SENSOR_MODES = {"eo", "nv", "thermal", "radar"}
MAX_EVENTS = 5000


def rubric_hash(path):
    try:
        content = Path(path).read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]
    except Exception:
        return "unknown"


def load_rubric(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["_hash"] = rubric_hash(path)
    return data


# ---------------------------------------------------------------- validation

def validate_events(raw_events, scenario, rubric, ended_t=None):
    """Check a submitted event log and return it normalised and sorted by time.
    Enforces per-contact chronology: contact must have spawned, and must have been
    validly marked before or at classification/response. Events must occur within
    the contact active lifetime and prior to session end.
    Raises ValueError with a message that names the first bad event."""
    if not isinstance(raw_events, list):
        raise ValueError("events must be a list")
    if len(raw_events) > MAX_EVENTS:
        raise ValueError(f"too many events (max {MAX_EVENTS})")

    mark_tol = float(rubric.get("geometry", {}).get("mark_tolerance_s", 1.0))
    session_end_tol = float(rubric.get("geometry", {}).get("session_end_tolerance_s", 0.5))
    session_end = scenario["duration_s"] if ended_t is None else min(float(ended_t), scenario["duration_s"])
    max_t = session_end + session_end_tol
    contacts_map = {c["id"]: c for c in scenario["contacts"]}
    contact_ids = set(contacts_map.keys())

    out = []
    for i, ev in enumerate(raw_events):
        if not isinstance(ev, dict):
            raise ValueError(f"event {i} is not an object")
        t = ev.get("t")
        if not isinstance(t, (int, float)) or isinstance(t, bool) or not math.isfinite(t) or not 0 <= t <= max_t:
            raise ValueError(f"event {i}: t must be a number between 0 and {round(max_t, 2)}")
        etype = ev.get("type")
        if etype not in EVENT_TYPES:
            raise ValueError(f"event {i}: unknown type {etype!r}")
        cid = ev.get("contact_id") or None
        if cid is not None and (not isinstance(cid, str) or len(cid) > 32):
            raise ValueError(f"event {i}: contact_id must be a short string")
        data = ev.get("data") or {}
        if not isinstance(data, dict) or len(json.dumps(data)) > 500:
            raise ValueError(f"event {i}: data must be a small object")
        if etype in ("classify", "respond", "breach"):
            if not cid or cid not in contact_ids:
                raise ValueError(f"event {i}: {etype} needs a contact_id from this scenario")
        if etype == "classify" and data.get("class") not in rubric["classes"]:
            raise ValueError(f"event {i}: class must be one of {', '.join(rubric['classes'])}")
        if etype == "respond" and data.get("response") not in rubric["responses"]:
            raise ValueError(f"event {i}: response must be one of {', '.join(rubric['responses'])}")
        if etype == "sensor" and data.get("mode") not in SENSOR_MODES:
            raise ValueError(f"event {i}: sensor mode must be one of {', '.join(sorted(SENSOR_MODES))}")
        out.append({"t": round(float(t), 3), "type": etype, "contact_id": cid, "data": data, "seq": i})

    # Sort chronologically by time and submission sequence (deterministic tie-breaking)
    out.sort(key=lambda e: (e["t"], e["seq"]))

    # Chronological state machine validation
    marked_contacts = set()
    for ev in out:
        cid = ev["contact_id"]
        t = ev["t"]
        etype = ev["type"]
        if etype == "mark":
            if cid in contacts_map:
                c = contacts_map[cid]
                if c["spawn_t"] - mark_tol <= t <= geometry.end_time(c) + mark_tol:
                    marked_contacts.add(cid)
        elif etype in ("classify", "respond"):
            c = contacts_map[cid]
            end_t = geometry.end_time(c)
            if t < c["spawn_t"] - mark_tol:
                raise ValueError(f"event {ev['seq']}: {etype} for {cid} occurred before spawn ({t} < {c['spawn_t']})")
            if cid not in marked_contacts:
                raise ValueError(f"event {ev['seq']}: {etype} for {cid} occurred before contact was marked")
            if t > end_t + mark_tol:
                raise ValueError(f"event {ev['seq']}: {etype} for {cid} occurred after contact left area ({t} > {round(end_t, 2)})")

    return out


# ---------------------------------------------------------------- helpers

def stays_out_of_reach(rubric, contact, t, responses, step=0.5):
    """The farthest any of these responses can reach (max_range_m), if the contact never comes
    within it from time t to the end of its path; otherwise None."""
    reach = max((rubric["responses"][x].get("max_range_m", 0) for x in responses), default=0)
    if not reach:
        return None
    end, s = geometry.end_time(contact), t
    while s <= end:
        r = geometry.range_at(contact, s)
        if r is not None and r <= reach:
            return None
        s += step
    return reach


def effectiveness(rubric, response, contact, t):
    spec = rubric["responses"][response]
    if not spec.get("engages"):
        return 0.0
    base = spec["effectiveness"].get(contact["model"], 0.0)
    r = geometry.range_at(contact, t)
    if r is None:
        return 0.0
    if r > spec.get("max_range_m", math.inf):
        base *= spec.get("out_of_range_factor", 0.0)
    if spec.get("fast_speed_mps") and contact["speed_mps"] > spec["fast_speed_mps"]:
        base *= spec.get("fast_factor", 1.0)
    return round(base, 4)


def _family(rubric, cls):
    return rubric["classes"][cls]["family"]


def _label(rubric, cls):
    return rubric["classes"][cls]["label"]


def _grade(rubric, total):
    for band in rubric["grade_bands"]:
        if total >= band["min"]:
            return band
    return rubric["grade_bands"][-1]


def _fmt(t):
    return f"{t:.1f} s"


# ---------------------------------------------------------------- scoring

def score_session(scenario, events, rubric, ended_t=None):
    """Score a validated event log. Returns a JSON-serialisable result."""
    geo = rubric["geometry"]
    tol = geo["mark_tolerance_s"]
    contacts = {c["id"]: c for c in scenario["contacts"]}
    session_end = scenario["duration_s"] if ended_t is None else min(ended_t, scenario["duration_s"])
    seed = scenario["seed"]

    by_contact = {cid: {"marks": [], "classes": [], "responses": []} for cid in contacts}
    false_alarm_events = []
    for ev in events:
        cid = ev["contact_id"]
        if ev["type"] == "mark":
            c = contacts.get(cid)
            if c and c["spawn_t"] - tol <= ev["t"] <= geometry.end_time(c) + tol:
                by_contact[cid]["marks"].append(ev)
            else:
                false_alarm_events.append(ev)
        elif ev["type"] == "classify":
            by_contact[cid]["classes"].append(ev)
        elif ev["type"] == "respond":
            by_contact[cid]["responses"].append(ev)

    results = []
    critical_events = []
    breaches = 0
    annotations = {}  # event seq -> list of stage notes for the timeline

    for cid, c in contacts.items():
        log = by_contact[cid]
        end_t = geometry.end_time(c)
        hostile = c["threat"] == "hostile"

        # Responses: work out rolls and when (if ever) the contact was neutralised.
        attempts = []
        neutralised_t = None
        for ev in log["responses"]:
            resp = ev["data"]["response"]
            if not rubric["responses"][resp].get("engages"):
                continue
            if neutralised_t is not None or not (c["spawn_t"] - tol <= ev["t"] <= end_t + tol):
                continue
            k = len(attempts)
            eff = effectiveness(rubric, resp, c, ev["t"])
            value = rng.roll(seed, cid, k)
            success = value < eff
            attempts.append({"t": ev["t"], "response": resp, "attempt": k, "effectiveness": eff,
                             "roll": round(value, 4), "success": success, "seq": ev["seq"]})
            if success:
                neutralised_t = ev["t"]

        breached = (hostile and neutralised_t is None and end_t <= session_end
                    and geometry.ends_inside(c, geo["inner_ring_m"]))
        if breached:
            breaches += 1

        marked = bool(log["marks"])
        scored = hostile or marked
        inbound_unresolved = (hostile and neutralised_t is None and end_t > session_end
                              and geometry.ends_inside(c, geo["inner_ring_m"]))
        entry = {"id": cid, "model": c["model"], "true_class": c["true_class"], "threat": c["threat"],
                 "spawn_t": c["spawn_t"], "par_detect_s": c["par_detect_s"], "scored": scored,
                 "breached": breached, "breach_t": round(end_t, 1) if breached else None,
                 "inbound_unresolved": inbound_unresolved,
                 "neutralised_t": neutralised_t, "attempts": attempts, "critical": []}

        if not scored:
            entry["path"] = ["not scored: non-hostile contact was never marked"]
            results.append(entry)
            continue

        # ---- detection
        if marked:
            first = log["marks"][0]
            dt = max(0.0, first["t"] - c["spawn_t"])
            ratio = dt / c["par_detect_s"]
            tier = next(tr for tr in rubric["detection_tiers"]
                        if tr["max_par_ratio"] is None or ratio <= tr["max_par_ratio"])
            det = {"points": tier["score"], "node": tier["node"], "t": first["t"],
                   "reason": f"Marked {_fmt(dt)} after it appeared; par is {_fmt(c['par_detect_s'])} "
                             f"({ratio:.2f}x par) so it earns {round(tier['score'] * 100)}%."}
            annotations.setdefault(first["seq"], []).append(("detection", det))
        else:
            how = "breached the inner ring" if breached else (
                "left the area" if end_t <= session_end else "was still inbound when the session ended")
            det = {"points": 0.0, "node": "missed", "t": None,
                   "reason": f"Hostile contact was never marked before it {how}."}
        entry["detection"] = det

        # ---- classification
        if not marked:
            cls = {"points": 0.0, "node": "not_marked", "chosen": None,
                   "reason": "Not classified because it was never marked."}
        elif not log["classes"]:
            cls = {"points": 0.0, "node": "not_classified", "chosen": None,
                   "reason": "Marked but never classified."}
        else:
            last = log["classes"][-1]
            chosen = last["data"]["class"]
            true_fam, chosen_fam = _family(rubric, c["true_class"]), _family(rubric, chosen)
            if chosen == c["true_class"]:
                node, pts = "exact", rubric["classification_scores"]["exact"]
                reason = f"Classified as {_label(rubric, chosen)}, which is correct."
            elif chosen_fam == true_fam:
                node, pts = "same_family", rubric["classification_scores"]["same_family"]
                reason = (f"Classified as {_label(rubric, chosen)}; it was a {_label(rubric, c['true_class'])}. "
                          f"Right family, wrong type.")
            else:
                node, pts = "wrong_family", rubric["classification_scores"]["wrong_family"]
                reason = (f"Classified as {_label(rubric, chosen)}; it was a {_label(rubric, c['true_class'])}. "
                          f"Wrong family.")
                if chosen_fam in rubric["critical_misclassification"].get(true_fam, []):
                    node = "critical_misclassification"
                    reason += " Calling a hostile drone harmless or friendly is a critical error."
                    entry["critical"].append("hostile_called_" + chosen_fam)
                    critical_events.append({"contact_id": cid, "kind": "hostile_called_" + chosen_fam,
                                            "t": last["t"]})
            cls = {"points": pts, "node": node, "chosen": chosen, "t": last["t"], "reason": reason}
            annotations.setdefault(last["seq"], []).append(("classification", cls))
        entry["classification"] = cls

        # ---- engagement
        engaging = [ev for ev in log["responses"] if rubric["responses"][ev["data"]["response"]].get("engages")]
        sc = rubric["engagement_scores"]
        if hostile:
            others = [ev for ev in log["responses"] if ev["data"]["response"] != "TRACK"]
            decision = engaging[0] if engaging else (others[0] if others else None)
            expected = c.get("expected_responses") or rubric["expected_responses"].get(c["model"], [])
            # Decision quality first: a suitable, timely engaging response is credited even if the
            # roll fails and the contact then breaches (the breach penalty still applies to the total).
            resp = decision["data"]["response"] if decision else None
            r = geometry.range_at(c, decision["t"]) if decision else None
            suitable = resp in expected
            engages = bool(resp) and rubric["responses"][resp].get("engages")
            label = rubric["responses"][resp]["label"] if resp else ""
            att = next((a for a in attempts if decision and a["seq"] == decision["seq"]), None)
            chance = round(att["effectiveness"] * 100) if att else 0

            def in_time(dist):
                return dist is not None and dist >= geo["late_range_m"]
            timely = in_time(r)

            if suitable and timely and engages:
                # A failed first try followed by a suitable retry that stops the drone in time
                # earns full credit, so persisting scores better than giving up (issue #15).
                retry = None if att and att["success"] else next(
                    (a for a in attempts if a["success"] and a["response"] in expected
                     and in_time(geometry.range_at(c, a["t"]))), None)
                if att and att["success"]:
                    eng = {"points": sc["correct_effective"], "node": "correct_effective",
                           "reason": f"{label} at {round(r)} m was suitable and timely, and it worked "
                                     f"(chance {chance}%)."}
                elif retry:
                    retry_label = rubric["responses"][retry["response"]]["label"]
                    eng = {"points": sc["correct_effective"], "node": "correct_effective",
                           "reason": f"{label} at {round(r)} m was suitable and timely but did not work "
                                     f"(chance {chance}%); attempt {retry['attempt'] + 1}, "
                                     f"{retry_label} at {round(geometry.range_at(c, retry['t']))} m, stopped it in time."}
                else:
                    eng = {"points": sc["correct_failed_roll"], "node": "correct_failed_roll",
                           "reason": f"{label} at {round(r)} m was the right decision but did not work this time "
                                     f"(chance {chance}%). The decision is credited, not the luck."}
            elif suitable and timely and not breached:
                eng = {"points": sc["correct_effective"], "node": "correct_effective",
                       "reason": f"{label} at {round(r)} m was the expected response."}
            elif (not engaging and resp in rubric.get("passive_responses", [])
                  and (reach := stays_out_of_reach(rubric, c, decision["t"], expected))):
                # ATP 3-01.81: when the threat is outside the range of the unit's weapons, the best
                # option can be to disperse and seek cover (issue #14, R8).
                eng = {"points": sc["correct_effective"], "node": "correct_passive",
                       "reason": f"{label} at {round(r)} m was right: it never came within {reach} m, "
                                 f"the reach of the suitable responses, so cover was the best option."}
            elif breached:
                eng = {"points": sc["none_or_breach"], "node": "breach",
                       "reason": f"Reached the inner ring at {_fmt(end_t)} without being stopped."}
            elif decision is None:
                eng = {"points": sc["none_or_breach"], "node": "no_response",
                       "reason": "No response was chosen for this hostile contact."}
            elif not suitable:
                names = ", ".join(rubric["responses"][x]["label"] for x in expected) or "none"
                eng = {"points": sc["late_or_unsuitable"], "node": "unsuitable",
                       "reason": f"{label} is not suitable against a {c['model'].replace('_', ' ')}; "
                                 f"suitable responses: {names}."}
            else:
                where = "after it had left" if r is None else f"at {round(r)} m"
                eng = {"points": sc["late_or_unsuitable"], "node": "late",
                       "reason": f"{label} was the right choice but came late, {where} "
                                 f"(inside {geo['late_range_m']} m)."}
            if decision is not None:
                eng["t"] = decision["t"]
                annotations.setdefault(decision["seq"], []).append(("engagement", eng))
        else:
            if engaging:
                ev = engaging[0]
                label = rubric["responses"][ev["data"]["response"]]["label"]
                if c["threat"] == "friendly":
                    eng = {"points": sc["unnecessary_engagement"], "node": "friendly_engaged",
                           "reason": f"{label} used against a friendly aircraft. Critical error."}
                    entry["critical"].append("friendly_engaged")
                    critical_events.append({"contact_id": cid, "kind": "friendly_engaged", "t": ev["t"]})
                else:
                    eng = {"points": sc["unnecessary_engagement"], "node": "unnecessary_engagement",
                           "reason": f"{label} used against a {_label(rubric, c['true_class']).lower()}, "
                                     f"which is not a threat."}
                eng["t"] = ev["t"]
                annotations.setdefault(ev["seq"], []).append(("engagement", eng))
            else:
                eng = {"points": sc["restraint"], "node": "restraint",
                       "reason": "Correctly held fire on a contact that was not a threat."}
        entry["engagement"] = eng

        entry["path"] = [f"detection/{det['node']}", f"classification/{cls['node']}", f"engagement/{eng['node']}"]
        results.append(entry)

    # ---- totals
    scored = [r for r in results if r["scored"]]
    stages = {}
    for stage in ("detection", "classification", "engagement"):
        vals = [r[stage]["points"] for r in scored]
        stages[stage] = round(100 * sum(vals) / len(vals), 1) if vals else 0.0

    weights = rubric["weights"]
    wsum = sum(weights.values()) or 1
    weighted = sum(weights[s] * stages[s] for s in stages) / wsum

    pen = rubric["penalties"]
    fa_points = min(pen["false_alarm_cap"], pen["false_alarm"] * len(false_alarm_events))
    breach_points = pen["breach"] * breaches
    unresolved_count = sum(1 for r in results if r.get("inbound_unresolved"))
    unresolved_points = pen["breach"] * unresolved_count
    critical_points = pen["critical"] * len(critical_events)
    total = round(min(100.0, max(0.0, weighted - fa_points - breach_points - unresolved_points - critical_points)), 1)

    is_interrupted = (ended_t is not None and ended_t < scenario["duration_s"] - 1.0)
    session_status = "interrupted" if is_interrupted else "completed"
    if is_interrupted:
        band = {"min": 0, "grade": "INCOMPLETE", "label": "Session interrupted — assessment incomplete"}
    else:
        band = _grade(rubric, total)

    # ---- timeline: every event in order, with the stage outcomes it produced
    timeline = []
    for ev in events:
        item = {"t": ev["t"], "type": ev["type"], "contact_id": ev["contact_id"], "data": ev["data"], "notes": []}
        for stage, outcome in annotations.get(ev["seq"], []):
            item["notes"].append({"stage": stage, "node": outcome["node"],
                                  "points": round(outcome["points"] * 100), "reason": outcome["reason"]})
        if ev in false_alarm_events:
            item["notes"].append({"stage": "penalty", "node": "false_alarm", "points": -pen["false_alarm"],
                                  "reason": "Marked empty sky or a contact that was not there."})
        timeline.append(item)
    for r in results:
        if r["breached"]:
            timeline.append({"t": r["breach_t"], "type": "breach", "contact_id": r["id"], "data": {},
                             "notes": [{"stage": "penalty", "node": "breach", "points": -pen["breach"],
                                        "reason": "Hostile contact reached the inner ring."}]})
        elif r.get("inbound_unresolved"):
            timeline.append({"t": session_end, "type": "unresolved_threat", "contact_id": r["id"], "data": {},
                             "notes": [{"stage": "penalty", "node": "inbound_unresolved", "points": -pen["breach"],
                                        "reason": "Hostile contact was inbound toward inner ring when session ended prematurely."}]})
        if r["neutralised_t"] is not None:
            timeline.append({"t": r["neutralised_t"], "type": "neutralised", "contact_id": r["id"],
                             "data": {}, "notes": []})
    timeline.sort(key=lambda x: x["t"])

    return {
        "app_version": "1.0.0",
        "rubric_version": rubric.get("version"),
        "rubric_hash": rubric.get("_hash", "unknown"),
        "scenario": {"id": scenario["id"], "name": scenario["name"], "seed": seed,
                     "kind": scenario["kind"], "params": scenario.get("params")},
        "ended_t": session_end,
        "session_status": session_status,
        "stages": stages,
        "weights": weights,
        "weighted": round(weighted, 1),
        "penalties": {
            "false_alarms": len(false_alarm_events), "false_alarm_points": fa_points,
            "breaches": breaches, "breach_points": breach_points,
            "inbound_unresolved": unresolved_count, "inbound_unresolved_points": unresolved_points,
            "critical_errors": len(critical_events), "critical_points": critical_points,
            "critical_detail": critical_events,
        },
        "total": total,
        "grade": band["grade"],
        "grade_label": band["label"],
        "contacts": results,
        "timeline": timeline,
    }
