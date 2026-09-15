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
        self.vocab_size = vocab_size
        self.smoothing = smoothing
        self.ignore_index = ignore_index

    def forward(self, logits, target):
        log_probs = torch.log_softmax(logits.reshape(-1, self.vocab_size), dim=-1)  # stable log p(k)
        target = target.reshape(-1)
        # -sum_k q'(k) log p(k) = (1 - eps) * (-log p(y)) + eps * (-(1/V) sum_k log p(k))
        nll = -log_probs.gather(1, target.unsqueeze(1)).squeeze(1)
        uniform = -log_probs.mean(dim=1)
        loss = (1 - self.smoothing) * nll + self.smoothing * uniform
        if self.ignore_index is None:
            return loss.mean()
        keep = target != self.ignore_index
        return loss[keep].sum() / keep.sum().clamp(min=1)
