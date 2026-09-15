"""07 · Encoder layer and stack. See README.md and §3.1 of the paper."""
import torch
from torch import nn

from _load import load

# Your work from earlier exercises.
MultiHeadAttention = load("02_multi_head_attention").MultiHeadAttention
PositionwiseFeedForward = load("03_position_wise_ffn").PositionwiseFeedForward
SublayerConnection = load("06_sublayer_connection").SublayerConnection


class EncoderLayer(nn.Module):
    """Self-attention, then feed-forward, each wrapped in a SublayerConnection (§3.1).

    Create these submodules (the tests use these names):
        self_attn: MultiHeadAttention(d_model, h)
        ffn:       PositionwiseFeedForward(d_model, d_ff)
        sublayer1: SublayerConnection(d_model, dropout)   # around self_attn
        sublayer2: SublayerConnection(d_model, dropout)   # around ffn
    """

    def __init__(self, d_model, h, d_ff, dropout=0.0):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, h)
        self.ffn = PositionwiseFeedForward(d_model, d_ff)
        self.sublayer1 = SublayerConnection(d_model, dropout)
        self.sublayer2 = SublayerConnection(d_model, dropout)

    def forward(self, x, mask=None):
        """x: (batch, n, d_model); mask: bool (batch or 1, 1, n), True = real token -> (batch, n, d_model)"""
        # Self-attention: queries, keys and values all come from x (§3.2.3, first encoder bullet).
        # The lambda turns the 4-argument attention into the 1-argument function SublayerConnection expects.
        x = self.sublayer1(x, lambda t: self.self_attn(t, t, t, mask))
        return self.sublayer2(x, self.ffn)


class Encoder(nn.Module):
    """A stack of N EncoderLayers with separate weights (§3.1, N = 6 in the paper).

    Create `layers`: nn.ModuleList of N EncoderLayer(d_model, h, d_ff, dropout).
    """

    def __init__(self, d_model, h, d_ff, N, dropout=0.0):
        super().__init__()
        # Build N fresh layers. Repeating one layer object N times would silently share its weights.
        self.layers = nn.ModuleList([EncoderLayer(d_model, h, d_ff, dropout) for _ in range(N)])

    def forward(self, x, mask=None):
        """x: (batch, n, d_model) -> (batch, n, d_model)"""
        for layer in self.layers:
            x = layer(x, mask)
        return x
