"""Trainee and unit analytics for the AAR dashboard (AVD "AAR dashboard")."""

import json

METRICS = ("detection", "classification", "engagement")
TARGET = 80


def _rolling(values, window=3):
    out = []
    for i in range(len(values)):
        chunk = values[max(0, i - window + 1): i + 1]
        out.append(round(sum(chunk) / len(chunk), 1))
    return out


def _avg(values):
    return round(sum(values) / len(values), 1) if values else None


def trainee(db, trainee_id, rubric):
    t = db.execute("SELECT * FROM trainees WHERE id = ?", (trainee_id,)).fetchone()
    if t is None:
        return None
    rows = [dict(r) for r in db.execute(
        "SELECT id, scenario_name, started_at, total, detection, classification, engagement, grade, "
        "false_alarms, breaches, critical_errors, result FROM sessions WHERE trainee_id = ? "
        "ORDER BY started_at, id", (trainee_id,))]

    classes = list(rubric["classes"])
    columns = classes + ["NOT_CLASSIFIED"]
    matrix = {c: {k: 0 for k in columns} for c in classes}
    detect_times = []
    for r in rows:
        result = json.loads(r.pop("result"))
        for c in result["contacts"]:
            if not c["scored"]:
                continue
            chosen = c["classification"].get("chosen") or "NOT_CLASSIFIED"
            if c["true_class"] in matrix:
                matrix[c["true_class"]][chosen] += 1
            if c["detection"].get("t") is not None:
                detect_times.append(c["detection"]["t"] - c["spawn_t"])

    series = {m: [r[m] for r in rows] for m in METRICS + ("total",)}
    return {
        "trainee": dict(t),
        "sessions": rows,
        "series": series,
        "rolling": {m: _rolling(v) for m, v in series.items()},
        "averages": {m: _avg(v) for m, v in series.items()},
        "change": {m: (round(v[-1] - v[0], 1) if len(v) >= 2 else None) for m, v in series.items()},
        "mean_time_to_detect_s": _avg(detect_times),
        "false_alarms_per_session": _avg([r["false_alarms"] for r in rows]),
        "confusion": {"rows": classes, "columns": columns, "counts": matrix},
    }


def unit(db, unit_name):
    trainees = [dict(r) for r in db.execute(
        "SELECT t.id, t.callsign, COUNT(s.id) AS sessions, ROUND(AVG(s.total), 1) AS total, "
        "ROUND(AVG(s.detection), 1) AS detection, ROUND(AVG(s.classification), 1) AS classification, "
        "ROUND(AVG(s.engagement), 1) AS engagement, SUM(s.breaches) AS breaches "
        "FROM trainees t LEFT JOIN sessions s ON s.trainee_id = t.id WHERE t.unit = ? "
        "GROUP BY t.id ORDER BY t.callsign", (unit_name,))]
    if not trainees:
        return None
    agg = db.execute(
        "SELECT COUNT(*) AS sessions, ROUND(AVG(total), 1) AS total, ROUND(AVG(detection), 1) AS detection, "
        "ROUND(AVG(classification), 1) AS classification, ROUND(AVG(engagement), 1) AS engagement, "
        "COALESCE(SUM(breaches), 0) AS breaches FROM sessions s JOIN trainees t ON t.id = s.trainee_id "
        "WHERE t.unit = ?", (unit_name,)).fetchone()
    averages = {m: agg[m] for m in METRICS + ("total",)}

    weakest = None
    present = [m for m in METRICS if averages[m] is not None]
    if present:
        # Lowest unit average. On a tie the gap to the target is equal too, so the
        # fixed metric order (detection first) decides.
        weakest = min(present, key=lambda m: averages[m])

    trained = [t for t in trainees if t["sessions"]]
    recent = [dict(r) for r in db.execute(
        "SELECT s.id, t.callsign, s.scenario_name, s.started_at, s.total, s.grade, s.breaches, s.false_alarms "
        "FROM sessions s JOIN trainees t ON t.id = s.trainee_id WHERE t.unit = ? "
        "ORDER BY s.started_at DESC, s.id DESC LIMIT 10", (unit_name,))]
    return {
        "unit": unit_name,
        "sessions": agg["sessions"],
        "breaches": agg["breaches"],
        "averages": averages,
        "target": TARGET,
        "weakest_skill": weakest,
        "weakest_trainees": sorted(trained, key=lambda t: t["total"])[:3],
        "trainees": trainees,
        "recent": recent,
    }
