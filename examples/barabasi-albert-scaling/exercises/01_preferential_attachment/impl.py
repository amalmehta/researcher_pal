"""01 · Preferential attachment. See README.md and ¶8, E4 of the paper."""
import numpy as np


def attachment_probabilities(degrees):
    """Pi(k_i) = k_i / sum_j k_j.

    Args:
        degrees: 1-D int array of current degrees, not all zero

    Returns:
        1-D float array of the same length, summing to 1
    """
    raise NotImplementedError("TODO: implement E4")


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
    raise NotImplementedError("TODO: sample m distinct targets with probability proportional to degree")
