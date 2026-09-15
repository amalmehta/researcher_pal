"""01 · Scaled dot-product attention. See README.md and §3.2.1, Eq. (1) of the paper."""
import math

import torch


def scaled_dot_product_attention(q, k, v, mask=None):
    """Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V.

    Args:
        q: queries, shape (..., n_q, d_k)
        k: keys, shape (..., n_k, d_k)
        v: values, shape (..., n_k, d_v)
        mask: optional bool tensor broadcastable to (..., n_q, n_k);
            True where the query may attend to the key.

    Returns:
        output: shape (..., n_q, d_v)
        weights: attention weights, shape (..., n_q, n_k); each row sums to 1
    """
    d_k = q.size(-1)
    # (..., n_q, d_k) @ (..., d_k, n_k) -> (..., n_q, n_k): one score per query-key pair.
    # Dividing by sqrt(d_k) keeps the scores' spread near 1 whatever d_k is (footnote 4).
    scores = q @ k.transpose(-2, -1) / math.sqrt(d_k)
    if mask is not None:
        # §3.2.3: illegal connections get -inf *before* the softmax, so they receive exactly 0 weight
        # and the remaining weights still sum to 1.
        scores = scores.masked_fill(~mask, float("-inf"))
    # Normalize over the keys axis: each query distributes one unit of attention.
    weights = torch.softmax(scores, dim=-1)
    return weights @ v, weights
