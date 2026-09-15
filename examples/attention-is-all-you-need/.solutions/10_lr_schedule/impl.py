"""10 · Adam with the warmup learning-rate schedule. See README.md and §5.3, Eq. (3) of the paper."""
import torch


def transformer_lr(step, d_model=512, warmup_steps=4000):
    """Eq. (3): d_model^-0.5 * min(step^-0.5, step * warmup_steps^-1.5).

    Steps count from 1; treat step < 1 as 1 (not in paper: the formula divides by zero at 0).
    """
    step = max(step, 1)
    # Linear ramp (step * warmup^-1.5) until the two branches meet at step == warmup_steps,
    # then inverse-square-root decay (step^-0.5).
    return d_model ** -0.5 * min(step ** -0.5, step * warmup_steps ** -1.5)


def make_optimizer(parameters, d_model=512, warmup_steps=4000):
    """Adam(beta1=0.9, beta2=0.98, eps=1e-9) whose learning rate follows Eq. (3) (§5.3).

    Returns:
        (optimizer, scheduler): scheduler is a torch.optim.lr_scheduler.LambdaLR; after k calls to
        scheduler.step(), the learning rate is transformer_lr(k, d_model, warmup_steps).
    """
    # Base lr = 1.0 because LambdaLR multiplies it by our function: Eq. (3) *is* the learning rate.
    optimizer = torch.optim.Adam(parameters, lr=1.0, betas=(0.9, 0.98), eps=1e-9)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: transformer_lr(step, d_model, warmup_steps)
    )
    return optimizer, scheduler
