"""Full control plan: GA -> fuzzy adjustment -> safety rules -> baseline comparison."""
from config import *
from ga import optimize, fitness
from fuzzy import adjust


def _clamp(x):
    return max(MIN_G, min(MAX_G, round(x)))


def plan(counts, prev_counts=None, emergency_lane=None, seed=None):
    prev = prev_counts or counts
    g = optimize(counts, seed)
    g = [_clamp(gi + adjust(c, p)) for gi, c, p in zip(g, counts, prev)]

    if emergency_lane is not None:                     # rule-based priority override
        g = [MAX_G if i == emergency_lane else MIN_G for i in range(len(g))]

    # starvation guard: shrink the longest greens until every red <= MAX_WAIT
    while max(sum(x + YELLOW + ALL_RED for x in g) - gi for gi in g) > MAX_WAIT:
        j = max(range(len(g)), key=lambda k: g[k])
        if g[j] <= MIN_G:
            break
        g[j] -= 1

    base = [30] * len(counts)
    f_ad, f_base = fitness(g, counts), fitness(base, counts)
    return {
        "green_times": g,
        "cycle_time": sum(x + YELLOW + ALL_RED for x in g),
        "counts": counts,
        "improvement_pct": round(100 * (f_base - f_ad) / f_base, 1) if f_base else 0.0,
    }


if __name__ == "__main__":
    print(plan([18, 4, 9, 2], [10, 5, 9, 3], seed=1))
    print(plan([18, 4, 9, 2], emergency_lane=1, seed=1))
