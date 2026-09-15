"""03 · Position-wise feed-forward network. See README.md and §3.3, Eq. (2) of the paper."""
import torch
from torch import nn


class PositionwiseFeedForward(nn.Module):
    """FFN(x) = max(0, x W_1 + b_1) W_2 + b_2, applied to every position separately and identically.

    Create these submodules (the tests use these names):
        linear1: nn.Linear(d_model, d_ff)   # W_1, b_1
        linear2: nn.Linear(d_ff, d_model)   # W_2, b_2
    """

    def __init__(self, d_model, d_ff):
        super().__init__()
        raise NotImplementedError("TODO: create linear1 and linear2")

    def forward(self, x):
        """x: (batch, n, d_model) -> (batch, n, d_model)"""
        raise NotImplementedError("TODO: implement Eq. (2)")
