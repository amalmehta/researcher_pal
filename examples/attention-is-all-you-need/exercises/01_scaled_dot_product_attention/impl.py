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
    raise NotImplementedError("TODO: implement Eq. (1) with optional masking")
