"""Tests for 04 · Sinusoidal positional encoding.

Run from the paper folder: python3.9 -m pytest exercises/04_positional_encoding
"""
import math

import torch

from _load import load

impl = load("04_positional_encoding")


def test_table_shape_and_range():
    pe = impl.sinusoidal_positional_encoding(50, 16)
    assert pe.shape == (50, 16), "one row per position, one column per dimension"
    assert pe.abs().max() <= 1.0 + 1e-6, "sines and cosines stay within [-1, 1]"


def test_position_zero_is_all_sin0_cos0():
    pe = impl.sinusoidal_positional_encoding(4, 8)
    torch.testing.assert_close(
        pe[0], torch.tensor([0.0, 1.0] * 4),
        msg="at pos 0 every sine is 0 and every cosine is 1: even dims are sin, odd dims are cos",
    )


def test_hand_computed_values():
    d_model = 8
    pe = impl.sinusoidal_positional_encoding(10, d_model)
    for pos in [1, 7]:
        for i in range(d_model // 2):
            angle = pos / 10000 ** (2 * i / d_model)
            torch.testing.assert_close(
                pe[pos, 2 * i], torch.tensor(math.sin(angle)),
                msg="PE[%d, %d] should be sin(%d / 10000^(%d/%d))" % (pos, 2 * i, pos, 2 * i, d_model),
            )
            torch.testing.assert_close(pe[pos, 2 * i + 1], torch.tensor(math.cos(angle)))


def test_fixed_offset_is_a_rotation_independent_of_position():
    # §3.5: PE[pos + k] is a linear function of PE[pos]. For each (sin, cos) pair it is a 2x2 rotation
    # by angle k * w_i, the same matrix for every pos.
    d_model, k = 8, 3
    pe = impl.sinusoidal_positional_encoding(40, d_model).double()
    for i in range(d_model // 2):
        theta = k / 10000 ** (2 * i / d_model)
        rotation = torch.tensor(
            [[math.cos(theta), math.sin(theta)], [-math.sin(theta), math.cos(theta)]], dtype=torch.float64
        )
        pair = pe[:, 2 * i: 2 * i + 2]  # rows are (sin, cos)
        torch.testing.assert_close(pair[k:], pair[:-k] @ rotation.T, rtol=1e-4, atol=1e-5)


def test_module_adds_encoding_and_has_no_parameters():
    module = impl.PositionalEncoding(d_model=8, dropout=0.0, max_len=20)
    assert len(list(module.parameters())) == 0, "positional encodings are fixed: register a buffer, not a Parameter"
    assert "pe" in dict(module.named_buffers()), "store the table as a buffer named `pe`"
    x = torch.zeros(2, 5, 8)
    torch.testing.assert_close(module(x), impl.sinusoidal_positional_encoding(20, 8)[:5].expand(2, 5, 8))
