"""Sugeno-style fuzzy controller: adjusts a lane's green time (seconds)."""
from config import MAX_VEH


def trap(x, a, b, c, d):
    if b <= x <= c:
        return 1.0
    if x <= a or x >= d:
        return 0.0
    return (x - a) / (b - a) if x < b else (d - x) / (d - c)


DENSITY = {"low": (-1, -1, 0.2, 0.5), "med": (0.2, 0.5, 0.5, 0.8), "high": (0.5, 0.8, 2, 2)}
GROWTH = {"down": (-2, -2, -0.3, 0), "stable": (-0.3, 0, 0, 0.3), "up": (0, 0.3, 2, 2)}

# (density, growth) -> adjustment in seconds
RULES = {
    ("high", "up"): 15, ("high", "stable"): 8, ("high", "down"): 3,
    ("med", "up"): 6, ("med", "stable"): 0, ("med", "down"): -3,
    ("low", "up"): -3, ("low", "stable"): -8, ("low", "down"): -8,
}


def adjust(count, prev_count):
    d = min(1.0, count / MAX_VEH)
    gr = max(-1.0, min(1.0, (count - prev_count) / MAX_VEH * 2))
    num = den = 0.0
    for (dl, gl), out in RULES.items():
        w = min(trap(d, *DENSITY[dl]), trap(gr, *GROWTH[gl]))   # AND = min
        num += w * out
        den += w
    return num / den if den else 0.0
