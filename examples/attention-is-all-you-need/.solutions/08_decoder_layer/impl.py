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
    # Lower triangle including the diagonal: "up to and including that position" (§3.2.3).
    return torch.tril(torch.ones(1, n, n, dtype=torch.bool))


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
        self.self_attn = MultiHeadAttention(d_model, h)
        self.cross_attn = MultiHeadAttention(d_model, h)
        self.ffn = PositionwiseFeedForward(d_model, d_ff)
        self.sublayer1 = SublayerConnection(d_model, dropout)
        self.sublayer2 = SublayerConnection(d_model, dropout)
        self.sublayer3 = SublayerConnection(d_model, dropout)

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
        # 1. Masked self-attention over the target so far: no peeking at later positions.
        x = self.sublayer1(x, lambda t: self.self_attn(t, t, t, tgt_mask))
        # 2. Encoder-decoder attention: queries from the decoder, keys and values from the encoder memory.
        #    The whole source is visible, so only the source padding mask applies.
        x = self.sublayer2(x, lambda t: self.cross_attn(t, memory, memory, src_mask))
        # 3. Position-wise feed-forward.
        return self.sublayer3(x, self.ffn)


class Decoder(nn.Module):
    """A stack of N DecoderLayers with separate weights, all attending to the same memory (§3.1).

    Create `layers`: nn.ModuleList of N DecoderLayer(d_model, h, d_ff, dropout).
    """

    def __init__(self, d_model, h, d_ff, N, dropout=0.0):
        super().__init__()
        self.layers = nn.ModuleList([DecoderLayer(d_model, h, d_ff, dropout) for _ in range(N)])

    def forward(self, x, memory, src_mask=None, tgt_mask=None):
        """x: (batch, n_tgt, d_model), memory: (batch, n_src, d_model) -> (batch, n_tgt, d_model)"""
        # Every layer reads the *final* encoder output (Figure 1), not the matching encoder layer.
        for layer in self.layers:
            x = layer(x, memory, src_mask, tgt_mask)
        return x
