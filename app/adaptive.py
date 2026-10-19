"""Adaptive Training Intelligence engine (SIH PS 26247, Phase 3).

Analyzes trainee assessment history, derives explainable multi-dimensional skill profiles,
diagnoses learning gaps (detection latency, classification confusion, false alarms,
perimeter breaches, and environmental degradation sensitivity), and deterministically
recommends targeted training scenarios and difficulty progressions.
"""

import json
import math
from datetime import datetime, timezone

from . import scenario as scen

POLICY_VERSION = "1.0.0"
TARGET_SCORE = 80.0

SCRIPTED_NAMES = {
    "s1-dawn-recon": "Dawn Recon Pass",
    "s2-night-loiter": "Night Loitering Drone",
    "s3-urban-canyon": "Urban Canyon",
    "s4-mixed-traffic": "Mixed Traffic",
    "s5-fog-noise": "Fog and Noise",
    "s6-saturation-swarm": "Saturation Swarm",
}


def _avg(values):
    return round(sum(values) / len(values), 1) if values else None


def _safe_float(val, min_val=0.0, max_val=100.0, default=None):
    if val is None or isinstance(val, (bool, str, bytes, list, dict, set, tuple)):
        return default
    if not isinstance(val, (int, float)):
        try:
            from decimal import Decimal
            if not isinstance(val, Decimal):
                return default
        except (ImportError, Exception):
            return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        if min_val is not None and f < min_val:
            return default
        if max_val is not None and f > max_val:
            return default
        return f
    except (ValueError, TypeError, OverflowError):
        return default


def _safe_int(val, min_val=0, max_val=100000, default=0):
    if val is None or isinstance(val, (bool, str, bytes, list, dict, set, tuple)):
        return default
    if not isinstance(val, int):
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val) or not val.is_integer():
                return default
        else:
            try:
                from decimal import Decimal
                if isinstance(val, Decimal):
                    if val != val.to_integral_value():
                        return default
                else:
                    return default
            except (ImportError, Exception):
                return default
    try:
        i = int(val)
        if min_val is not None and i < min_val:
            return default
        if max_val is not None and i > max_val:
            return default
        return i
    except (ValueError, TypeError, OverflowError):
        return default


def _get_adaptive_config(rubric):
    """Extract and validate adaptive configuration from rubric JSON with default fallbacks.

    Validates numeric types, finiteness, ranges, and consistency among thresholds.
    Raises ValueError on contradictory, non-numeric, or out-of-range configurations.
    """
    raw_cfg = (rubric.get("adaptive") if isinstance(rubric, dict) else {}) or {}
    if not isinstance(raw_cfg, dict):
        raise ValueError("Adaptive configuration must be a dictionary")

    def _val_float(key, default, min_val=0.0, max_val=100.0):
        if key not in raw_cfg or raw_cfg[key] is None:
            return float(default)
        val = raw_cfg[key]
        if isinstance(val, bool):
            raise ValueError(f"Invalid boolean value for adaptive config {key!r}")
        try:
            f = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Non-numeric value for adaptive config {key!r}: {val!r}")
        if math.isnan(f) or math.isinf(f):
            raise ValueError(f"Invalid NaN or infinite value for adaptive config {key!r}")
        if min_val is not None and f < min_val:
            raise ValueError(f"Value for {key!r} ({f}) below minimum allowed ({min_val})")
        if max_val is not None and f > max_val:
            raise ValueError(f"Value for {key!r} ({f}) exceeds maximum allowed ({max_val})")
        return f

    def _val_int(key, default, min_val=0, max_val=1000):
        if key not in raw_cfg or raw_cfg[key] is None:
            return int(default)
        val = raw_cfg[key]
        if isinstance(val, bool):
            raise ValueError(f"Invalid boolean value for adaptive config {key!r}")
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Invalid NaN or infinite value for adaptive config {key!r}")
            if not val.is_integer():
                raise ValueError(f"Fractional number not allowed for integer config {key!r}: {val!r}")
            i = int(val)
        elif isinstance(val, int):
            i = val
        elif isinstance(val, str):
            val_str = val.strip()
            if "." in val_str or "e" in val_str.lower():
                try:
                    f = float(val_str)
                    if math.isnan(f) or math.isinf(f) or not f.is_integer():
                        raise ValueError(f"Non-integer value for adaptive config {key!r}: {val!r}")
                    i = int(f)
                except ValueError:
                    raise ValueError(f"Non-integer value for adaptive config {key!r}: {val!r}")
            elif val_str.startswith("-") and val_str[1:].isdigit():
                i = int(val_str)
            elif val_str.isdigit():
                i = int(val_str)
            else:
                raise ValueError(f"Non-integer value for adaptive config {key!r}: {val!r}")
        else:
            raise ValueError(f"Non-integer value for adaptive config {key!r}: {val!r}")

        if min_val is not None and i < min_val:
            raise ValueError(f"Value for {key!r} ({i}) below minimum allowed ({min_val})")
        if max_val is not None and i > max_val:
            raise ValueError(f"Value for {key!r} ({i}) exceeds maximum allowed ({max_val})")
        return i

    target_score = _val_float("target_score", 80.0, 0.0, 100.0)
    weak_threshold = _val_float("weak_threshold", 65.0, 0.0, 100.0)
    strong_threshold = _val_float("strong_threshold", 80.0, 0.0, 100.0)

    # Validate threshold relationships
    if weak_threshold >= strong_threshold:
        raise ValueError(
            f"Contradictory adaptive thresholds: weak_threshold ({weak_threshold}) "
            f"must be strictly less than strong_threshold ({strong_threshold})"
        )

    mttd_weak_s = _val_float("mttd_weak_s", 16.0, 0.0, 120.0)
    mttd_strong_s = _val_float("mttd_strong_s", 10.0, 0.0, 120.0)
    if mttd_strong_s >= mttd_weak_s:
        raise ValueError(
            f"Contradictory detection latency thresholds: mttd_strong_s ({mttd_strong_s}) "
            f"must be strictly less than mttd_weak_s ({mttd_weak_s})"
        )

    practitioner_score = _val_float("practitioner_score", 65.0, 0.0, 100.0)
    expert_score = _val_float("expert_score", 82.0, 0.0, 100.0)
    if practitioner_score >= expert_score:
        raise ValueError(
            f"Contradictory mastery thresholds: practitioner_score ({practitioner_score}) "
            f"must be strictly less than expert_score ({expert_score})"
        )

    breach_rate_weak = _val_float("breach_rate_weak", 0.33, 0.0, 10.0)
    false_alarm_rate_weak = _val_float("false_alarm_rate_weak", 1.25, 0.0, 20.0)
    classification_weak_score = _val_float("classification_weak_score", 68.0, 0.0, 100.0)
    detection_weak_score = _val_float("detection_weak_score", 70.0, 0.0, 100.0)

    fa_weak_count = _val_float("fa_weak_count", 2.0, 0.0, 20.0)
    fa_strong_count = _val_float("fa_strong_count", 1.0, 0.0, 20.0)
    if fa_strong_count >= fa_weak_count:
        raise ValueError(f"fa_strong_count ({fa_strong_count}) must be less than fa_weak_count ({fa_weak_count})")

    env_drop_weak = _val_float("env_drop_weak", 20.0, 0.0, 100.0)
    env_strong_score = _val_float("env_strong_score", 75.0, 0.0, 100.0)
    hotspots_weak_count = _val_int("hotspots_weak_count", 3, 1, 20)
    hotspots_remediation_count = _val_int("hotspots_remediation_count", 2, 1, 20)
    breach_rate_expert = _val_float("breach_rate_expert", 0.2, 0.0, 1.0)
    breach_rate_practitioner = _val_float("breach_rate_practitioner", 0.5, 0.0, 1.0)

    return {
        "target_score": target_score,
        "weak_threshold": weak_threshold,
        "strong_threshold": strong_threshold,
        "breach_rate_weak": breach_rate_weak,
        "mttd_weak_s": mttd_weak_s,
        "mttd_strong_s": mttd_strong_s,
        "false_alarm_rate_weak": false_alarm_rate_weak,
        "classification_weak_score": classification_weak_score,
        "detection_weak_score": detection_weak_score,
        "expert_score": expert_score,
        "practitioner_score": practitioner_score,
        "fa_weak_count": fa_weak_count,
        "fa_strong_count": fa_strong_count,
        "env_drop_weak": env_drop_weak,
        "env_strong_score": env_strong_score,
        "hotspots_weak_count": hotspots_weak_count,
        "hotspots_remediation_count": hotspots_remediation_count,
        "breach_rate_expert": breach_rate_expert,
        "breach_rate_practitioner": breach_rate_practitioner,
    }


