"""09 · The full Transformer. See README.md and Figure 1, §3.4 of the paper."""
import torch
from torch import nn

from _load import load

# Your work from earlier exercises.
PositionalEncoding = load("04_positional_encoding").PositionalEncoding
Embeddings = load("05_embeddings").Embeddings
Encoder = load("07_encoder_layer").Encoder
Decoder = load("08_decoder_layer").Decoder


class Transformer(nn.Module):
    """Figure 1: a shared-vocabulary encoder-decoder with tied embeddings (§3, §3.4).

    Create these submodules (the tests use these names):
        src_embed, tgt_embed: Embeddings(vocab_size, d_model)
        pos_encoding:         PositionalEncoding(d_model, dropout, max_len)  # no parameters, used by both sides
        encoder:              Encoder(d_model, h, d_ff, N, dropout)
        decoder:              Decoder(d_model, h, d_ff, N, dropout)
        generator:            nn.Linear(d_model, vocab_size, bias=False)

    Tie the weights (§3.4): src_embed.lut.weight, tgt_embed.lut.weight and generator.weight must be the
    same Parameter. Initialize every parameter with dim > 1 using nn.init.xavier_uniform_ (not in paper).
    """

    def __init__(self, vocab_size, d_model=512, h=8, d_ff=2048, N=6, dropout=0.1, max_len=5000):
        super().__init__()
        raise NotImplementedError("TODO: create the submodules, tie the weights, initialize")

    def encode(self, src, src_mask=None):
        """src: (batch, n_src) long -> memory: (batch, n_src, d_model)"""
        raise NotImplementedError("TODO: embed, add positions, run the encoder")

    def decode(self, memory, tgt, src_mask=None, tgt_mask=None):
        """memory: (batch, n_src, d_model), tgt: (batch, n_tgt) long -> (batch, n_tgt, d_model)"""
        raise NotImplementedError("TODO: embed, add positions, run the decoder")

    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        """-> logits: (batch, n_tgt, vocab_size)"""
        raise NotImplementedError("TODO: encode, decode, project to the vocabulary")
