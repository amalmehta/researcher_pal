"""Tests for 09 · The full Transformer.

Run from the paper folder: python3.9 -m pytest exercises/09_transformer
"""
import torch

from _load import load

impl = load("09_transformer")
subsequent_mask = load("08_decoder_layer").subsequent_mask

VOCAB = 20


def small_model():
    torch.manual_seed(0)
    return impl.Transformer(VOCAB, d_model=16, h=4, d_ff=32, N=2, dropout=0.0, max_len=50).eval()


def test_logits_shape():
    model = small_model()
    src = torch.randint(0, VOCAB, (2, 7))
    tgt = torch.randint(0, VOCAB, (2, 5))
    assert model(src, tgt, tgt_mask=subsequent_mask(5)).shape == (2, 5, VOCAB), "logits are (batch, n_tgt, vocab)"


def test_three_way_weight_tying():
    model = small_model()
    shared = model.src_embed.lut.weight
    assert model.tgt_embed.lut.weight is shared, "§3.4: both embedding layers share one weight matrix"
    assert model.generator.weight is shared, "§3.4: the pre-softmax projection shares the embedding matrix too"
    assert model.generator.bias is None


def test_logits_are_decoder_output_times_embedding_transpose():
    model = small_model()
    src, tgt = torch.randint(0, VOCAB, (2, 7)), torch.randint(0, VOCAB, (2, 5))
    mask = subsequent_mask(5)
    hidden = model.decode(model.encode(src), tgt, tgt_mask=mask)
    torch.testing.assert_close(model(src, tgt, tgt_mask=mask), hidden @ model.src_embed.lut.weight.T)


def test_logits_are_causal():
    model = small_model()
    src = torch.randint(0, VOCAB, (1, 6))
    tgt = torch.randint(0, VOCAB, (1, 5))
    tgt_changed = tgt.clone()
    tgt_changed[:, 3:] = (tgt[:, 3:] + 1) % VOCAB
    mask = subsequent_mask(5)
    torch.testing.assert_close(
        model(src, tgt, tgt_mask=mask)[:, :3], model(src, tgt_changed, tgt_mask=mask)[:, :3],
        msg="predictions for positions 0-2 must not see target tokens 3-4",
    )


def test_source_padding_is_ignored():
    model = small_model()
    src = torch.randint(1, VOCAB, (1, 6))
    src_changed = src.clone()
    src_changed[:, 4:] = 0
    src_mask = torch.tensor([[[True, True, True, True, False, False]]])
    tgt = torch.randint(0, VOCAB, (1, 4))
    mask = subsequent_mask(4)
    torch.testing.assert_close(
        model(src, tgt, src_mask, mask), model(src_changed, tgt, src_mask, mask),
        msg="with a source padding mask, the padded tokens can't affect the logits",
    )


def test_base_config_parameter_count_close_to_table_3():
    model = impl.Transformer(37000, d_model=512, h=8, d_ff=2048, N=6, dropout=0.1)
    n = sum(p.numel() for p in model.parameters())  # shared weights counted once
    assert 60e6 < n < 66e6, (
        "base model should have roughly Table 3's 65M parameters with a ~37k shared vocabulary; got %.1fM" % (n / 1e6)
    )