def get_qualifying_sessions(sessions_rows, rubric=None):
    """Filter and validate session records according to strict evidence validation policy.

    Single authoritative validation path for both skill evaluation and curriculum progression.
    Guarantees:
    - Excludes non-dict sessions, unverified/interrupted/rejected statuses, and unknown grades.
    - Excludes sessions whose result JSON is null, non-object, empty, or malformed.
    - Requires valid scenario ID and valid finite numeric scores in [0.0, 100.0].
    - Rejects boolean, string, or NaN/inf values for numeric measurements.
    - Safely tolerates legacy records omitting optional fields without overstating demonstrated skill.
    """
    valid_grades = set()
    if rubric and isinstance(rubric, dict) and "grade_bands" in rubric:
        for b in rubric.get("grade_bands", []):
            if isinstance(b, dict) and "grade" in b and isinstance(b["grade"], str):
                valid_grades.add(b["grade"].strip().upper())
    if not valid_grades:
        valid_grades = {"A", "B", "C", "D", "E", "F", "SATISFACTORY", "UNSATISFACTORY"}

    qualifying = []
    if not isinstance(sessions_rows, (list, tuple)):
        return qualifying

    for s in sessions_rows:
        if not isinstance(s, dict):
            continue

        # 1. Grade validation: must be recognized qualifying grade
        grade = s.get("grade")
        if not grade or not isinstance(grade, str):
            continue
        clean_grade = grade.strip().upper()
        if clean_grade in ("INCOMPLETE", "UNVERIFIED") or clean_grade not in valid_grades:
            continue

        # 2. Session status validation
        # Allows genuinely legacy records to omit optional status fields when backward compatibility requires it.
        # If an explicit status is present in session or parsed result, accept only recognized completed statuses ("completed").
        # Explicitly reject unverified, interrupted, rejected, failed, abandoned, unknown, explicit null, non-string, etc.
        COMPLETED_STATUSES = {"completed"}

        def _check_status_keys(container):
            found_any = False
            for k in ("session_status", "status"):
                if k in container:
                    found_any = True
                    val = container[k]
                    if val is None or not isinstance(val, str):
                        return "INVALID"
                    if val.strip().lower() not in COMPLETED_STATUSES:
                        return "INVALID"
            return "VALID" if found_any else "ABSENT"

        st_top = _check_status_keys(s)
        if st_top == "INVALID":
            continue

        # 3. Result JSON validation: must parse to a non-empty dictionary
        raw_res = s.get("result")
        if raw_res is None:
            continue
        if isinstance(raw_res, str):
            if raw_res.strip().lower() in ("null", ""):
                continue
            try:
                parsed_res = json.loads(raw_res)
            except Exception:
                continue
        elif isinstance(raw_res, dict):
            parsed_res = raw_res
        else:
            # Result is scalar int, list, float, boolean, etc.
            continue

        if not isinstance(parsed_res, dict) or not parsed_res:
            continue

        # If result dict itself contains session_status or status, verify it
        st_nest = _check_status_keys(parsed_res)
        if st_nest == "INVALID":
            continue

        # Grade consistency between session metadata and parsed result metadata
        if "grade" in parsed_res:
            res_grade = parsed_res["grade"]
            if res_grade is None or not isinstance(res_grade, str):
                continue
            if res_grade.strip().upper() != clean_grade:
                continue

        # 4. Scenario ID validation (guarded against non-dict scenario object in parsed_result)
        scen_id = s.get("scenario_id")
        if not scen_id:
            res_scen = parsed_res.get("scenario")
            if isinstance(res_scen, dict):
                scen_id = res_scen.get("id")
        if not scen_id or not isinstance(scen_id, str):
            continue

        # 5. Score validation: total, detection, classification, engagement must be valid numeric in [0.0, 100.0]
        # Strict numeric-score policy: rejects explicit None, numeric strings (e.g. "85.0", "0"), booleans, NaN/inf.
        # Enforces consistency when both top-level session and nested result metadata are present.
        if "stages" in parsed_res:
            if parsed_res["stages"] is None or not isinstance(parsed_res["stages"], dict):
                continue
            stages = parsed_res["stages"]
        else:
            stages = {}

        def _validate_score_field(top_present, top_raw, nest_present, nest_raw):
            if not top_present and not nest_present:
                return False, None
            v_top = None
            if top_present:
                v_top = _safe_float(top_raw, min_val=0.0, max_val=100.0)
                if v_top is None:
                    return False, None
            v_nest = None
            if nest_present:
                v_nest = _safe_float(nest_raw, min_val=0.0, max_val=100.0)
                if v_nest is None:
                    return False, None
            if top_present and nest_present:
                if abs(v_top - v_nest) > 0.5:
                    return False, None
                return True, v_top
            if top_present:
                return True, v_top
            return True, v_nest

        valid_tot, clean_tot = _validate_score_field("total" in s, s.get("total"), "total" in parsed_res, parsed_res.get("total"))
        valid_det, clean_det = _validate_score_field("detection" in s, s.get("detection"), "detection" in stages, stages.get("detection"))
        valid_cls, clean_cls = _validate_score_field("classification" in s, s.get("classification"), "classification" in stages, stages.get("classification"))
        valid_eng, clean_eng = _validate_score_field("engagement" in s, s.get("engagement"), "engagement" in stages, stages.get("engagement"))

        if not (valid_tot and valid_det and valid_cls and valid_eng):
            # Critical score missing or malformed: exclude session
            continue

        # 6. Non-negative diagnostics counts (false_alarms, breaches, critical_errors)
        # Distinguish genuinely absent optional fields (legacy records) from present but malformed values.
        # An invalid present penalty value (None, negative, boolean, float/fractional, NaN/inf, string)
        # must NOT be coerced to zero; it must cause the session to be excluded from qualifying evidence.
        if "penalties" in parsed_res:
            if parsed_res["penalties"] is None or not isinstance(parsed_res["penalties"], dict):
                continue
            penalties = parsed_res["penalties"]
        else:
            penalties = {}

        def _check_penalty_val(v):
            if v is None or isinstance(v, (bool, str, bytes, list, dict, set, tuple)):
                return False, None
            if isinstance(v, int):
                if v < 0:
                    return False, None
                return True, v
            if isinstance(v, float):
                if math.isnan(v) or math.isinf(v) or not v.is_integer() or v < 0:
                    return False, None
                return True, int(v)
            try:
                from decimal import Decimal
                if isinstance(v, Decimal):
                    if v < 0 or v != v.to_integral_value():
                        return False, None
                    return True, int(v)
            except (ImportError, Exception):
                pass
            return False, None

        def _validate_penalty_metric(top_present, top_raw, nest_present, nest_raw):
            if not top_present and not nest_present:
                return True, 0
            v_top = None
            if top_present:
                top_ok, v_top = _check_penalty_val(top_raw)
                if not top_ok:
                    return False, None
            v_nest = None
            if nest_present:
                nest_ok, v_nest = _check_penalty_val(nest_raw)
                if not nest_ok:
                    return False, None
            if top_present and nest_present:
                if v_top != v_nest:
                    return False, None
                return True, v_top
            if top_present:
                return True, v_top
            return True, v_nest

        valid_fa, fa = _validate_penalty_metric("false_alarms" in s, s.get("false_alarms"), "false_alarms" in penalties, penalties.get("false_alarms"))
        valid_br, br = _validate_penalty_metric("breaches" in s, s.get("breaches"), "breaches" in penalties, penalties.get("breaches"))
        valid_cr, cr = _validate_penalty_metric("critical_errors" in s, s.get("critical_errors"), "critical_errors" in penalties, penalties.get("critical_errors"))

        if not (valid_fa and valid_br and valid_cr):
            # Exclude session with invalid penalty measurement
            continue

        qualifying.append({
            **s,
            "scenario_id": scen_id,
            "grade": clean_grade,
            "total": clean_tot,
            "detection": clean_det,
            "classification": clean_cls,
            "engagement": clean_eng,
            "false_alarms": fa,
            "breaches": br,
            "critical_errors": cr,
            "parsed_result": parsed_res,
        })

    return qualifying


