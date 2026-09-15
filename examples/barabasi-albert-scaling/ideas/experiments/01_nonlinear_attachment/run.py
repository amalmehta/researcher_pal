"""Experiment I-01: does scaling really appear only for linear attachment (alpha = 1)?

The paper (¶10, E9) says simulations with Pi(k) ~ k^alpha show scaling "only for alpha = 1", without details. Grow the
same model with alpha in {0.5, 1.0, 1.5} and measure the fitted tail exponent, the largest hub, and the hub's share of
all edge endpoints. The learner's measurement code (.solutions/03_final_scale_free) is imported read-only.

Writes results/runs.csv, results/degree_ccdf.csv and results/degree_ccdf.png next to this file.
Usage: python3.9 run.py [--t 20000] [--seeds 0 1 2] [--alphas 0.5 1.0 1.5]
"""
import argparse
import csv
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[2]
RESULTS = HERE / "results"

sys.path.insert(0, str(PAPER / "exercises"))  # for the harness's _load
spec = importlib.util.spec_from_file_location("final_solution", PAPER / ".solutions" / "03_final_scale_free" / "impl.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)  # read-only: fit_power_law_exponent


def grow(t, m, m0, alpha, rng):
    """The paper's model with Pi(k_i) proportional to k_i^alpha; complete-graph start as in exercise 03."""
    degrees = np.zeros(m0 + t)
    degrees[:m0] = m0 - 1
    for step in range(t):
        n = m0 + step
        weights = degrees[:n] ** alpha
        targets = rng.choice(n, size=m, replace=False, p=weights / weights.sum())
        degrees[targets] += 1
        degrees[n] = m
    return degrees.astype(int)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=20000)
    parser.add_argument("--m", type=int, default=5)
    parser.add_argument("--m0", type=int, default=5)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.5, 1.0, 1.5])
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / ("environment%s.json" % args.tag)).write_text(json.dumps(
        {"python": platform.python_version(), "numpy": np.__version__, **vars(args)}, indent=2))

    rows, ccdf = [], []
    for alpha in args.alphas:
        for seed in args.seeds:
            start = time.time()
            degrees = grow(args.t, args.m, args.m0, alpha, np.random.default_rng(seed))
            ks, counts = np.unique(degrees, return_counts=True)
            tail = counts[::-1].cumsum()[::-1] / len(degrees)  # P(K >= k)
            ccdf += [(alpha, seed, int(k), float(p)) for k, p in zip(ks, tail)]
            rows.append({
                "alpha": alpha, "seed": seed, "t": args.t, "m": args.m,
                "gamma_fit_kmin20": float(final.fit_power_law_exponent(degrees, k_min=20)),
                "max_degree": int(degrees.max()), "hub_share": float(degrees.max() / degrees.sum()),
                "vertices_degree_ge_20": int((degrees >= 20).sum()), "seconds": time.time() - start,
            })
            print(rows[-1], flush=True)

    with (RESULTS / ("runs%s.csv" % args.tag)).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (RESULTS / ("degree_ccdf%s.csv" % args.tag)).open("w", newline="") as f:
        csv.writer(f).writerows([("alpha", "seed", "k", "ccdf")] + ccdf)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {0.5: "#0072B2", 1.0: "#D55E00", 1.5: "#009E73"}
    fig, ax = plt.subplots(figsize=(5.5, 3.4), constrained_layout=True)
    for alpha in args.alphas:
        pts = [(k, p) for a, s, k, p in ccdf if a == alpha and s == args.seeds[0]]
        ax.loglog([k for k, _ in pts], [p for _, p in pts], color=colors.get(alpha, "black"), label="alpha = %g" % alpha)
    ref = np.logspace(np.log10(args.m), 3, 50)
    ax.loglog(ref, (ref / args.m) ** -2, "k--", linewidth=0.8, label="slope -2 (P(k) ~ k^-3)")
    ax.set_xlabel("degree k")
    ax.set_ylabel("P(K >= k)")
    ax.set_title("Degree CCDF, seed %d, t = %d" % (args.seeds[0], args.t))
    ax.legend(frameon=False)
    fig.savefig(RESULTS / ("degree_ccdf%s.png" % args.tag), dpi=150)
    print("wrote results")


if __name__ == "__main__":
    main()
