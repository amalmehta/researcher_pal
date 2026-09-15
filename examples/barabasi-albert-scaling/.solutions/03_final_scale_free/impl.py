"""03 · Final: grow the network and measure its scaling. See README.md and ¶8–¶10 of the paper."""
import numpy as np

from _load import load

# Your work from exercise 01.
choose_targets = load("01_preferential_attachment").choose_targets


# ---- Provided: measurement tools (not from the paper) -----------------------------------------
def fit_power_law_exponent(degrees, k_min):
    """Maximum-likelihood gamma for the tail k >= k_min of integer data, using the standard continuous
    approximation gamma = 1 + n / sum(ln(k / (k_min - 1/2))) (Clauset, Shalizi & Newman 2009).
    The paper read slopes off log-log plots instead."""
    tail = np.asarray(degrees, dtype=float)
    tail = tail[tail >= k_min]
    return 1.0 + len(tail) / np.log(tail / (k_min - 0.5)).sum()


def growth_exponent(degrees, m0, t_min=10):
    """Log-log slope of mean degree against arrival time t_i (1 = first added vertex), over
    log-spaced bins with t_i >= t_min. k_i(t) = m (t / t_i)^(1/2) predicts -0.5."""
    degrees = np.asarray(degrees)
    t_i = np.arange(len(degrees)) - m0 + 1
    keep = t_i >= t_min
    t_i, k = t_i[keep], degrees[keep]
    edges = np.unique(np.logspace(np.log10(t_min), np.log10(t_i.max() + 1), 15).astype(int))
    xs, ys = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        in_bin = (t_i >= lo) & (t_i < hi)
        if in_bin.any():
            xs.append(np.log(t_i[in_bin].mean()))
            ys.append(np.log(k[in_bin].mean()))
    return np.polyfit(xs, ys, 1)[0]


# ---- Your part ---------------------------------------------------------------------------------
def grow_network(t, m, m0, rng, preferential=True):
    """Grow the network for t steps and return every vertex's final degree.

    Start: m0 vertices joined as a complete graph (not in paper). Each step adds one vertex with m
    edges to m different existing vertices, chosen with choose_targets (preferential=True) or
    uniformly at random (preferential=False, model A).

    Args:
        t: number of steps; m: edges per new vertex (m <= m0); m0: starting vertices (>= 2)
        rng: numpy.random.Generator
        preferential: True for the paper's model, False for model A

    Returns:
        1-D int array of length m0 + t, in arrival order
    """
    if not 1 <= m <= m0 or m0 < 2:
        raise ValueError("need 1 <= m <= m0 and m0 >= 2")
    degrees = np.zeros(m0 + t, dtype=np.int64)
    # The paper doesn't say how the m0 starting vertices are connected. With no edges, every
    # Pi(k) would be 0/0 on the first step, so start from a complete graph.
    degrees[:m0] = m0 - 1
    for step in range(t):
        n = m0 + step  # vertices already present; the newcomer gets index n
        if preferential:
            targets = choose_targets(degrees[:n], m, rng)   # Pi(k_i) = k_i / sum_j k_j
        else:
            targets = rng.choice(n, size=m, replace=False)  # model A: Pi = 1 / (m0 + t - 1)
        degrees[targets] += 1
        degrees[n] = m
    return degrees


def simulate_and_measure(seed=0, t=20000, m=5, m0=5):
    """Grow the model and model A with one numpy.random.default_rng(seed), then measure.

    Returns a dict:
        gamma:         fit_power_law_exponent(model degrees, k_min=20)
        growth_slope:  growth_exponent(model degrees, m0)
        max_degree_ba: largest degree in the model
        max_degree_a:  largest degree in model A
    """
    rng = np.random.default_rng(seed)
    model = grow_network(t, m, m0, rng, preferential=True)
    model_a = grow_network(t, m, m0, rng, preferential=False)
    return {
        "gamma": fit_power_law_exponent(model, k_min=20),
        "growth_slope": growth_exponent(model, m0),
        "max_degree_ba": int(model.max()),
        "max_degree_a": int(model_a.max()),
    }
