"""02 · Multi-head attention. See README.md and §3.2.2 of the paper."""
import torch
from torch import nn

from _load import load

# Your attention function from exercise 01.
scaled_dot_product_attention = load("01_scaled_dot_product_attention").scaled_dot_product_attention


class MultiHeadAttention(nn.Module):
    """MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O,  head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V).

    Create these submodules (the tests use these names):
        w_q, w_k, w_v: nn.Linear(d_model, d_model, bias=False); the h heads' projections stacked,
                       head i owning output features i*d_k : (i+1)*d_k
        w_o:           nn.Linear(d_model, d_model, bias=False)

    d_k = d_v = d_model // h; raise ValueError if d_model is not divisible by h.
    After forward, self.last_weights holds the attention weights, shape (batch, h, n_q, n_k).
    """

    def __init__(self, d_model, h):
        super().__init__()
        raise NotImplementedError("TODO: check d_model % h and create w_q, w_k, w_v, w_o")

    def forward(self, query, key, value, mask=None):
        """
        Args:
            query: (batch, n_q, d_model)
            key, value: (batch, n_k, d_model)
            mask: optional bool, shape (batch or 1, n_q or 1, n_k); True = may attend

        Returns:
            (batch, n_q, d_model)
        """
        raise NotImplementedError("TODO: project, split into heads, attend, concatenate, project")
