"""Tests for 10 · Adam with the warmup learning-rate schedule.

Run from the paper folder: python3.9 -m pytest exercises/10_lr_schedule
"""
import pytest
import torch

from _load import load

impl = load("10_lr_schedule")


def test_hand_computed_values():
    assert impl.transformer_lr(4000) == pytest.approx(512 ** -0.5 * 4000 ** -0.5), "at step = warmup both branches equal"
    assert impl.transformer_lr(1) == pytest.approx(512 ** -0.5 * 4000 ** -1.5), "step 1 is on the linear warmup branch"
    assert impl.transformer_lr(100000) == pytest.approx(512 ** -0.5 * 100000 ** -0.5)


def test_peak_is_at_warmup_steps():
    rates = [impl.transformer_lr(s) for s in range(1, 20001)]
    assert rates.index(max(rates)) + 1 == 4000, "the learning rate should peak exactly at step = warmup_steps"


def test_linear_warmup_then_inverse_sqrt_decay():
    lr = impl.transformer_lr
    assert lr(2000) == pytest.approx(2 * lr(1000)), "during warmup, doubling the step doubles the learning rate"
    assert lr(16000) == pytest.approx(lr(4000) / 2), "after warmup, 4x the steps halves the learning rate"


def test_scales_with_d_model():
    assert impl.transformer_lr(500, d_model=128) == pytest.approx(2 * impl.transformer_lr(500, d_model=512))


def test_step_zero_is_safe():
    assert impl.transformer_lr(0) == pytest.approx(impl.transformer_lr(1)), "treat step 0 as step 1 instead of dividing by zero"


def test_optimizer_settings_and_schedule():
    param = torch.nn.Parameter(torch.zeros(3))
    optimizer, scheduler = impl.make_optimizer([param], d_model=64, warmup_steps=10)
    group = optimizer.param_groups[0]
    assert isinstance(optimizer, torch.optim.Adam)
    assert group["betas"] == (0.9, 0.98), "§5.3: beta1 = 0.9, beta2 = 0.98"
    assert group["eps"] == 1e-9, "§5.3: epsilon = 1e-9"
    assert group["lr"] == pytest.approx(impl.transformer_lr(1, 64, 10)), "Eq. (3) must be the actual learning rate"
    for _ in range(25):
        param.grad = torch.ones(3)
        optimizer.step()
        scheduler.step()
    assert group["lr"] == pytest.approx(impl.transformer_lr(25, 64, 10))
