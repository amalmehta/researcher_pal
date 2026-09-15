"""Tests for 01 · Preferential attachment.

Run from the paper folder: python3.9 -m pytest exercises/01_preferential_attachment
"""
import numpy as np
import pytest

from _load import load

impl = load("01_preferential_attachment")


def test_probabilities_hand_computed():
    np.testing.assert_allclose(
        impl.attachment_probabilities(np.array([1, 2, 3, 4])), [0.1, 0.2, 0.3, 0.4],
        err_msg="Pi(k_i) = k_i / sum_j k_j: degrees 1..4 sum to 10",
    )


def test_probabilities_sum_to_one_and_isolated_vertices_get_zero():
    p = impl.attachment_probabilities(np.array([0, 5, 1, 0, 2]))
    assert p.shape == (5,)
    assert np.isclose(p.sum(), 1.0), "probabilities must sum to 1"
    assert p[0] == 0 and p[3] == 0, "a vertex with no edges can't attract new ones"


def test_targets_are_distinct_valid_indices():
    rng = np.random.default_rng(0)
    degrees = np.array([3, 1, 4, 1, 5, 9, 2, 6])
    for _ in range(200):
        targets = impl.choose_targets(degrees, 3, rng)
        assert len(targets) == 3 and len(set(targets.tolist())) == 3, "the paper links to m *different* vertices"
        assert all(0 <= i < len(degrees) for i in targets)


def test_isolated_vertices_are_never_chosen():
    rng = np.random.default_rng(1)
    degrees = np.array([0, 2, 0, 7, 1])
    chosen = np.concatenate([impl.choose_targets(degrees, 2, rng) for _ in range(500)])
    assert not np.isin(chosen, [0, 2]).any(), "vertices 0 and 2 have degree 0"


def test_single_draw_frequencies_follow_degrees():
    rng = np.random.default_rng(2)
    degrees = np.array([1, 2, 3, 4])
    picks = [impl.choose_targets(degrees, 1, rng)[0] for _ in range(20000)]
    np.testing.assert_allclose(
        np.bincount(picks, minlength=4) / 20000, [0.1, 0.2, 0.3, 0.4], atol=0.015,
        err_msg="with m = 1, vertex i should be picked with probability k_i / sum_j k_j",
    )


def test_second_draw_is_renormalized_over_the_rest():
    # degrees [1, 1, 8], m = 2: P(vertex 0 is picked) = P(first) + P(second)
    # = 0.1 + 0.1 * (1/9) + 0.8 * (1/2) = 0.5111...
    rng = np.random.default_rng(3)
    degrees = np.array([1, 1, 8])
    hits = sum(0 in impl.choose_targets(degrees, 2, rng) for _ in range(20000))
    assert abs(hits / 20000 - (0.1 + 0.1 / 9 + 0.8 / 2)) < 0.02, (
        "after the first pick, choose the next target in proportion to the degrees of the vertices that are left"
    )


def test_raises_when_too_few_vertices_have_edges():
    with pytest.raises(ValueError):
        impl.choose_targets(np.array([0, 3, 0]), 2, np.random.default_rng(0))
