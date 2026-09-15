"""04 · Sinusoidal positional encoding. See README.md and §3.5 of the paper."""
import math

import torch
from torch import nn


def sinusoidal_positional_encoding(max_len, d_model):
    """Table of positional encodings, shape (max_len, d_model), d_model even.

    PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
    PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
    """
    raise NotImplementedError("TODO: build the sine/cosine table")


class PositionalEncoding(nn.Module):
    """Adds the fixed encodings to a batch of embeddings, then applies dropout (§5.4).

    Store the table from sinusoidal_positional_encoding as a buffer named `pe`
    (a buffer, not a parameter: it is never trained).
    """

    def __init__(self, d_model, dropout=0.0, max_len=5000):
        super().__init__()
        raise NotImplementedError("TODO: create the dropout and register the `pe` buffer")

    def forward(self, x):
        """x: (batch, n, d_model) -> (batch, n, d_model)"""
        raise NotImplementedError("TODO: add the first n encodings, then dropout")
