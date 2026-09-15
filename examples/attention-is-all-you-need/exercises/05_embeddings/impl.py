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
        raise NotImplementedError("TODO: create the lookup table `lut`")

    def forward(self, tokens):
        """tokens: (batch, n) long -> (batch, n, d_model)"""
        raise NotImplementedError("TODO: look up and scale")
