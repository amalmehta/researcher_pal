"""Tests for 05 · Token embeddings scaled by sqrt(d_model).

Run from the paper folder: python3.9 -m pytest exercises/05_embeddings
"""
import math

import torch

from _load import load

impl = load("05_embeddings")


def test_shape_and_table():
    emb = impl.Embeddings(vocab_size=11, d_model=8)
    assert isinstance(emb.lut, torch.nn.Embedding), "store the table as `lut`, an nn.Embedding"
    assert emb.lut.weight.shape == (11, 8), "one row per token: (vocab_size, d_model)"
    assert emb(torch.tensor([[1, 2, 3], [4, 5, 6]])).shape == (2, 3, 8)


def test_scaled_by_sqrt_d_model():
    torch.manual_seed(0)
    emb = impl.Embeddings(vocab_size=11, d_model=16)
    tokens = torch.tensor([[3, 0, 10]])
    torch.testing.assert_close(
        emb(tokens), emb.lut.weight[tokens] * math.sqrt(16),
        msg="§3.4: multiply the looked-up rows by sqrt(d_model)",
    )


def test_same_token_same_vector():
    emb = impl.Embeddings(vocab_size=11, d_model=8)
    out = emb(torch.tensor([[7, 2, 7]]))
    torch.testing.assert_close(out[0, 0], out[0, 2], msg="an embedding depends only on the token, not its position")


def test_gradient_only_reaches_used_rows():
    emb = impl.Embeddings(vocab_size=11, d_model=8)
    emb(torch.tensor([[1, 4]])).sum().backward()
    used = emb.lut.weight.grad.abs().sum(-1) > 0
    assert used.tolist() == [i in (1, 4) for i in range(11)], "only the rows for tokens 1 and 4 should get gradient"