def _validate_session_end_tolerance(rubric=None, default=0.5, min_val=0.0, max_val=10.0):
    """Validate and extract session_end_tolerance_s from rubric geometry.

    Enforces strict numeric validation:
    - Must be a finite, non-negative int or float within [0.0, 10.0].
    - Strictly rejects booleans, strings (including numeric strings like "0.5"),
      bytes (e.g. b"0.5"), collections, NaN, and infinities.
    - Defaults to 0.5 when rubric, geometry, or session_end_tolerance_s is omitted or None.
    - Raises ValueError on invalid types, negative, non-finite, or out-of-range tolerance.
    """
    if rubric is None:
        return float(default)
    if not isinstance(rubric, dict):
        raise ValueError("Rubric must be a dictionary")

    if "geometry" not in rubric or rubric["geometry"] is None:
        return float(default)
    geometry = rubric["geometry"]
    if not isinstance(geometry, dict):
        raise ValueError("Rubric geometry configuration must be a dictionary")

    if "session_end_tolerance_s" not in geometry or geometry["session_end_tolerance_s"] is None:
        return float(default)

    val = geometry["session_end_tolerance_s"]
    # Booleans are subclasses of int in Python (isinstance(True, int) is True)
    if isinstance(val, bool):
        raise ValueError("Invalid boolean value for session_end_tolerance_s")
    if isinstance(val, (str, bytes)):
        raise ValueError(f"String or bytes value not permitted for session_end_tolerance_s: {val!r}")
    if not isinstance(val, (int, float)):
        raise ValueError(f"Non-numeric value for session_end_tolerance_s: {val!r}")

    try:
        f = float(val)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"Non-numeric value for session_end_tolerance_s: {val!r}")

    if math.isnan(f) or math.isinf(f):
        raise ValueError(f"Invalid NaN or infinite value for session_end_tolerance_s: {val!r}")
    if min_val is not None and f < min_val:
        raise ValueError(f"Value for session_end_tolerance_s ({f}) below minimum allowed ({min_val})")
    if max_val is not None and f > max_val:
        raise ValueError(f"Value for session_end_tolerance_s ({f}) exceeds maximum allowed ({max_val})")
    return f


