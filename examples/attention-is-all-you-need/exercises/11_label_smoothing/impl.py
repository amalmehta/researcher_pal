"""11 · Label smoothing. See README.md and §5.4 of the paper."""
import torch
from torch import nn


class LabelSmoothingLoss(nn.Module):
    """Cross-entropy against the smoothed target q'(k) = (1 - eps) [k == y] + eps / V   (§5.4).

    Args:
        vocab_size: V
        smoothing: eps (0.1 in the paper)
        ignore_index: optional token ID (e.g. padding) whose positions don't count

    forward(logits, target): logits (..., V), target (...) long -> scalar mean over counted positions
    """

    def __init__(self, vocab_size, smoothing=0.1, ignore_index=None):
        super().__init__()
        raise NotImplementedError("TODO: store the settings")

    def forward(self, logits, target):
        raise NotImplementedError("TODO: smoothed cross-entropy, ignoring padded positions")
