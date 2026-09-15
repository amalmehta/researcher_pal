"""Tests for 07 · Encoder layer and stack.

Run from the paper folder: python3.9 -m pytest exercises/07_encoder_layer
"""
import torch

from _load import load

impl = load("07_encoder_layer")


def make_layer():
    torch.manual_seed(0)
    return impl.EncoderLayer(d_model=16, h=4, d_ff=32, dropout=0.0).eval()


def test_layer_shape():
    assert make_layer()(torch.randn(2, 5, 16)).shape == (2, 5, 16)


def test_layer_is_attention_sublayer_then_ffn_sublayer():
    layer = make_layer()
    x = torch.randn(2, 5, 16)
    mask = torch.ones(1, 1, 5, dtype=torch.bool)
    expected = layer.sublayer2(layer.sublayer1(x, lambda t: layer.self_attn(t, t, t, mask)), layer.ffn)
    torch.testing.assert_close(
        layer(x, mask), expected,
        msg="an encoder layer is self-attention (Q = K = V = x) wrapped in sublayer1, then the FFN wrapped in sublayer2",
    )


def test_stack_has_n_layers_with_separate_weights():
    torch.manual_seed(0)
    encoder = impl.Encoder(d_model=16, h=4, d_ff=32, N=3)
    assert len(encoder.layers) == 3
    w0 = encoder.layers[0].ffn.linear1.weight
    w1 = encoder.layers[1].ffn.linear1.weight
    assert w0.data_ptr() != w1.data_ptr(), "layers must not share weights: create a new EncoderLayer for each"
    one_layer = sum(p.numel() for p in encoder.layers[0].parameters())
    assert sum(p.numel() for p in encoder.parameters()) == 3 * one_layer


def test_stack_applies_layers_in_order():
    torch.manual_seed(0)
    encoder = impl.Encoder(d_model=16, h=4, d_ff=32, N=3).eval()
    x = torch.randn(2, 5, 16)
    expected = encoder.layers[2](encoder.layers[1](encoder.layers[0](x)))
    torch.testing.assert_close(encoder(x), expected)


def test_encoder_without_positions_is_permutation_equivariant():
    torch.manual_seed(0)
    encoder = impl.Encoder(d_model=16, h=4, d_ff=32, N=2).eval()
    x = torch.randn(1, 6, 16)
    perm = torch.tensor([3, 0, 5, 1, 4, 2])
    torch.testing.assert_close(
        encoder(x[:, perm]), encoder(x)[:, perm], rtol=1e-4, atol=1e-5,
        msg="with no positional encoding, shuffling input positions should just shuffle the outputs (§3.5 motivation)",
    )


def test_padding_mask_hides_padded_positions():
    torch.manual_seed(0)
    encoder = impl.Encoder(d_model=16, h=4, d_ff=32, N=2).eval()
    x = torch.randn(1, 5, 16)
    mask = torch.tensor([[[True, True, True, False, False]]])  # last two positions are padding
    x_changed = x.clone()
    x_changed[:, 3:] = torch.randn(1, 2, 16)
    torch.testing.assert_close(
        encoder(x, mask)[:, :3], encoder(x_changed, mask)[:, :3],
        msg="real tokens must not be affected by what's in padded positions",
    )
