"""Tests for 03 · Final: grow the network and measure its scaling.

Run from the paper folder: python3.9 -m pytest exercises/03_final_scale_free
"""
import numpy as np
import pytest

from _load import load

impl = load("03_final_scale_free")


@pytest.mark.parametrize("preferential", [True, False])
def test_small_network_bookkeeping(preferential):
    rng = np.random.default_rng(0)
    degrees = impl.grow_network(50, 2, 3, rng, preferential=preferential)
    assert len(degrees) == 53, "after t steps there are t + m0 vertices"
    assert degrees.sum() == 2 * (3 + 2 * 50), (
        "sum of degrees = 2 x edges; edges = 3 in the complete graph on 3 vertices + m per step"
    )
    assert (degrees[3:] >= 2).all(), "every added vertex arrives with m edges"
    assert degrees.max() <= 52, "no vertex can have more distinct neighbours than there are other vertices"


def test_preferential_growth_uses_degree():
    # Many small runs: the first vertices should end up far richer than the last ones.
    rng = np.random.default_rng(1)
    runs = np.array([impl.grow_network(300, 2, 3, rng) for _ in range(5)])
    assert runs[:, :10].mean() > 4 * runs[:, -100:].mean(), "early vertices should accumulate links (rich get richer)"


@pytest.fixture(scope="module")
def results():
    return impl.simulate_and_measure(seed=0)


def test_degree_exponent_is_close_to_3(results):
    assert 2.7 <= results["gamma"] <= 3.3, "expected gamma near 3 (paper: 2.9 +/- 0.1), got %.2f" % results["gamma"]


def test_degree_grows_like_square_root_of_age(results):
    assert -0.6 <= results["growth_slope"] <= -0.4, (
        "k_i(t) = m (t / t_i)^(1/2) predicts slope -0.5 against arrival time, got %.2f" % results["growth_slope"]
    )


def test_uniform_attachment_has_no_hubs(results):
    assert results["max_degree_ba"] > 4 * results["max_degree_a"], (
        "model A should have no hubs: largest degree %d (model) vs %d (model A)"
        % (results["max_degree_ba"], results["max_degree_a"])
    )
