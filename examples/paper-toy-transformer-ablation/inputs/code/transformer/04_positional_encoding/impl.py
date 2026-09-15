"""04 · Sinusoidal positional encoding. See README.md and §3.5 of the paper."""
import math

import torch
from torch import nn


def sinusoidal_positional_encoding(max_len, d_model):
    """Table of positional encodings, shape (max_len, d_model), d_model even.

    PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
    PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
    """
    pos = torch.arange(max_len, dtype=torch.float32).unsqueeze(1)  # (max_len, 1)
    two_i = torch.arange(0, d_model, 2, dtype=torch.float32)       # 2i = 0, 2, 4, ...
    # 1 / 10000^(2i/d_model), computed in log space so we never form huge powers.
    inv_freq = torch.exp(-math.log(10000.0) * two_i / d_model)     # (d_model/2,)
    angles = pos * inv_freq                                        # (max_len, d_model/2)
    pe = torch.zeros(max_len, d_model)
    pe[:, 0::2] = torch.sin(angles)  # even dimensions: sine
    pe[:, 1::2] = torch.cos(angles)  # odd dimensions: cosine at the same frequency (interleaved)
    return pe


class PositionalEncoding(nn.Module):
    """Adds the fixed encodings to a batch of embeddings, then applies dropout (§5.4).

    Store the table from sinusoidal_positional_encoding as a buffer named `pe`
    (a buffer, not a parameter: it is never trained).
    """

    def __init__(self, d_model, dropout=0.0, max_len=5000):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        # A buffer moves with .to(device) and is saved in state_dict, but the optimizer never sees it.
        self.register_buffer("pe", sinusoidal_positional_encoding(max_len, d_model))

    def forward(self, x):
        """x: (batch, n, d_model) -> (batch, n, d_model)"""
        # pe[:n] is (n, d_model) and broadcasts over the batch dimension.
        return self.dropout(x + self.pe[: x.size(1)])
