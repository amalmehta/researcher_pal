"""Tests for 08 · Decoder layer, causal mask and stack.

Run from the paper folder: python3.9 -m pytest exercises/08_decoder_layer
"""
import torch

from _load import load

impl = load("08_decoder_layer")


def make_decoder(N=2):
    torch.manual_seed(0)
    return impl.Decoder(d_model=16, h=4, d_ff=32, N=N, dropout=0.0).eval()


def test_subsequent_mask_values():
    mask = impl.subsequent_mask(4)
    assert mask.dtype == torch.bool and mask.shape == (1, 4, 4)
    expected = torch.tensor([[
        [True, False, False, False],
        [True, True, False, False],
        [True, True, True, False],
        [True, True, True, True],
    ]])
    assert torch.equal(mask, expected), "position i may attend to j <= i: lower triangle including the diagonal"


def test_shapes_with_different_source_and_target_lengths():
    torch.manual_seed(0)
    layer = impl.DecoderLayer(d_model=16, h=4, d_ff=32).eval()
    x, memory = torch.randn(2, 5, 16), torch.randn(2, 7, 16)
    out = layer(x, memory, tgt_mask=impl.subsequent_mask(5))
    assert out.shape == (2, 5, 16), "one output per target position"
    assert layer.cross_attn.last_weights.shape == (2, 4, 5, 7), (
        "encoder-decoder attention weights should be (batch, h, n_tgt, n_src): queries from the decoder, keys from memory"
    )


def test_layer_is_three_sublayers_in_order():
    torch.manual_seed(0)
    layer = impl.DecoderLayer(d_model=16, h=4, d_ff=32).eval()
    x, memory = torch.randn(2, 5, 16), torch.randn(2, 7, 16)
    tgt_mask = impl.subsequent_mask(5)
    a = layer.sublayer1(x, lambda t: layer.self_attn(t, t, t, tgt_mask))
    b = layer.sublayer2(a, lambda t: layer.cross_attn(t, memory, memory, None))
    expected = layer.sublayer3(b, layer.ffn)
    torch.testing.assert_close(layer(x, memory, tgt_mask=tgt_mask), expected)


def test_future_target_positions_cannot_leak():
    decoder = make_decoder()
    x, memory = torch.randn(1, 6, 16), torch.randn(1, 4, 16)
    x_changed = x.clone()
    x_changed[:, 3:] = torch.randn(1, 3, 16)  # change positions 3, 4, 5
    mask = impl.subsequent_mask(6)
    torch.testing.assert_close(
        decoder(x, memory, tgt_mask=mask)[:, :3], decoder(x_changed, memory, tgt_mask=mask)[:, :3],
        msg="outputs at positions 0-2 must not depend on target positions 3-5 (causal mask in self-attention)",
    )


def test_decoder_reads_the_memory():
    decoder = make_decoder()
    x = torch.randn(1, 3, 16)
    mask = impl.subsequent_mask(3)
    out1 = decoder(x, torch.randn(1, 4, 16), tgt_mask=mask)
    out2 = decoder(x, torch.randn(1, 4, 16), tgt_mask=mask)
    assert not torch.allclose(out1, out2), "a different source (memory) must change the decoder output"


def test_source_padding_is_ignored():
    decoder = make_decoder()
    x, memory = torch.randn(1, 3, 16), torch.randn(1, 5, 16)
    src_mask = torch.tensor([[[True, True, True, False, False]]])
    memory_changed = memory.clone()
    memory_changed[:, 3:] = torch.randn(1, 2, 16)
    mask = impl.subsequent_mask(3)
    torch.testing.assert_close(
        decoder(x, memory, src_mask, mask), decoder(x, memory_changed, src_mask, mask),
        msg="padded source positions must be invisible to encoder-decoder attention",
    )


def test_stack_has_separate_layers():
    decoder = make_decoder(N=3)
    assert len(decoder.layers) == 3
    ptrs = {layer.cross_attn.w_q.weight.data_ptr() for layer in decoder.layers}
    assert len(ptrs) == 3, "each decoder layer needs its own weights"
