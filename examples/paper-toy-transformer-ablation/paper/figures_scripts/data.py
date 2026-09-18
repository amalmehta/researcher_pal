"""Load the researcher's results. Every number in the paper passes through here."""
import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent


def _venue_dir():
    """Which venue these figures are built for: $VENUE_DIR (set by make_all.py), or the only one there is."""
    if os.environ.get("VENUE_DIR"):
        return Path(os.environ["VENUE_DIR"]).resolve()
    venues = sorted(p.parent for p in PAPER_DIR.glob("*/main.tex"))
    if len(venues) != 1:
        raise SystemExit("this paper has %d venue folders; run 'python3 make_all.py <venue folder>' or set VENUE_DIR"
                         % len(venues))
    return venues[0]


VENUE_DIR = _venue_dir()
VENUE = os.environ.get("VENUE") or re.sub(r"\d+$", "", VENUE_DIR.name)
INPUTS = PAPER_DIR.parent / "inputs"
RESULTS = INPUTS / "results"
# Approved improvement experiment I-01 (paper-ideas); read only if its results exist.
RAMP = PAPER_DIR / "ideas" / "experiments" / "01_ramp_vs_peak_lr" / "results"

# (config id in the CSV, label in the paper)
CONFIGS = [
    ("baseline", "Baseline"),
    ("no_scaling", "No scaling"),
    ("no_warmup", "No warmup"),
    ("no_warmup_no_scaling", "Neither"),
]
if (RAMP / "runs.csv").exists():
    CONFIGS.append(("no_ramp_capped", "No ramp, capped"))


def _experiment_rows(config):
    rows = []
    if (RAMP / "runs.csv").exists():
        with (RAMP / "runs.csv").open() as f:
            for row in csv.DictReader(f):
                if row["config"] == config:
                    rows.append({"config": config, "warmup_steps": int(row["warmup_steps"]), "scaled_attention": 1,
                                 "seed": int(row["seed"]), "steps": int(row["steps"]), "final_loss": float(row["final_loss"]),
                                 "accuracy": float(row["accuracy"]), "alignment": float(row["alignment"]),
                                 "seconds": float(row["seconds"])})
    return rows


def rerun_runs():
    """Baseline rerun from experiment I-01, used to confirm the experiment reproduces the original setup."""
    return _experiment_rows("baseline_rerun")


def runs():
    """{config: [row, ...]} with numeric fields converted."""
    out = defaultdict(list)
    with (RESULTS / "ablation_runs.csv").open() as f:
        for row in csv.DictReader(f):
            for key in ("warmup_steps", "scaled_attention", "seed", "steps"):
                row[key] = int(row[key])
            for key in ("final_loss", "accuracy", "alignment", "seconds"):
                row[key] = float(row[key])
            out[row["config"]].append(row)
    for row in _experiment_rows("no_ramp_capped"):
        out[row["config"]].append(row)
    return out


def curves():
    """{config: {seed: [(step, loss), ...]}}"""
    out = defaultdict(lambda: defaultdict(list))
    with (RESULTS / "loss_curves.csv").open() as f:
        for row in csv.DictReader(f):
            out[row["config"]][int(row["seed"])].append((int(row["step"]), float(row["loss"])))
    if (RAMP / "loss_curves.csv").exists():
        with (RAMP / "loss_curves.csv").open() as f:
            for row in csv.DictReader(f):
                if row["config"] == "no_ramp_capped":
                    out[row["config"]][int(row["seed"])].append((int(row["step"]), float(row["loss"])))
    return out


def environment():
    return json.loads((RESULTS / "environment.json").read_text())


def optimizer_constants():
    """Adam betas and epsilon exactly as written in the researcher's code."""
    source = (INPUTS / "code" / "transformer" / "10_lr_schedule" / "impl.py").read_text()
    match = re.search(r"betas=\(([\d.]+),\s*([\d.]+)\),\s*eps=([\de.+-]+)", source)
    return {"beta1": match.group(1), "beta2": match.group(2), "eps": match.group(3)}


def learning_rate(step, d_model, warmup):
    """Eq. 3 of Vaswani et al. (2017), as implemented in the researcher's code."""
    step = max(step, 1)
    return d_model ** -0.5 * min(step ** -0.5, step * warmup ** -1.5)
