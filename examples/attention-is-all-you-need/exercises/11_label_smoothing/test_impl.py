"""Tests for 11 · Label smoothing.

Run from the paper folder: python3.9 -m pytest exercises/11_label_smoothing
"""
import math

import torch
import torch.nn.functional as F

from _load import load

impl = load("11_label_smoothing")


def test_no_smoothing_is_plain_cross_entropy():
    torch.manual_seed(0)
    logits, target = torch.randn(6, 5), torch.randint(0, 5, (6,))
    loss = impl.LabelSmoothingLoss(5, smoothing=0.0)(logits, target)
    torch.testing.assert_close(loss, F.cross_entropy(logits, target), msg="with eps = 0 this is ordinary cross-entropy")


def test_uniform_prediction_costs_log_v_whatever_eps():
    logits, target = torch.zeros(3, 4), torch.tensor([0, 2, 3])
    for eps in (0.0, 0.1, 0.5):
        loss = impl.LabelSmoothingLoss(4, smoothing=eps)(logits, target)
        torch.testing.assert_close(loss, torch.tensor(math.log(4)), msg="a uniform prediction costs log V for any target mix")


def test_matches_pytorch_label_smoothing():
    torch.manual_seed(0)
    logits, target = torch.randn(10, 7), torch.randint(0, 7, (10,))
    loss = impl.LabelSmoothingLoss(7, smoothing=0.1)(logits, target)
    torch.testing.assert_close(loss, F.cross_entropy(logits, target, label_smoothing=0.1))


def test_ignore_index_excludes_padding():
    torch.manual_seed(0)
    logits, target = torch.randn(2, 5, 7), torch.randint(1, 7, (2, 5))
    target[:, 3:] = 0  # padding
    loss_fn = impl.LabelSmoothingLoss(7, smoothing=0.1, ignore_index=0)
    expected = F.cross_entropy(logits.reshape(-1, 7), target.reshape(-1), ignore_index=0, label_smoothing=0.1)
    torch.testing.assert_close(loss_fn(logits, target), expected, msg="accept (..., V) logits and skip padded positions in the mean")
    logits_changed = logits.clone()
    logits_changed[:, 3:] = torch.randn(2, 2, 7)
    torch.testing.assert_close(loss_fn(logits_changed, target), loss_fn(logits, target), msg="padded positions must not affect the loss")


def test_optimum_is_the_smoothed_target_not_one_hot():
    V, eps = 4, 0.1
    target = torch.tensor([2])
    loss_fn = impl.LabelSmoothingLoss(V, smoothing=eps)
    smoothed = torch.full((1, V), eps / V)
    smoothed[0, 2] += 1 - eps
    confident = torch.full((1, V), -20.0)
    confident[0, 2] = 20.0
    assert loss_fn(smoothed.log(), target) < loss_fn(confident, target), (
        "with smoothing, predicting q' exactly beats being 100% sure: that's why perplexity gets worse"
    )
