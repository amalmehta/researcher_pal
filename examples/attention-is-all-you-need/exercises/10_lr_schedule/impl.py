"""10 · Adam with the warmup learning-rate schedule. See README.md and §5.3, Eq. (3) of the paper."""
import torch


def transformer_lr(step, d_model=512, warmup_steps=4000):
    """Eq. (3): d_model^-0.5 * min(step^-0.5, step * warmup_steps^-1.5).

    Steps count from 1; treat step < 1 as 1 (not in paper: the formula divides by zero at 0).
    """
    raise NotImplementedError("TODO: implement Eq. (3)")


def make_optimizer(parameters, d_model=512, warmup_steps=4000):
    """Adam(beta1=0.9, beta2=0.98, eps=1e-9) whose learning rate follows Eq. (3) (§5.3).

    Returns:
        (optimizer, scheduler): scheduler is a torch.optim.lr_scheduler.LambdaLR; after k calls to
        scheduler.step(), the learning rate is transformer_lr(k, d_model, warmup_steps).
    """
    raise NotImplementedError("TODO: create Adam and a LambdaLR that follows Eq. (3)")
