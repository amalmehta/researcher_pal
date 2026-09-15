"""Tests for 03 · Position-wise feed-forward network.

Run from the paper folder: python3.9 -m pytest exercises/03_position_wise_ffn
"""
import torch

from _load import load

impl = load("03_position_wise_ffn")


def test_shape_and_parameter_count():
    ffn = impl.PositionwiseFeedForward(d_model=8, d_ff=32)
    assert ffn(torch.randn(2, 5, 8)).shape == (2, 5, 8)
    expected = 8 * 32 + 32 + 32 * 8 + 8  # W_1, b_1, W_2, b_2
    assert sum(p.numel() for p in ffn.parameters()) == expected, "Eq. (2) has exactly W_1, b_1, W_2, b_2"


def test_matches_equation_2():
    torch.manual_seed(0)
    ffn = impl.PositionwiseFeedForward(6, 10)
    x = torch.randn(2, 3, 6)
    l1, l2 = ffn.linear1, ffn.linear2
    expected = torch.clamp(x @ l1.weight.T + l1.bias, min=0) @ l2.weight.T + l2.bias
    torch.testing.assert_close(ffn(x), expected, msg="output should be max(0, x W_1 + b_1) W_2 + b_2")


def test_positions_do_not_interact():
    torch.manual_seed(0)
    ffn = impl.PositionwiseFeedForward(6, 10)
    x = torch.randn(2, 3, 6)
    x_changed = x.clone()
    x_changed[:, 1] += 5.0
    out, out_changed = ffn(x), ffn(x_changed)
    torch.testing.assert_close(
        out[:, [0, 2]], out_changed[:, [0, 2]],
        msg="changing position 1 must not affect positions 0 and 2: the FFN sees one position at a time",
    )
    assert not torch.allclose(out[:, 1], out_changed[:, 1])


def test_relu_blocks_negative_hidden_units():
    torch.manual_seed(0)
    ffn = impl.PositionwiseFeedForward(4, 8)
    with torch.no_grad():
        ffn.linear1.bias.fill_(-1e3)  # every hidden unit is negative before the ReLU
    out = ffn(torch.randn(2, 3, 4))
    torch.testing.assert_close(
        out, ffn.linear2.bias.detach().expand(2, 3, 4),
        msg="with every hidden unit negative, max(0, .) gives 0 and only b_2 remains",
    )
