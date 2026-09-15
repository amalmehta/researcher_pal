"""Tests for 06 · Residual connection, dropout and LayerNorm.

Run from the paper folder: python3.9 -m pytest exercises/06_sublayer_connection
"""
import torch
import torch.nn.functional as F

from _load import load

impl = load("06_sublayer_connection")


def test_shape_and_submodules():
    block = impl.SublayerConnection(6)
    assert isinstance(block.norm, torch.nn.LayerNorm) and isinstance(block.dropout, torch.nn.Dropout)
    assert block(torch.randn(2, 3, 6), lambda t: t).shape == (2, 3, 6)


def test_post_norm_order():
    torch.manual_seed(0)
    block = impl.SublayerConnection(6)
    x = torch.randn(2, 3, 6)

    def sublayer(t):
        return 3 * t + 1

    expected = F.layer_norm(x + sublayer(x), (6,))
    torch.testing.assert_close(
        block(x, sublayer), expected,
        msg="the paper normalizes after the residual add: LayerNorm(x + Sublayer(x)), not x + Sublayer(LayerNorm(x))",
    )


def test_output_is_normalized_per_position():
    torch.manual_seed(0)
    block = impl.SublayerConnection(6)
    out = block(torch.randn(2, 3, 6) * 10 + 4, lambda t: t)
    torch.testing.assert_close(
        out.mean(-1), torch.zeros(2, 3), rtol=0, atol=1e-5,
        msg="LayerNorm is the last operation, so each position's features should have mean 0",
    )


def test_dropout_hits_the_sublayer_branch_not_the_residual():
    torch.manual_seed(0)
    block = impl.SublayerConnection(6, dropout=1.0).train()
    x = torch.randn(2, 3, 6)
    torch.testing.assert_close(
        block(x, lambda t: 5 * t), F.layer_norm(x, (6,)),
        msg="with dropout=1 the sub-layer output is zeroed, leaving LayerNorm(x): dropout goes on Sublayer(x) before the add",
    )


def test_dropout_is_off_in_eval_mode():
    torch.manual_seed(0)
    block = impl.SublayerConnection(6, dropout=0.5).eval()
    x = torch.randn(2, 3, 6)
    torch.testing.assert_close(block(x, lambda t: 2 * t), F.layer_norm(3 * x, (6,)))