def _resolve_session_end(q, res, rubric=None):
    """Determine the authoritative session end time and tolerance for timeline validation.

    Returns (session_end, session_end_tol) if a reliable session end can be established,
    or (None, session_end_tol) if the timeline cannot be validated reliably.
    """
    tol = _validate_session_end_tolerance(rubric)

    # 1. Authoritative ended_t if explicitly present in parsed result or session row
    has_explicit_ended = ("ended_t" in res) or ("ended_t" in q)
    raw_ended_t = res.get("ended_t") if "ended_t" in res else q.get("ended_t")
    if has_explicit_ended:
        ended_t = _safe_float(raw_ended_t, min_val=0.0, max_val=10000.0, default=None)
        if ended_t is None:
            # Explicit ended_t is malformed/corrupted: cannot validate timeline reliably
            return None, tol
    else:
        ended_t = None

    # 2. Authoritative scenario duration
    scen_info = res.get("scenario") if isinstance(res.get("scenario"), dict) else {}
    raw_dur = scen_info.get("duration_s") if "duration_s" in scen_info else (res.get("duration_s") or q.get("duration_s"))
    scen_duration = _safe_float(raw_dur, min_val=0.0, max_val=10000.0, default=None)

    if scen_duration is None:
        scen_id = q.get("scenario_id") or scen_info.get("id")
        if scen_id and isinstance(scen_id, str):
            try:
                params = scen_info.get("params") or q.get("params")
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except Exception:
                        params = None
                sc_obj = scen.get_scenario(scen_id, params if isinstance(params, dict) else None)
                if isinstance(sc_obj, dict) and "duration_s" in sc_obj:
                    scen_duration = _safe_float(sc_obj.get("duration_s"), min_val=0.0, max_val=10000.0, default=None)
            except Exception:
                pass

    # 3. Combine ended_t and scenario duration
    if ended_t is not None and scen_duration is not None:
        session_end = min(ended_t, scen_duration)
    elif ended_t is not None:
        session_end = ended_t
    elif scen_duration is not None:
        session_end = scen_duration
    else:
        # Cannot determine session end reliably
        session_end = None

    return session_end, tol


