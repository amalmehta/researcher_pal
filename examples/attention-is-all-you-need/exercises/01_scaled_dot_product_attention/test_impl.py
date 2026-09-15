"""Tests for 01 · Scaled dot-product attention.

Run from the paper folder: python3.9 -m pytest exercises/01_scaled_dot_product_attention
"""
import math

import pytest
import torch

from _load import load

impl = load("01_scaled_dot_product_attention")


def test_output_shapes():
    torch.manual_seed(0)
    q, k, v = torch.randn(2, 3, 4), torch.randn(2, 5, 4), torch.randn(2, 5, 6)
    out, w = impl.scaled_dot_product_attention(q, k, v)
    assert out.shape == (2, 3, 6), "output should have one row per query and the values' size d_v"
    assert w.shape == (2, 3, 5), "weights should be (batch, n_q, n_k): one weight per query-key pair"


def test_each_query_weights_sum_to_one():
    torch.manual_seed(0)
    q, k, v = torch.randn(2, 3, 4), torch.randn(2, 5, 4), torch.randn(2, 5, 4)
    _, w = impl.scaled_dot_product_attention(q, k, v)
    torch.testing.assert_close(
        w.sum(-1), torch.ones(2, 3),
        msg="each query's weights should sum to 1: did you softmax over the keys axis?",
    )
    assert (w >= 0).all(), "attention weights come out of a softmax, so they can't be negative"


def test_hand_computed_example():
    # One query [1, 0]; keys [1, 0] and [0, 1]; d_k = 2.
    # Scores = [1/sqrt(2), 0], so w0 = e^(1/sqrt2) / (e^(1/sqrt2) + 1).
    q = torch.tensor([[1.0, 0.0]])
    k = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    v = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    out, w = impl.scaled_dot_product_attention(q, k, v)
    w0 = math.exp(1 / math.sqrt(2)) / (math.exp(1 / math.sqrt(2)) + 1)
    torch.testing.assert_close(w, torch.tensor([[w0, 1 - w0]]))
    torch.testing.assert_close(out, torch.tensor([[w0 * 1 + (1 - w0) * 3, w0 * 2 + (1 - w0) * 4]]))


def test_scores_are_divided_by_sqrt_dk():
    # d_k = 4: raw scores are [4, 0]; after dividing by sqrt(4) they are [2, 0].
    q = torch.ones(1, 4)
    k = torch.stack([torch.ones(4), torch.zeros(4)])
    v = torch.eye(2)
    _, w = impl.scaled_dot_product_attention(q, k, v)
    expected = math.exp(2) / (math.exp(2) + 1)
    torch.testing.assert_close(
        w[0, 0], torch.tensor(expected),
        msg="weight on key 0 should be softmax([4, 0] / sqrt(4))[0]: did you divide by sqrt(d_k)?",
    )


def test_masked_keys_get_zero_weight():
    torch.manual_seed(0)
    q, k, v = torch.randn(1, 3, 4), torch.randn(1, 3, 4), torch.randn(1, 3, 4)
    causal = torch.tril(torch.ones(3, 3, dtype=torch.bool))
    out, w = impl.scaled_dot_product_attention(q, k, v, mask=causal)
    assert torch.all(w[0][~causal] == 0), (
        "masked positions must get exactly zero weight: set their scores to -inf before the softmax"
    )
    torch.testing.assert_close(w.sum(-1), torch.ones(1, 3), msg="unmasked weights should still sum to 1")
    # The first query may only see the first key, so its output is exactly the first value.
    torch.testing.assert_close(out[0, 0], v[0, 0])


def test_permuting_keys_and_values_together_changes_nothing():
    torch.manual_seed(0)
    q, k, v = torch.randn(2, 4), torch.randn(5, 4), torch.randn(5, 3)
    perm = torch.randperm(5)
    out1, _ = impl.scaled_dot_product_attention(q, k, v)
    out2, _ = impl.scaled_dot_product_attention(q, k[perm], v[perm])
    torch.testing.assert_close(out1, out2, msg="attention is a weighted sum over a set: key order must not matter")


def test_matches_pytorch_builtin():
    F = torch.nn.functional
    if not hasattr(F, "scaled_dot_product_attention"):
        pytest.skip("this PyTorch version has no F.scaled_dot_product_attention")
    torch.manual_seed(0)
    q, k, v = torch.randn(2, 8, 3, 16), torch.randn(2, 8, 5, 16), torch.randn(2, 8, 5, 16)
    mask = torch.rand(2, 1, 3, 5) > 0.3
    mask[..., 0] = True  # every query can see at least one key
    out, _ = impl.scaled_dot_product_attention(q, k, v, mask=mask)
    torch.testing.assert_close(out, F.scaled_dot_product_attention(q, k, v, attn_mask=mask), rtol=1e-4, atol=1e-5)
