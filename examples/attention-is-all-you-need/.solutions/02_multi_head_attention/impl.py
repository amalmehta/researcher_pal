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
        if d_model % h != 0:
            raise ValueError("d_model=%d is not divisible by h=%d" % (d_model, h))
        self.h = h
        self.d_k = d_model // h
        # One d_model -> h*d_k matrix is the h per-head d_model -> d_k matrices stacked row-wise.
        # No biases: the paper's projections are plain matrices.
        self.w_q = nn.Linear(d_model, d_model, bias=False)
        self.w_k = nn.Linear(d_model, d_model, bias=False)
        self.w_v = nn.Linear(d_model, d_model, bias=False)
        self.w_o = nn.Linear(d_model, d_model, bias=False)
        self.last_weights = None

    def _split_heads(self, x):
        # (batch, n, d_model) -> (batch, h, n, d_k): heads become a leading dimension,
        # so one call to scaled_dot_product_attention runs all heads in parallel.
        batch, n, _ = x.shape
        return x.view(batch, n, self.h, self.d_k).transpose(1, 2)

    def forward(self, query, key, value, mask=None):
        """
        Args:
            query: (batch, n_q, d_model)
            key, value: (batch, n_k, d_model)
            mask: optional bool, shape (batch or 1, n_q or 1, n_k); True = may attend

        Returns:
            (batch, n_q, d_model)
        """
        q = self._split_heads(self.w_q(query))
        k = self._split_heads(self.w_k(key))
        v = self._split_heads(self.w_v(value))
        if mask is not None:
            mask = mask.unsqueeze(1)  # (batch, 1, n_q, n_k): broadcast the same mask over every head
        out, self.last_weights = scaled_dot_product_attention(q, k, v, mask)
        batch, _, n_q, _ = out.shape
        # Concat(head_1, ..., head_h): move heads next to d_k, then merge. transpose makes the
        # tensor non-contiguous, so .contiguous() is needed before .view().
        out = out.transpose(1, 2).contiguous().view(batch, n_q, self.h * self.d_k)
        return self.w_o(out)