def evaluate_trainee_skills(sessions_rows, rubric=None):
    """Derive an explainable multi-dimensional skill profile from validated session history.

    Filters strictly for completed, qualifying sessions with documented final grades.
    Excludes INCOMPLETE, UNVERIFIED, rejected, and malformed non-object sessions.
    Returns an objective diagnostic dictionary with dimensions:
    - detection (score, reaction latency, false alarms)
    - classification (score, confusion hotspots, false hostility)
    - engagement (score, breaches, critical errors)
    - environmental_resilience (performance under sensor noise/fog/night)
    """
    acfg = _get_adaptive_config(rubric)
    qualifying = get_qualifying_sessions(sessions_rows, rubric)
    n = len(qualifying)
    if n == 0:
        return {
            "sample_size": 0,
            "confidence": "NONE",
            "mastery_level": "NOVICE",
            "average_score": None,
            "dimensions": {
                "detection": {"score": None, "rating": "UNTESTED"},
                "classification": {"score": None, "rating": "UNTESTED"},
                "engagement": {"score": None, "rating": "UNTESTED"},
                "environmental_resilience": {"score": None, "rating": "UNTESTED"},
            },
            "diagnostics": {
                "weakest_dimension": None,
                "mean_time_to_detect_s": None,
                "false_alarms_per_session": 0.0,
                "total_breaches": 0,
                "breach_rate": 0.0,
                "critical_errors": 0,
                "confusion_hotspots": [],
            },
        }

    # Confidence based on sample size
    if n >= 5:
        confidence = "HIGH"
    elif n >= 3:
        confidence = "MODERATE"
    else:
        confidence = "LOW"

    # Stage scores safely extracted
    det_scores = [_safe_float(q.get("detection")) for q in qualifying]
    det_scores = [x for x in det_scores if x is not None]

    cls_scores = [_safe_float(q.get("classification")) for q in qualifying]
    cls_scores = [x for x in cls_scores if x is not None]

    eng_scores = [_safe_float(q.get("engagement")) for q in qualifying]
    eng_scores = [x for x in eng_scores if x is not None]

    tot_scores = [_safe_float(q.get("total")) for q in qualifying]
    tot_scores = [x for x in tot_scores if x is not None]

    avg_det = _avg(det_scores) or 0.0
    avg_cls = _avg(cls_scores) or 0.0
    avg_eng = _avg(eng_scores) or 0.0
    avg_tot = _avg(tot_scores) or 0.0

    # Detection latency & false alarms
    detect_deltas = []
    total_false_alarms = 0
    total_breaches = 0
    total_critical = 0
    confusion_pairs = {}

    # Valid classification vocabulary from rubric or standard classes
    valid_classes = set()
    if rubric and isinstance(rubric, dict) and "classes" in rubric and isinstance(rubric["classes"], dict):
        valid_classes = {k.strip().upper() for k in rubric["classes"].keys() if isinstance(k, str)}
    if not valid_classes:
        valid_classes = {"RECON_UAS", "ARMED_UAS", "DECOY", "BIRD", "FRIENDLY"}

    degraded_scores = []
    clean_scores = []

    for q in qualifying:
        res = q.get("parsed_result", {})
        total_false_alarms += _safe_int(q.get("false_alarms"), min_val=0)
        total_breaches += _safe_int(q.get("breaches"), min_val=0)
        total_critical += _safe_int(q.get("critical_errors"), min_val=0)

        # Environmental breakdown
        scen_info = res.get("scenario") if isinstance(res.get("scenario"), dict) else {}
        params = scen_info.get("params") if isinstance(scen_info.get("params"), dict) else {}
        scen_id = q.get("scenario_id") or scen_info.get("id") or ""
        deg_val = _safe_int(params.get("degradation"), min_val=0)
        is_degraded = (
            scen_id in ("s2-night-loiter", "s5-fog-noise", "s6-saturation-swarm")
            or deg_val > 0
            or params.get("time_of_day") in ("night", "dusk")
        )
        q_tot = _safe_float(q.get("total"))
        if q_tot is not None:
            if is_degraded:
                degraded_scores.append(q_tot)
            else:
                clean_scores.append(q_tot)

        # Authoritative session end and time tolerance for timeline validation
        session_end, session_end_tol = _resolve_session_end(q, res, rubric)

        contacts = res.get("contacts")
        if isinstance(contacts, list):
            for c in contacts:
                # 1. Require exact boolean True for scored (reject truthiness and string "false"/"true")
                if not isinstance(c, dict) or c.get("scored") is not True:
                    continue

                # 2. Vocabulary validation on true_class: must be recognized in rubric classes
                true_cls = c.get("true_class")
                if not isinstance(true_cls, str) or true_cls.strip().upper() not in valid_classes:
                    continue
                clean_true = true_cls.strip().upper()

                # 3. Vocabulary validation on chosen class if classified
                cls_info = c.get("classification")
                chosen_cls = None
                if isinstance(cls_info, dict):
                    raw_chosen = cls_info.get("chosen")
                    if raw_chosen is not None:
                        if not isinstance(raw_chosen, str) or raw_chosen.strip().upper() not in valid_classes:
                            # Malformed classification label: discard contact to prevent fabricated diagnostics
                            continue
                        chosen_cls = raw_chosen.strip().upper()

                # 4. Session-bounded timestamp validation for detection latency:
                # - When an authoritative session end is present, require spawn and detection timestamps
                #   to be consistent with that session end and the scoring engine's documented tolerance.
                # - When legacy results omit the end time, use the authoritative scenario duration.
                # - Do not silently treat the arbitrary 10,000-second cap as the actual session duration.
                # - Do not calculate detection latency if the timeline cannot be validated reliably.
                if session_end is not None:
                    max_session_t = session_end + session_end_tol
                    # Validate spawn_t: finite, non-negative, and bounded by max_session_t (do NOT default to 0.0)
                    spawn_t = _safe_float(c.get("spawn_t"), min_val=0.0, max_val=max_session_t, default=None)
                    if spawn_t is not None:
                        det_info = c.get("detection")
                        if isinstance(det_info, dict):
                            # Validate det_t: finite, non-negative, and bounded by max_session_t
                            det_t = _safe_float(det_info.get("t"), min_val=0.0, max_val=max_session_t, default=None)
                            if det_t is not None and det_t >= spawn_t:
                                detect_deltas.append(round(det_t - spawn_t, 2))

                # 5. Record confusion pair if classified and disparate (independent of timing validity)
                if chosen_cls and clean_true != chosen_cls:
                    pair = f"{clean_true} -> {chosen_cls}"
                    confusion_pairs[pair] = confusion_pairs.get(pair, 0) + 1

    mttd = _avg(detect_deltas)
    fa_per_session = round(total_false_alarms / n, 2)
    breach_rate = round(total_breaches / n, 2)

    # Confusion hotspots sorted by frequency
    hotspots = [
        {"pattern": pair, "count": cnt}
        for pair, cnt in sorted(confusion_pairs.items(), key=lambda x: x[1], reverse=True)
    ]

    # Dimension ratings using configurable thresholds
    acfg = _get_adaptive_config(rubric)

    dim_ratings = {
        "detection": {
            "score": avg_det,
            "rating": "WEAK" if (avg_det < acfg["weak_threshold"] or (mttd and mttd > acfg["mttd_weak_s"]) or fa_per_session >= acfg["fa_weak_count"])
            else "STRONG" if (avg_det >= acfg["strong_threshold"] and (not mttd or mttd <= acfg["mttd_strong_s"]) and fa_per_session < acfg["fa_strong_count"])
            else "SATISFACTORY",
        },
        "classification": {
            "score": avg_cls,
            "rating": "WEAK" if (avg_cls < acfg["weak_threshold"] or total_critical > 0 or len(hotspots) >= acfg["hotspots_weak_count"])
            else "STRONG" if (avg_cls >= acfg["strong_threshold"] and not hotspots)
            else "SATISFACTORY",
        },
        "engagement": {
            "score": avg_eng,
            "rating": "WEAK" if (avg_eng < acfg["weak_threshold"] or breach_rate >= acfg["breach_rate_weak"])
            else "STRONG" if (avg_eng >= acfg["strong_threshold"] and total_breaches == 0)
            else "SATISFACTORY",
        },
    }

    # Environmental resilience rating using configurable thresholds
    avg_degraded = _avg(degraded_scores)
    avg_clean = _avg(clean_scores)
    if avg_degraded is None:
        env_rating = "UNTESTED"
        env_score = None
    elif avg_clean is not None and (avg_clean - avg_degraded) >= acfg["env_drop_weak"]:
        env_rating = "WEAK"
        env_score = avg_degraded
    elif avg_degraded >= acfg["env_strong_score"]:
        env_rating = "STRONG"
        env_score = avg_degraded
    else:
        env_rating = "SATISFACTORY"
        env_score = avg_degraded

    dim_ratings["environmental_resilience"] = {
        "score": env_score,
        "rating": env_rating,
        "clean_avg": avg_clean,
        "degraded_avg": avg_degraded,
    }

    # Weakest dimension determination (deterministic order)
    scored_dims = [
        (k, v["score"]) for k, v in dim_ratings.items()
        if k != "environmental_resilience" and v["score"] is not None
    ]
    weakest_dim = min(scored_dims, key=lambda x: x[1])[0] if scored_dims else None

    # Overall Mastery Level using configurable thresholds
    if n >= 5 and avg_tot >= acfg["target_score"] and breach_rate < acfg["breach_rate_expert"] and fa_per_session < acfg["fa_strong_count"]:
        mastery = "EXPERT"
    elif n >= 3 and avg_tot >= acfg["practitioner_score"] and breach_rate < acfg["breach_rate_practitioner"]:
        mastery = "PRACTITIONER"
    else:
        mastery = "NOVICE"

    return {
        "sample_size": n,
        "confidence": confidence,
        "mastery_level": mastery,
        "average_score": avg_tot,
        "dimensions": dim_ratings,
        "diagnostics": {
            "weakest_dimension": weakest_dim,
            "mean_time_to_detect_s": mttd,
            "false_alarms_per_session": fa_per_session,
            "total_breaches": total_breaches,
            "breach_rate": breach_rate,
            "critical_errors": total_critical,
            "confusion_hotspots": hotspots[:3],
        },
    }


