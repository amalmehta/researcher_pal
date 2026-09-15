"""08 · Decoder layer, causal mask and stack. See README.md and §3.1, §3.2.3 of the paper."""
import torch
from torch import nn

from _load import load

# Your work from earlier exercises.
MultiHeadAttention = load("02_multi_head_attention").MultiHeadAttention
PositionwiseFeedForward = load("03_position_wise_ffn").PositionwiseFeedForward
SublayerConnection = load("06_sublayer_connection").SublayerConnection


def subsequent_mask(n):
    """Bool mask of shape (1, n, n): True where position i may attend to position j, i.e. j <= i."""
    raise NotImplementedError("TODO: build the causal mask")


class DecoderLayer(nn.Module):
    """Masked self-attention, encoder-decoder attention, feed-forward; each in a SublayerConnection (§3.1).

    Create these submodules (the tests use these names):
        self_attn:  MultiHeadAttention(d_model, h)
        cross_attn: MultiHeadAttention(d_model, h)
        ffn:        PositionwiseFeedForward(d_model, d_ff)
        sublayer1, sublayer2, sublayer3: SublayerConnection(d_model, dropout)
    """

    def __init__(self, d_model, h, d_ff, dropout=0.0):
        super().__init__()
        raise NotImplementedError("TODO: create the attention blocks, the FFN and three sublayer wrappers")

    def forward(self, x, memory, src_mask=None, tgt_mask=None):
        """
        Args:
            x: (batch, n_tgt, d_model)
            memory: final encoder output, (batch, n_src, d_model)
            src_mask: bool (batch or 1, 1, n_src), True = real source token
            tgt_mask: bool (batch or 1, n_tgt, n_tgt), True = may attend

        Returns:
            (batch, n_tgt, d_model)
        """
        raise NotImplementedError("TODO: masked self-attention, encoder-decoder attention, feed-forward")


class Decoder(nn.Module):
    """A stack of N DecoderLayers with separate weights, all attending to the same memory (§3.1).

    Create `layers`: nn.ModuleList of N DecoderLayer(d_model, h, d_ff, dropout).
    """

    def __init__(self, d_model, h, d_ff, N, dropout=0.0):
        super().__init__()
        raise NotImplementedError("TODO: create the N layers")

    def forward(self, x, memory, src_mask=None, tgt_mask=None):
        """x: (batch, n_tgt, d_model), memory: (batch, n_src, d_model) -> (batch, n_tgt, d_model)"""
        raise NotImplementedError("TODO: run the layers in order")
