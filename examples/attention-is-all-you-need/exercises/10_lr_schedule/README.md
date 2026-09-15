# 10 · Adam with the warmup learning-rate schedule

**Goal:** implement Eq. (3) and the Adam settings from §5.3. Without warmup, the post-LN Transformer often fails
to train.

**Read first:** [lr_schedule](../../concept_graph.md#lr_schedule-warmup-learning-rate-schedule) · §5.3, Eq. (3)
**Watch:** [learning-rate schedule animation](../../animations/lr_schedule.html)

## What to implement

1. `transformer_lr(step, d_model=512, warmup_steps=4000)`:

$$
lrate = d_{model}^{-0.5} \cdot \min\!\left(step\_num^{-0.5},\ step\_num \cdot warmup\_steps^{-1.5}\right) \tag{3}
$$

   Steps count from 1. Treat `step < 1` as 1, since the formula divides by zero at 0 (**not in paper**).

2. `make_optimizer(parameters, d_model=512, warmup_steps=4000)` returns `(optimizer, scheduler)`:
   `torch.optim.Adam` with $\beta_1 = 0.9$, $\beta_2 = 0.98$, $\epsilon = 10^{-9}$, and a
   `torch.optim.lr_scheduler.LambdaLR` so that the learning rate after `k` calls to `scheduler.step()` is `transformer_lr(k)`.

## Run the tests

```bash
python3.9 -m pytest exercises/10_lr_schedule
```

## Things to think about

- `LambdaLR` *multiplies* the optimizer's base learning rate by your function. What base learning rate makes the product
  exactly Eq. (3)?
- Where do the two branches of the `min` cross? What's the peak learning rate for the base model?