def recommend_next_scenario(trainee_dict, sessions_rows, rubric=None, policy_version=POLICY_VERSION):
    """Select the optimal next training scenario and difficulty based on demonstrated evidence.

    Deterministic and fully explainable. Outputs:
    - target scenario ID and readable name
    - execution parameters (scripted vs procedural)
    - difficulty level (1-5 bounded)
    - difficulty type ('curriculum_tier' for scripted, 'parameter' for procedural)
    - primary training focus area
    - plain-language rationale referencing actual performance evidence
    - concrete progression criteria to achieve next level

    Note on Determinism: Given the same validated session inputs, rubric, and policy_version,
    all recommendation decisions (rule_id, scenario_id, difficulty, focus_area, launch_params,
    and rationale) are 100% deterministic. The 'evaluated_at' field provides operational
    audit metadata recording when the evaluation was computed.
    """
    acfg = _get_adaptive_config(rubric)
    qualifying = get_qualifying_sessions(sessions_rows, rubric)
    profile = evaluate_trainee_skills(sessions_rows, rubric)
    n = profile["sample_size"]
    dims = profile["dimensions"]
    diag = profile["diagnostics"]

    # History of completed scripted scenario IDs derived strictly from validated qualifying evidence
    completed_scenarios = {q["scenario_id"] for q in qualifying if q.get("scenario_id")}

    # 1. New Trainee / Insufficient Baseline (0 sessions)
    if n == 0:
        return {
            "policy_version": policy_version,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "trainee": trainee_dict,
            "skill_profile": profile,
            "recommendation": {
                "rule_id": "REC-01-BASELINE-ONBOARDING",
                "scenario_kind": "scripted",
                "scenario_id": "s1-dawn-recon",
                "scenario_name": SCRIPTED_NAMES["s1-dawn-recon"],
                "difficulty": 1,
                "difficulty_type": "curriculum_tier",
                "focus_area": "Fundamentals: Detection, Identification & Reporting",
                "rationale": (
                    "No qualifying assessment history found. Recommended baseline onboarding mission "
                    "to assess optical contact detection, standard UAS classification, and reporting procedures."
                ),
                "progression_criteria": (
                    "Score >= 75.0 with zero false alarms and mean detection latency under 12.0 seconds "
                    "to unlock tactical interception missions."
                ),
                "launch_params": {
                    "kind": "scripted",
                    "id": "s1-dawn-recon",
                    "vary": True,
                },
            },
        }

    # 2. Priority 1: Critical Defense Breaches & Engagement Deficits
    # If breach rate >= breach_rate_weak or engagement score < weak_threshold
    if diag["breach_rate"] >= acfg["breach_rate_weak"] or (dims["engagement"]["score"] is not None and dims["engagement"]["score"] < acfg["weak_threshold"]):
        # If breaches occurred with multiple hostiles/swarms, target swarm triage
        if diag["total_breaches"] >= 3 and "s6-saturation-swarm" in completed_scenarios:
            rec_id = "s6-saturation-swarm"
            rec_diff = 2
            rationale = (
                f"Trainee experienced {diag['total_breaches']} defense perimeter breach(es) (rate: {diag['breach_rate']}/session). "
                "Recommended Saturation Swarm scenario focuses on target triage and prioritizing closest inbound threats."
            )
            focus = "Perimeter Defense & Threat Triage under Swarm Saturation"
        else:
            rec_id = "s2-night-loiter"
            rec_diff = 1 if profile["mastery_level"] == "NOVICE" else 2
            rationale = (
                f"Low engagement score ({dims['engagement']['score']}%) or perimeter breaches detected ({diag['total_breaches']} breaches). "
                "Night Loitering Drone scenario emphasizes recognizing autonomous loitering profiles and executing decisive kinetic countermeasures."
            )
            focus = "Autonomous Threat Neutralization & Decisive Kinetic Engagement"

        return {
            "policy_version": policy_version,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "trainee": trainee_dict,
            "skill_profile": profile,
            "recommendation": {
                "rule_id": "REC-02-ENGAGEMENT-BREACH-RECOVERY",
                "scenario_kind": "scripted",
                "scenario_id": rec_id,
                "scenario_name": SCRIPTED_NAMES[rec_id],
                "difficulty": rec_diff,
                "difficulty_type": "curriculum_tier",
                "focus_area": focus,
                "rationale": rationale,
                "progression_criteria": "Neutralize 100% of inbound hostile threats before the 1,000m defense perimeter ring with 0 breaches.",
                "launch_params": {
                    "kind": "scripted",
                    "id": rec_id,
                    "vary": True,
                },
            },
        }

    # 3. Priority 2: Target Discrimination, Confusion & False Alarms
    if (
        (dims["classification"]["score"] is not None and dims["classification"]["score"] < acfg["classification_weak_score"])
        or diag["false_alarms_per_session"] >= acfg["false_alarm_rate_weak"]
        or diag["critical_errors"] > 0
        or len(diag["confusion_hotspots"]) >= acfg["hotspots_remediation_count"]
    ):
        top_confusion = diag["confusion_hotspots"][0]["pattern"] if diag["confusion_hotspots"] else "decoys/benign contacts"
        return {
            "policy_version": policy_version,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "trainee": trainee_dict,
            "skill_profile": profile,
            "recommendation": {
                "rule_id": "REC-03-DISCRIMINATION-AND-RESTRAINT",
                "scenario_kind": "scripted",
                "scenario_id": "s4-mixed-traffic",
                "scenario_name": SCRIPTED_NAMES["s4-mixed-traffic"],
                "difficulty": 2,
                "difficulty_type": "curriculum_tier",
                "focus_area": "Target Discrimination, False Alarm Suppression & Restraint",
                "rationale": (
                    f"Classification score ({dims['classification']['score']}%) or false alarm frequency "
                    f"({diag['false_alarms_per_session']}/session) requires remediation. Primary confusion hotspot: {top_confusion}. "
                    "Scenario s4-mixed-traffic exercises discriminating hostile drones from birds, decoys, and friendly aircraft."
                ),
                "progression_criteria": (
                    "Achieve >= 85.0% classification accuracy with 0 friendly fire incidents and <= 1 false alarm."
                ),
                "launch_params": {
                    "kind": "scripted",
                    "id": "s4-mixed-traffic",
                    "vary": True,
                },
            },
        }

    # 4. Priority 3: Detection Latency & Sightline Pop-up Tracking
    if (
        (dims["detection"]["score"] is not None and dims["detection"]["score"] < acfg["detection_weak_score"])
        or (diag["mean_time_to_detect_s"] and diag["mean_time_to_detect_s"] > (acfg["mttd_weak_s"] - 2.0))
    ):
        return {
            "policy_version": policy_version,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "trainee": trainee_dict,
            "skill_profile": profile,
            "recommendation": {
                "rule_id": "REC-04-RAPID-DETECTION-POPUP",
                "scenario_kind": "scripted",
                "scenario_id": "s3-urban-canyon",
                "scenario_name": SCRIPTED_NAMES["s3-urban-canyon"],
                "difficulty": 2,
                "difficulty_type": "curriculum_tier",
                "focus_area": "Rapid Detection & Pop-Up Sightline Tracking",
                "rationale": (
                    f"Detection reaction time ({diag['mean_time_to_detect_s'] or 'slow'}s) or detection score ({dims['detection']['score']}%) "
                    "indicates delayed contact acquisition. Urban Canyon scenario exercises rapid acquisition during fleeting visual windows between buildings."
                ),
                "progression_criteria": "Acquire and mark hostile quadcopter in the initial roofline pop-up window within 10.0 seconds of spawn.",
                "launch_params": {
                    "kind": "scripted",
                    "id": "s3-urban-canyon",
                    "vary": True,
                },
            },
        }

    # 5. Priority 4: Environmental & Sensor Degradation Sensitivity
    if dims["environmental_resilience"]["rating"] == "WEAK":
        clean_avg = dims["environmental_resilience"].get("clean_avg") or 0.0
        deg_avg = dims["environmental_resilience"].get("degraded_avg") or 0.0
        return {
            "policy_version": policy_version,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "trainee": trainee_dict,
            "skill_profile": profile,
            "recommendation": {
                "rule_id": "REC-05-SENSOR-DEGRADATION-RESILIENCE",
                "scenario_kind": "scripted",
                "scenario_id": "s5-fog-noise",
                "scenario_name": SCRIPTED_NAMES["s5-fog-noise"],
                "difficulty": 3,
                "difficulty_type": "curriculum_tier",
                "focus_area": "Degraded Visual Operations & Radar Console Cueing",
                "rationale": (
                    f"Performance drops under degraded conditions ({deg_avg}% vs {clean_avg}% in clean visibility). "
                    "Fog and Noise scenario trains cross-referencing radar console cues with thermal/night optics under adverse conditions."
                ),
                "progression_criteria": "Detect and engage both hostile contacts with >= 75.0% total score under Level 3 sensor degradation.",
                "launch_params": {
                    "kind": "scripted",
                    "id": "s5-fog-noise",
                    "vary": True,
                },
            },
        }

    # 6. Priority 5: Mastery Escalation & Advanced Procedural Swarms
    if profile["mastery_level"] == "EXPERT" or (n >= 3 and profile["average_score"] and profile["average_score"] >= acfg["expert_score"]):
        # If saturation swarm has not been scored >= 85, recommend it first
        s6_scores = [q["total"] for q in qualifying if q.get("scenario_id") == "s6-saturation-swarm"]
        if not s6_scores or max(s6_scores) < 85.0:
            return {
                "policy_version": policy_version,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "trainee": trainee_dict,
                "skill_profile": profile,
                "recommendation": {
                    "rule_id": "REC-06-SWARM-TRIAGE-MASTERY",
                    "scenario_kind": "scripted",
                    "scenario_id": "s6-saturation-swarm",
                    "scenario_name": SCRIPTED_NAMES["s6-saturation-swarm"],
                    "difficulty": 4,
                    "difficulty_type": "curriculum_tier",
                    "focus_area": "Multi-Axis Swarm Saturation Defense",
                    "rationale": (
                        f"Consistent high performance across standard missions (average score: {profile['average_score']}%). "
                        "Escalating to Saturation Swarm to test multi-axis defense under high cognitive load."
                    ),
                    "progression_criteria": "Achieve >= 85.0% total score against 8-drone multi-axis swarm with zero perimeter breaches.",
                    "launch_params": {
                        "kind": "scripted",
                        "id": "s6-saturation-swarm",
                        "vary": True,
                    },
                },
            }
        else:
            # Procedural Generation escalation: difficulty bounded progression
            recent_diffs = []
            for q in qualifying:
                params = q.get("params")
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except Exception:
                        params = {}
                if isinstance(params, dict) and "difficulty" in params:
                    recent_diffs.append(params["difficulty"])
            current_diff = max(recent_diffs, default=3)
            next_diff = min(5, current_diff + 1)
            proc_seed = 10000 + (n * 37) % 900000

            return {
                "policy_version": policy_version,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "trainee": trainee_dict,
                "skill_profile": profile,
                "recommendation": {
                    "rule_id": "REC-07-PROCEDURAL-SWARM-ESCALATION",
                    "scenario_kind": "procedural",
                    "scenario_id": f"proc-diff{next_diff}-seed{proc_seed}",
                    "scenario_name": f"Procedural Swarm Defense (Difficulty {next_diff})",
                    "difficulty": next_diff,
                    "difficulty_type": "parameter",
                    "focus_area": "Adaptive Dynamic Swarm & Mixed Threat Complexity",
                    "rationale": (
                        f"Trainee has achieved Expert mastery (average score: {profile['average_score']}%). "
                        f"Advancing to procedural generation at Difficulty {next_diff} with dynamic swarm spawns and mixed threat profiles."
                    ),
                    "progression_criteria": f"Maintain >= 80.0% score at Difficulty {next_diff} to qualify for elite operator readiness.",
                    "launch_params": {
                        "kind": "procedural",
                        "params": {
                            "seed": proc_seed,
                            "difficulty": next_diff,
                            "terrain": "urban" if next_diff >= 4 else "rural",
                            "time_of_day": "night" if next_diff >= 4 else "dusk",
                        },
                    },
                },
            }

    # 7. Priority 6: Sequential Curriculum Progression for Practitioners
    # Look for the first uncompleted scripted scenario in order 1 through 6
    ordered_scenarios = [
        ("s1-dawn-recon", 1, "Basic Detection & Identification"),
        ("s2-night-loiter", 2, "Night Observation & Kinetic Response"),
        ("s3-urban-canyon", 2, "Fast Acquisition in Urban Occlusion"),
        ("s4-mixed-traffic", 2, "Target Discrimination & Restraint"),
        ("s5-fog-noise", 3, "Degraded Sensor Operations"),
        ("s6-saturation-swarm", 3, "Swarm Threat Prioritization"),
    ]
    for s_id, s_diff, s_focus in ordered_scenarios:
        if s_id not in completed_scenarios:
            return {
                "policy_version": policy_version,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "trainee": trainee_dict,
                "skill_profile": profile,
                "recommendation": {
                    "rule_id": "REC-08-CURRICULUM-PROGRESSION",
                    "scenario_kind": "scripted",
                    "scenario_id": s_id,
                    "scenario_name": SCRIPTED_NAMES[s_id],
                    "difficulty": s_diff,
                    "difficulty_type": "curriculum_tier",
                    "focus_area": s_focus,
                    "rationale": (
                        f"Standard training curriculum progression. Trainee is ready for next syllabus objective: {SCRIPTED_NAMES[s_id]}."
                    ),
                    "progression_criteria": f"Complete {SCRIPTED_NAMES[s_id]} with qualifying score >= 75.0.",
                    "launch_params": {
                        "kind": "scripted",
                        "id": s_id,
                        "vary": True,
                    },
                },
            }

    # Fallback: Reinforcement run on weakest dimension
    fallback_id = "s3-urban-canyon" if diag["weakest_dimension"] == "detection" else "s4-mixed-traffic"
    return {
        "policy_version": policy_version,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "trainee": trainee_dict,
        "skill_profile": profile,
        "recommendation": {
            "rule_id": "REC-09-SKILL-REINFORCEMENT",
            "scenario_kind": "scripted",
            "scenario_id": fallback_id,
            "scenario_name": SCRIPTED_NAMES[fallback_id],
            "difficulty": 2,
            "difficulty_type": "curriculum_tier",
            "focus_area": f"Reinforce {diag['weakest_dimension'] or 'core skills'}",
            "rationale": f"All baseline scenarios completed. Reinforcing diagnosed priority area: {diag['weakest_dimension'] or 'tactical defense'}.",
            "progression_criteria": "Maintain consistent performance >= 80.0 across varied seeded runs.",
            "launch_params": {
                "kind": "scripted",
                "id": fallback_id,
                "vary": True,
            },
        },
    }
