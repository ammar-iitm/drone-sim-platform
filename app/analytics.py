"""Trainee and unit analytics for the AAR dashboard (AVD "AAR dashboard")."""

import json

from .db import avg1

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
        if r["grade"] == "INCOMPLETE":
            continue
        for c in result["contacts"]:
            if not c["scored"]:
                continue
            chosen = c["classification"].get("chosen") or "NOT_CLASSIFIED"
            if c["true_class"] in matrix:
                matrix[c["true_class"]][chosen] += 1
            if c["detection"].get("t") is not None:
                detect_times.append(c["detection"]["t"] - c["spawn_t"])

    completed = [r for r in rows if r["grade"] != "INCOMPLETE"]
    incomplete = [r for r in rows if r["grade"] == "INCOMPLETE"]

    # Qualifying series matching the session list index, with None for incomplete attempts
    # to maintain temporal alignment for charts and table rows.
    series = {m: [(r[m] if r["grade"] != "INCOMPLETE" else None) for r in rows] for m in METRICS + ("total",)}

    # Rolling average of total score computed across qualifying completed sessions
    qual_totals = [r["total"] for r in completed]
    qual_rolling = _rolling(qual_totals, window=3)
    roll_iter = iter(qual_rolling)
    rolling = {
        "total": [(next(roll_iter) if r["grade"] != "INCOMPLETE" else None) for r in rows]
    }
    for m in METRICS:
        m_vals = [r[m] for r in completed]
        m_roll = _rolling(m_vals, window=3)
        m_iter = iter(m_roll)
        rolling[m] = [(next(m_iter) if r["grade"] != "INCOMPLETE" else None) for r in rows]

    averages = {m: _avg([r[m] for r in completed]) for m in METRICS + ("total",)}
    change = {
        m: (round([r[m] for r in completed][-1] - [r[m] for r in completed][0], 1) if len(completed) >= 2 else None)
        for m in METRICS + ("total",)
    }

    return {
        "trainee": dict(t),
        "sessions": rows,
        "attempts": len(rows),
        "completed": len(completed),
        "incomplete": len(incomplete),
        "series": series,
        "rolling": rolling,
        "averages": averages,
        "change": change,
        "mean_time_to_detect_s": _avg(detect_times),
        "false_alarms_per_session": _avg([r["false_alarms"] for r in completed]),
        "confusion": {"rows": classes, "columns": columns, "counts": matrix},
    }


def unit(db, unit_name):
    stage_avgs = ", ".join(
        f"{avg1(f'CASE WHEN s.grade != \'INCOMPLETE\' THEN s.{m} END')} AS {m}"
        for m in ("total",) + METRICS
    )
    trainees = [dict(r) for r in db.execute(
        f"SELECT t.id, t.callsign, "
        f"COUNT(s.id) AS attempts, "
        f"COUNT(s.id) AS sessions, "
        f"COUNT(CASE WHEN s.grade != 'INCOMPLETE' THEN 1 END) AS completed, "
        f"COUNT(CASE WHEN s.grade = 'INCOMPLETE' THEN 1 END) AS incomplete, "
        f"{stage_avgs}, "
        f"COALESCE(SUM(s.breaches), 0) AS breaches "
        f"FROM trainees t LEFT JOIN sessions s ON s.trainee_id = t.id WHERE t.unit = ? "
        f"GROUP BY t.id ORDER BY t.callsign", (unit_name,))]
    if not trainees:
        return None
    agg = db.execute(
        f"SELECT COUNT(*) AS attempts, "
        f"COUNT(*) AS sessions, "
        f"COUNT(CASE WHEN s.grade != 'INCOMPLETE' THEN 1 END) AS completed, "
        f"COUNT(CASE WHEN s.grade = 'INCOMPLETE' THEN 1 END) AS incomplete, "
        f"{stage_avgs}, "
        f"COALESCE(SUM(s.breaches), 0) AS breaches FROM sessions s JOIN trainees t ON t.id = s.trainee_id "
        f"WHERE t.unit = ?", (unit_name,)).fetchone()
    averages = {m: agg[m] for m in METRICS + ("total",)}

    weakest = None
    present = [m for m in METRICS if averages[m] is not None]
    if present:
        # Lowest unit average. On a tie the gap to the target is equal too, so the
        # fixed metric order (detection first) decides.
        weakest = min(present, key=lambda m: averages[m])

    # Only trainees with completed qualifying sessions are eligible for ranking
    trained = [t for t in trainees if t["completed"] and t["total"] is not None]
    recent = [dict(r) for r in db.execute(
        "SELECT s.id, t.callsign, s.scenario_name, s.started_at, s.total, s.grade, s.breaches, s.false_alarms "
        "FROM sessions s JOIN trainees t ON t.id = s.trainee_id WHERE t.unit = ? "
        "ORDER BY s.started_at DESC, s.id DESC LIMIT 10", (unit_name,))]
    return {
        "unit": unit_name,
        "attempts": agg["attempts"],
        "sessions": agg["sessions"],
        "completed": agg["completed"],
        "incomplete": agg["incomplete"],
        "breaches": agg["breaches"],
        "averages": averages,
        "target": TARGET,
        "weakest_skill": weakest,
        "weakest_trainees": sorted(trained, key=lambda t: t["total"])[:3],
        "trainees": trainees,
        "recent": recent,
    }
