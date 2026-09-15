"""05 · Token embeddings scaled by sqrt(d_model). See README.md and §3.4 of the paper."""
import math

import torch
from torch import nn


class Embeddings(nn.Module):
    """embed(t) = sqrt(d_model) * E[t]   (§3.4)

    Create `lut`: nn.Embedding(vocab_size, d_model). Exercise 09 shares its weight with the
    other embedding and the pre-softmax projection.
    """

    def __init__(self, vocab_size, d_model):
        super().__init__()
        self.lut = nn.Embedding(vocab_size, d_model)
        self.scale = math.sqrt(d_model)

    def forward(self, tokens):
        """tokens: (batch, n) long -> (batch, n, d_model)"""
        # The sqrt(d_model) factor is stated but not explained in §3.4; it keeps embeddings on a
        # scale comparable to the positional encodings they are added to.
        return self.lut(tokens) * self.scale
