"""Tests for 02 · Multi-head attention.

Run from the paper folder: python3.9 -m pytest exercises/02_multi_head_attention
"""
import pytest
import torch

from _load import load

impl = load("02_multi_head_attention")
reference_attention = load("01_scaled_dot_product_attention").scaled_dot_product_attention


def test_output_and_weight_shapes():
    torch.manual_seed(0)
    mha = impl.MultiHeadAttention(d_model=16, h=4)
    q, kv = torch.randn(2, 3, 16), torch.randn(2, 5, 16)
    out = mha(q, kv, kv)
    assert out.shape == (2, 3, 16), "output should be (batch, n_q, d_model)"
    assert mha.last_weights is not None and mha.last_weights.shape == (2, 4, 3, 5), (
        "last_weights should be (batch, h, n_q, n_k)"
    )


def test_projections_are_bias_free_matrices():
    mha = impl.MultiHeadAttention(d_model=16, h=4)
    for name in ["w_q", "w_k", "w_v", "w_o"]:
        layer = getattr(mha, name)
        assert isinstance(layer, torch.nn.Linear), name + " should be an nn.Linear"
        assert layer.weight.shape == (16, 16), name + " should map d_model -> d_model (all heads stacked)"
        assert layer.bias is None, "the paper's projections are plain matrices W, with no bias"
    assert sum(p.numel() for p in mha.parameters()) == 4 * 16 * 16


def test_rejects_d_model_not_divisible_by_h():
    with pytest.raises(ValueError):
        impl.MultiHeadAttention(d_model=10, h=4)


def test_equals_h_independent_heads_concatenated():
    torch.manual_seed(0)
    d_model, h = 12, 3
    d_k = d_model // h
    mha = impl.MultiHeadAttention(d_model, h)
    x, memory = torch.randn(2, 4, d_model), torch.randn(2, 6, d_model)
    heads = []
    for i in range(h):
        rows = slice(i * d_k, (i + 1) * d_k)  # head i owns these output features of each projection
        w_q, w_k, w_v = mha.w_q.weight[rows], mha.w_k.weight[rows], mha.w_v.weight[rows]
        head, _ = reference_attention(x @ w_q.T, memory @ w_k.T, memory @ w_v.T)
        heads.append(head)
    expected = torch.cat(heads, dim=-1) @ mha.w_o.weight.T
    torch.testing.assert_close(
        mha(x, memory, memory), expected,
        msg="output should equal Concat(head_1..head_h) W^O, with head i using features i*d_k:(i+1)*d_k",
    )


def test_mask_applies_to_every_head():
    torch.manual_seed(0)
    mha = impl.MultiHeadAttention(d_model=8, h=2)
    x = torch.randn(1, 4, 8)
    mask = torch.tril(torch.ones(1, 4, 4, dtype=torch.bool))
    mha(x, x, x, mask=mask)
    assert torch.all(mha.last_weights[:, :, ~mask[0]] == 0), "every head must respect the mask"


def test_matches_pytorch_builtin():
    torch.manual_seed(0)
    d_model, h = 16, 4
    ours = impl.MultiHeadAttention(d_model, h)
    ref = torch.nn.MultiheadAttention(d_model, h, bias=False, batch_first=True)
    with torch.no_grad():
        ref.in_proj_weight.copy_(torch.cat([ours.w_q.weight, ours.w_k.weight, ours.w_v.weight]))
        ref.out_proj.weight.copy_(ours.w_o.weight)
    q, kv = torch.randn(2, 3, d_model), torch.randn(2, 5, d_model)
    expected, _ = ref(q, kv, kv, need_weights=False)
    torch.testing.assert_close(ours(q, kv, kv), expected, rtol=1e-4, atol=1e-5)
