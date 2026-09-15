"""Ablation for the workshop paper: does a small Transformer still learn sequence reversal without
learning-rate warmup (Eq. 3 of Vaswani et al.) or without the 1/sqrt(d_k) attention scaling (Eq. 1)?

Writes, next to this file:
    ../results/ablation_runs.csv   one row per (config, seed)
    ../results/loss_curves.csv     training loss every 25 steps
    ../results/environment.json    software and hardware the runs used

Usage: python3.9 run_ablation.py [--steps 1500] [--seeds 0 1 2]
"""
import argparse
import csv
import json
import platform
import sys
import time
from pathlib import Path

import torch

HERE = Path(__file__).parent
RESULTS = HERE.parent / "results"
sys.path.insert(0, str(HERE / "transformer"))
from _load import load  # noqa: E402

attention = load("01_scaled_dot_product_attention")
multi_head = load("02_multi_head_attention")
task = load("12_final_reversal")
Transformer = load("09_transformer").Transformer
subsequent_mask = load("08_decoder_layer").subsequent_mask
make_optimizer = load("10_lr_schedule").make_optimizer
LabelSmoothingLoss = load("11_label_smoothing").LabelSmoothingLoss

D_MODEL, HEADS, D_FF, LAYERS, BATCH = 64, 4, 128, 2, 64

# name, warmup_steps (1 = no warmup: Eq. 3 starts at its peak), scaled attention?
CONFIGS = [
    ("baseline", 200, True),
    ("no_warmup", 1, True),
    ("no_scaling", 200, False),
    ("no_warmup_no_scaling", 1, False),
]


def unscaled_attention(q, k, v, mask=None):
    """Eq. (1) without the 1/sqrt(d_k) factor."""
    scores = q @ k.transpose(-2, -1)
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))
    weights = torch.softmax(scores, dim=-1)
    return weights @ v, weights


def run(name, warmup, scaled, seed, steps, log_every=25):
    # Multi-head attention looks this function up at call time, so swapping it switches the ablation.
    multi_head.scaled_dot_product_attention = attention.scaled_dot_product_attention if scaled else unscaled_attention
    torch.manual_seed(seed)
    data = torch.Generator().manual_seed(seed)
    model = Transformer(task.VOCAB_SIZE, d_model=D_MODEL, h=HEADS, d_ff=D_FF, N=LAYERS, dropout=0.0, max_len=task.SEQ_LEN + 1)
    optimizer, scheduler = make_optimizer(model.parameters(), d_model=D_MODEL, warmup_steps=warmup)
    loss_fn = LabelSmoothingLoss(task.VOCAB_SIZE, smoothing=0.1, ignore_index=task.PAD)
    tgt_mask = subsequent_mask(task.SEQ_LEN)

    curve, start = [], time.time()
    model.train()
    for step in range(1, steps + 1):
        src, tgt_in, tgt = task.make_batch(BATCH, data)
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
    last = [loss for _, loss in curve[-4:]]
    row = {
        "config": name, "warmup_steps": warmup, "scaled_attention": int(scaled), "seed": seed, "steps": steps,
        "final_loss": sum(last) / len(last), "accuracy": accuracy, "alignment": alignment,
        "seconds": time.time() - start,
    }
    return row, curve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "environment.json").write_text(json.dumps({
        "python": platform.python_version(), "torch": torch.__version__, "machine": platform.machine(),
        "processor": platform.processor(), "torch_threads": torch.get_num_threads(), "device": "cpu",
        "d_model": D_MODEL, "heads": HEADS, "d_ff": D_FF, "layers": LAYERS, "batch_size": BATCH,
        "sequence_length": task.SEQ_LEN, "vocab_size": task.VOCAB_SIZE, "label_smoothing": 0.1,
        "eval_sequences": 500, "steps": args.steps, "seeds": args.seeds,
    }, indent=2))

    runs_path, curves_path = RESULTS / "ablation_runs.csv", RESULTS / "loss_curves.csv"
    with runs_path.open("w", newline="") as runs_file, curves_path.open("w", newline="") as curves_file:
        runs = csv.DictWriter(runs_file, fieldnames=["config", "warmup_steps", "scaled_attention", "seed", "steps",
                                                     "final_loss", "accuracy", "alignment", "seconds"])
        curves = csv.writer(curves_file)
        runs.writeheader()
        curves.writerow(["config", "seed", "step", "loss"])
        for name, warmup, scaled in CONFIGS:
            for seed in args.seeds:
                row, curve = run(name, warmup, scaled, seed, args.steps)
                runs.writerow(row)
                curves.writerows([(name, seed, step, loss) for step, loss in curve])
                runs_file.flush()
                curves_file.flush()
                print("%-22s seed %d  acc %.3f  align %.3f  loss %.3f  %.0fs"
                      % (name, seed, row["accuracy"], row["alignment"], row["final_loss"], row["seconds"]), flush=True)


if __name__ == "__main__":
    main()
