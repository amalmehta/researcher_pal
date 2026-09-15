"""06 · Residual connection, dropout and LayerNorm. See README.md and §3.1, §5.4 of the paper."""
import torch
from torch import nn


class SublayerConnection(nn.Module):
    """output = LayerNorm(x + Dropout(sublayer(x)))   (§3.1 and §5.4)

    Create `norm`: nn.LayerNorm(d_model) and `dropout`: nn.Dropout(dropout).
    """

    def __init__(self, d_model, dropout=0.0):
        super().__init__()
        raise NotImplementedError("TODO: create norm and dropout")

    def forward(self, x, sublayer):
        """x: (batch, n, d_model); sublayer: function (batch, n, d_model) -> (batch, n, d_model)."""
        raise NotImplementedError("TODO: residual + dropout + LayerNorm in the paper's order")
