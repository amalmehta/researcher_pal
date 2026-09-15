"""Experiment I-01: is it the warmup *ramp* that matters, or the large initial learning rate?

Without warmup (w = 1), Eq. 3 starts at 0.125, about 14x the warmup peak, so the original ablation changes two
things at once. The control removes the ramp but caps the learning rate at the baseline's peak:
    capped(t) = d_model^-0.5 * min(t^-0.5, w^-0.5)
It differs from the baseline only during the first w steps (flat at the peak instead of ramping up to it).

A baseline rerun checks that this script reproduces the original results.
Reads the researcher's code read-only; writes only to results/ next to this file.

Usage: python3.9 run.py [--steps 1500] [--seeds 0 1 2]
"""
import argparse
import csv
import importlib.util
import json
import platform
import time
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
CODE = HERE.parents[3] / "inputs" / "code"
RESULTS = HERE / "results"

spec = importlib.util.spec_from_file_location("run_ablation", CODE / "run_ablation.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)  # loads the researcher's Transformer, schedule, loss and task (read-only)

WARMUP = 200


def eq3(step, d_model, warmup):
    step = max(step, 1)
    return d_model ** -0.5 * min(step ** -0.5, step * warmup ** -1.5)


def capped(step, d_model, warmup):
    step = max(step, 1)
    return d_model ** -0.5 * min(step ** -0.5, warmup ** -0.5)


SCHEDULES = {"baseline_rerun": eq3, "no_ramp_capped": capped}


def run(name, seed, steps, log_every=25):
    ra.multi_head.scaled_dot_product_attention = ra.attention.scaled_dot_product_attention  # scaled attention
    torch.manual_seed(seed)
    data = torch.Generator().manual_seed(seed)
    task = ra.task
    model = ra.Transformer(task.VOCAB_SIZE, d_model=ra.D_MODEL, h=ra.HEADS, d_ff=ra.D_FF, N=ra.LAYERS, dropout=0.0,
                           max_len=task.SEQ_LEN + 1)
    optimizer, _ = ra.make_optimizer(model.parameters(), d_model=ra.D_MODEL, warmup_steps=WARMUP)  # same Adam settings
    schedule = SCHEDULES[name]
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda s: schedule(s, ra.D_MODEL, WARMUP))
    loss_fn = ra.LabelSmoothingLoss(task.VOCAB_SIZE, smoothing=0.1, ignore_index=task.PAD)
    tgt_mask = ra.subsequent_mask(task.SEQ_LEN)

    curve, start = [], time.time()
    model.train()
    for step in range(1, steps + 1):
        src, tgt_in, tgt = task.make_batch(ra.BATCH, data)
        loss = loss_fn(model(src, tgt_in, tgt_mask=tgt_mask), tgt)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        if step == 1 or step % log_every == 0:
            curve.append((step, loss.item()))
    model.eval()
    src, tgt_in, tgt = task.make_batch(500, data)
    with torch.no_grad():
        model(src, tgt_in, tgt_mask=tgt_mask)
        alignment = task.reversal_alignment(model)
        accuracy = (task.greedy_decode(model, src) == tgt).all(dim=1).float().mean().item()
    last = [l for _, l in curve[-4:]]
    return {"config": name, "warmup_steps": WARMUP, "seed": seed, "steps": steps,
            "initial_lr": schedule(1, ra.D_MODEL, WARMUP), "peak_lr": max(schedule(s, ra.D_MODEL, WARMUP) for s in range(1, steps + 1)),
            "final_loss": sum(last) / len(last), "accuracy": accuracy, "alignment": alignment,
            "seconds": time.time() - start}, curve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--configs", nargs="+", default=list(SCHEDULES))
    parser.add_argument("--tag", default="", help="suffix for result files, e.g. _pilot")
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / ("environment%s.json" % args.tag)).write_text(json.dumps({
        "python": platform.python_version(), "torch": torch.__version__, "torch_threads": torch.get_num_threads(),
        "steps": args.steps, "seeds": args.seeds, "warmup_steps": WARMUP, "d_model": ra.D_MODEL}, indent=2))
    with (RESULTS / ("runs%s.csv" % args.tag)).open("w", newline="") as rf, (RESULTS / ("loss_curves%s.csv" % args.tag)).open("w", newline="") as cf:
        runs = csv.DictWriter(rf, fieldnames=["config", "warmup_steps", "seed", "steps", "initial_lr", "peak_lr",
                                              "final_loss", "accuracy", "alignment", "seconds"])
        curves = csv.writer(cf)
        runs.writeheader()
        curves.writerow(["config", "seed", "step", "loss"])
        for name in args.configs:
            for seed in args.seeds:
                row, curve = run(name, seed, args.steps)
                runs.writerow(row)
                curves.writerows([(name, seed, s, l) for s, l in curve])
                rf.flush()
                cf.flush()
                print("%-15s seed %d acc %.3f align %.3f loss %.3f %.0fs" % (name, seed, row["accuracy"], row["alignment"],
                                                                            row["final_loss"], row["seconds"]), flush=True)


if __name__ == "__main__":
    main()
