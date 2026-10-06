// Contact paths. Mirrors app/geometry.py so the view shows what the server scores.

function dist(a, b) {
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}

export function pathLength(wps) {
  let total = 0;
  for (let i = 0; i < wps.length - 1; i++) total += dist(wps[i], wps[i + 1]);
  return total;
}

export function endTime(c) {
  if (c._end === undefined) c._end = c.spawn_t + pathLength(c.waypoints) / c.speed_mps;
  return c._end;
}

/** Writes the position at time t into out and returns true, or returns false outside the path. */
export function positionAt(c, t, out) {
  const elapsed = t - c.spawn_t;
  if (elapsed < 0) return false;
  let travelled = elapsed * c.speed_mps;
  const w = c.waypoints;
  for (let i = 0; i < w.length - 1; i++) {
    const seg = dist(w[i], w[i + 1]);
    if (travelled <= seg) {
      const f = seg ? travelled / seg : 0;
      out[0] = w[i][0] + (w[i + 1][0] - w[i][0]) * f;
      out[1] = w[i][1] + (w[i + 1][1] - w[i][1]) * f;
      out[2] = w[i][2] + (w[i + 1][2] - w[i][2]) * f;
      return true;
    }
    travelled -= seg;
  }
  return false;
}

const tmp = [0, 0, 0];
export function rangeAt(c, t) {
  if (!positionAt(c, t, tmp)) return null;
  return Math.hypot(tmp[0], tmp[1], tmp[2]);
}

export function endsInside(c, innerRing) {
  const last = c.waypoints[c.waypoints.length - 1];
  return Math.hypot(last[0], last[2]) <= innerRing;
}

/** Bearing in degrees clockwise from north (-z). */
export function bearingOf(x, z) {
  return (Math.atan2(x, -z) * 180 / Math.PI + 360) % 360;
}
