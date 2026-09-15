"""01 · Preferential attachment. See README.md and ¶8, E4 of the paper."""
import numpy as np


def attachment_probabilities(degrees):
    """Pi(k_i) = k_i / sum_j k_j.

    Args:
        degrees: 1-D int array of current degrees, not all zero

    Returns:
        1-D float array of the same length, summing to 1
    """
    degrees = np.asarray(degrees, dtype=float)
    # sum_j k_j = 2E: every edge contributes to two degrees.
    return degrees / degrees.sum()


def choose_targets(degrees, m, rng):
    """Pick m different vertices, each draw proportional to degree among the vertices not yet picked.

    Args:
        degrees: 1-D int array of current degrees
        m: number of distinct targets
        rng: numpy.random.Generator

    Returns:
        1-D int array of m distinct vertex indices

    Raises:
        ValueError: if fewer than m vertices have a nonzero degree
    """
    degrees = np.asarray(degrees)
    available = np.count_nonzero(degrees)
    if available < m:
        raise ValueError("need %d vertices with nonzero degree, only %d have edges" % (m, available))
    # Without replacement and with p, NumPy draws targets one at a time and renormalizes p over the
    # vertices not yet chosen, which is the standard reading of "m different vertices" (not in paper).
    return rng.choice(len(degrees), size=m, replace=False, p=attachment_probabilities(degrees))
