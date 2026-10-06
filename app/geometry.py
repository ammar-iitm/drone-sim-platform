"""Contact paths: a contact flies its waypoint polyline at constant speed from spawn_t.

The observation post is at the origin; units are metres; y is altitude.
The simulator draws seeded wobble on top of this path for looks only, so scoring
always uses the clean path.
"""

import math


def _dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def path_length(waypoints):
    return sum(_dist(waypoints[i], waypoints[i + 1]) for i in range(len(waypoints) - 1))


def end_time(contact):
    return contact["spawn_t"] + path_length(contact["waypoints"]) / contact["speed_mps"]


def position_at(contact, t):
    """Position at scenario time t, or None before spawn or after the path ends."""
    elapsed = t - contact["spawn_t"]
    if elapsed < 0:
        return None
    travelled = elapsed * contact["speed_mps"]
    wps = contact["waypoints"]
    for i in range(len(wps) - 1):
        seg = _dist(wps[i], wps[i + 1])
        if travelled <= seg:
            f = travelled / seg if seg else 0.0
            return [wps[i][k] + (wps[i + 1][k] - wps[i][k]) * f for k in range(3)]
        travelled -= seg
    return None


def range_at(contact, t):
    pos = position_at(contact, t)
    if pos is None:
        return None
    return math.sqrt(pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2)


def ends_inside(contact, inner_ring_m):
    """True if the path finishes inside the inner ring, which is a breach for a hostile."""
    last = contact["waypoints"][-1]
    return math.hypot(last[0], last[2]) <= inner_ring_m


def first_time_within(contact, range_m, step=0.5):
    """First scenario time the contact is within range_m of the post, or None."""
    t = contact["spawn_t"]
    stop = end_time(contact)
    while t <= stop:
        r = range_at(contact, t)
        if r is not None and r <= range_m:
            return t
        t += step
    return None
