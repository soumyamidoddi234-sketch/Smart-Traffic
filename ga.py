"""Genetic algorithm for green-time optimization."""
import random
from config import *


def fitness(g, counts):
    """Lower is better: weighted waiting + unserved vehicles + starvation penalty."""
    cycle = sum(x + YELLOW + ALL_RED for x in g)
    cost = 0.0
    for gi, n in zip(g, counts):
        red = cycle - gi
        unserved = max(0.0, n - gi * SAT_FLOW)
        cost += n * red + 5 * unserved * cycle
        if red > MAX_WAIT:
            cost += 1000 * (red - MAX_WAIT)
    return cost


def _clamp(x):
    return max(MIN_G, min(MAX_G, x))


def optimize(counts, seed=None):
    rng = random.Random(seed)
    n = len(counts)
    pop = [[rng.randint(MIN_G, MAX_G) for _ in range(n)] for _ in range(POP)]
    pop[0] = [_clamp(int(MIN_G + (MAX_G - MIN_G) * c / MAX_VEH)) for c in counts]  # heuristic seed
    for _ in range(GENS):
        pop.sort(key=lambda g: fitness(g, counts))
        nxt = [g[:] for g in pop[:ELITE]]
        while len(nxt) < POP:
            p1 = min(rng.sample(pop, TOURN_K), key=lambda g: fitness(g, counts))
            p2 = min(rng.sample(pop, TOURN_K), key=lambda g: fitness(g, counts))
            cut = rng.randint(1, n - 1)
            child = p1[:cut] + p2[cut:]
            child = [_clamp(x + rng.choice([-MUT_STEP, MUT_STEP])) if rng.random() < MUT_RATE else x
                     for x in child]
            nxt.append(child)
        pop = nxt
    return min(pop, key=lambda g: fitness(g, counts))
