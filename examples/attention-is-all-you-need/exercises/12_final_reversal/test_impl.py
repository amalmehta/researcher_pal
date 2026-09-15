"""Tests for 12 · Final: a small Transformer learns to reverse sequences.

Run from the paper folder: python3.9 -m pytest exercises/12_final_reversal
"""
import pytest
import torch

from _load import load

impl = load("12_final_reversal")
Transformer = load("09_transformer").Transformer
subsequent_mask = load("08_decoder_layer").subsequent_mask


def untrained_model():
    torch.manual_seed(0)
    return Transformer(impl.VOCAB_SIZE, d_model=16, h=2, d_ff=32, N=1, dropout=0.0, max_len=impl.SEQ_LEN + 1).eval()


def test_greedy_decode_shape_and_tokens():
    model = untrained_model()
    src = torch.randint(impl.FIRST_DIGIT, impl.VOCAB_SIZE, (3, impl.SEQ_LEN))
    out = impl.greedy_decode(model, src)
    assert out.shape == (3, impl.SEQ_LEN), "one generated token per target position, with the BOS removed"
    assert out.dtype == torch.long and ((out >= 0) & (out < impl.VOCAB_SIZE)).all()


def test_greedy_decode_agrees_with_teacher_forcing_on_its_own_output():
    model = untrained_model()
    src = torch.randint(impl.FIRST_DIGIT, impl.VOCAB_SIZE, (4, impl.SEQ_LEN))
    out = impl.greedy_decode(model, src)
    tgt_in = torch.cat([torch.full((4, 1), impl.BOS, dtype=torch.long), out[:, :-1]], dim=1)
    with torch.no_grad():
        teacher_forced = model(src, tgt_in, tgt_mask=subsequent_mask(impl.SEQ_LEN)).argmax(-1)
    assert torch.equal(teacher_forced, out), (
        "feeding the generated tokens back in one pass (with the causal mask) must reproduce each greedy choice"
    )


@pytest.fixture(scope="module")
def results():
    return impl.train_and_evaluate(seed=0)


def test_learns_to_reverse_unseen_sequences(results):
    assert results["accuracy"] >= 0.9, "expected >= 90%% exact reversals, got %.1f%%" % (100 * results["accuracy"])


def test_encoder_decoder_attention_discovers_the_alignment(results):
    assert results["alignment"] >= 0.8, (
        "some encoder-decoder head should attend to the source token being copied (anti-diagonal); got %.2f"
        % results["alignment"]
    )


def test_trains_on_cpu_in_under_5_minutes(results):
    assert results["seconds"] < 300, "took %.0f s" % results["seconds"]
