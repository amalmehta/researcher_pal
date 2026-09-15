"""06 · Residual connection, dropout and LayerNorm. See README.md and §3.1, §5.4 of the paper."""
import torch
from torch import nn


class SublayerConnection(nn.Module):
    """output = LayerNorm(x + Dropout(sublayer(x)))   (§3.1 and §5.4)

    Create `norm`: nn.LayerNorm(d_model) and `dropout`: nn.Dropout(dropout).
    """

    def __init__(self, d_model, dropout=0.0):
        super().__init__()
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        """x: (batch, n, d_model); sublayer: function (batch, n, d_model) -> (batch, n, d_model)."""
        # Post-LN, as in the paper: dropout on the sub-layer's output, add the untouched input,
        # then normalize the sum. (Pre-LN would be x + dropout(sublayer(norm(x))).)
        return self.norm(x + self.dropout(sublayer(x)))
