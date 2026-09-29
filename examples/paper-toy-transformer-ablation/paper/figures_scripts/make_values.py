"""Write generated/values.tex (one \\newcommand per number used in the prose) and sources.md."""
import math
import statistics

import data

rows = data.runs()
env = data.environment()
opt = data.optimizer_constants()
values = []  # (macro, LaTeX value, meaning, source)


def add(macro, value, meaning, source):
    assert macro.isalpha(), macro
    values.append((macro, value, meaning, source))


def pct(x):
    return "%.1f" % (100 * x)


def thousands(n):
    return "{:,}".format(n).replace(",", "{,}")


SUFFIX = {"baseline": "Baseline", "no_scaling": "NoScaling", "no_warmup": "NoWarmup", "no_warmup_no_scaling": "NoWarmupNoScaling"}
CSV = "inputs/results/ablation_runs.csv"
RAMP_SRC = "paper/ideas/experiments/01_ramp_vs_peak_lr/results/runs.csv"
SUFFIX["no_ramp_capped"] = "NoRampCapped"
for config, suffix in SUFFIX.items():
    if config not in rows:
        continue
    acc = [r["accuracy"] for r in rows[config]]
    align = [r["alignment"] for r in rows[config]]
    loss = [r["final_loss"] for r in rows[config]]
    where = "%s: config=%s" % (RAMP_SRC if config == "no_ramp_capped" else CSV, config)
    add("valAcc" + suffix, pct(statistics.mean(acc)), "mean exact-match accuracy (%%), %s" % config, where + ", mean(accuracy)×100")
    add("valAccMin" + suffix, pct(min(acc)), "lowest seed accuracy (%%), %s" % config, where + ", min(accuracy)×100")
    add("valAccMax" + suffix, pct(max(acc)), "highest seed accuracy (%%), %s" % config, where + ", max(accuracy)×100")
    add("valAlign" + suffix, pct(statistics.mean(align)), "mean alignment (%%), %s" % config, where + ", mean(alignment)×100")
    add("valLoss" + suffix, "%.2f" % statistics.mean(loss), "mean final training loss, %s" % config, where + ", mean(final_loss)")

all_rows = [r for config, group in rows.items() if config != "no_ramp_capped" for r in group]  # the original ablation
no_warmup_rows = [r for r in all_rows if r["warmup_steps"] == 1]
seeds = sorted({r["seed"] for r in all_rows})
add("valSeeds", str(len(seeds)), "seeds per configuration", CSV + ": distinct seed values")
add("valRuns", str(len(all_rows)), "total runs", CSV + ": number of rows")
add("valRunsNoWarmup", str(len(no_warmup_rows)), "runs without warmup", CSV + ": rows with warmup_steps=1")
add("valWarmup", str(rows["baseline"][0]["warmup_steps"]), "warmup steps in the warmup configurations", CSV + ": warmup_steps for config=baseline")
add("valSteps", thousands(env["steps"]), "training steps per run", "inputs/results/environment.json: steps")
add("valSecondsMin", "%d" % math.floor(min(r["seconds"] for r in all_rows)), "fastest run (s)", CSV + ": floor(min(seconds))")
add("valSecondsMax", "%d" % math.ceil(max(r["seconds"] for r in all_rows)), "slowest run (s)", CSV + ": ceil(max(seconds))")
add("valMinutesTotal", "%.0f" % (sum(r["seconds"] for r in all_rows) / 60), "total training time of all runs (min)", CSV + ": sum(seconds)/60")

for key, macro, meaning in [
    ("d_model", "valDModel", "model width d_model"), ("heads", "valHeads", "attention heads"), ("d_ff", "valDff", "feed-forward width"),
    ("batch_size", "valBatch", "sequences per training batch"), ("sequence_length", "valSeqLen", "sequence length"),
    ("vocab_size", "valVocab", "vocabulary size"), ("label_smoothing", "valLabelSmoothing", "label smoothing"),
    ("eval_sequences", "valEvalSeqs", "evaluation sequences"), ("torch_threads", "valThreads", "PyTorch CPU threads"),
    ("torch", "valTorch", "PyTorch version"),
]:
    add(macro, str(env[key]), meaning, "inputs/results/environment.json: %s" % key)
add("valDk", str(env["d_model"] // env["heads"]), "key dimension d_k = d_model / heads", "inputs/results/environment.json: d_model // heads")
add("valChanceAlign", "%.1f" % (100.0 / env["sequence_length"]), "alignment expected by chance: 1 / sequence length (%)", "inputs/results/environment.json: 100 / sequence_length")

LR_SRC = "inputs/code/transformer/10_lr_schedule/impl.py"
add("valBetaOne", opt["beta1"], "Adam beta1", LR_SRC + ": betas")
add("valBetaTwo", opt["beta2"], "Adam beta2", LR_SRC + ": betas")
exponent = int(round(math.log10(float(opt["eps"]))))
add("valEps", "10^{%d}" % exponent, "Adam epsilon (math mode)", LR_SRC + ": eps")
d_model, warmup = env["d_model"], rows["baseline"][0]["warmup_steps"]
add("valStartLRNoWarmup", "%.3f" % data.learning_rate(1, d_model, 1), "learning rate at step 1 without warmup",
    LR_SRC + ": transformer_lr(1, d_model, warmup_steps=1)")
peak = data.learning_rate(warmup, d_model, warmup)
mantissa_exp = int(math.floor(math.log10(peak)))
add("valPeakLR", "%.1f\\times10^{%d}" % (peak / 10 ** mantissa_exp, mantissa_exp), "peak learning rate with warmup (math mode)",
    LR_SRC + ": transformer_lr(warmup, d_model, warmup)")

# When do the no-warmup runs stop improving? The first logged step at which every such run is within 0.15 of
# the median of its own remaining losses; then the range and mean of their losses from that step on.
curves = data.curves()
stalled = [points for config in ("no_warmup", "no_warmup_no_scaling") for points in curves[config].values()]
stall_index = next(i for i in range(len(stalled[0]))
                   if all(abs(p[i][1] - statistics.median(l for _, l in p[i:])) <= 0.15 for p in stalled))
after = [loss for p in stalled for _, loss in p[stall_index:]]
NOWARM = "inputs/results/loss_curves.csv: configs without warmup"
add("valStallStep", str(stalled[0][stall_index][0]), "first step at which every no-warmup run is within 0.15 of the median of its remaining losses", NOWARM)
add("valStallLow", "%.2f" % min(after), "lowest loss of no-warmup runs from that step on", NOWARM + ", steps >= valStallStep")
add("valStallHigh", "%.2f" % max(after), "highest loss of no-warmup runs from that step on", NOWARM + ", steps >= valStallStep")
add("valPlateauLoss", "%.2f" % statistics.mean(after), "mean loss of no-warmup runs from that step on", NOWARM + ", steps >= valStallStep")

if rows.get("no_ramp_capped"):
    ramp_rows, reruns = rows["no_ramp_capped"], data.rerun_runs()
    original = {r["seed"]: r for r in rows["baseline"]}
    add("valRampRuns", str(len(ramp_rows)), "runs of the capped no-ramp control (experiment I-01)", RAMP_SRC + ": config=no_ramp_capped")
    THRESHOLD = 0.9
    solved = sum(r["accuracy"] >= THRESHOLD for r in ramp_rows)
    add("valSolveThreshold", "%d" % round(100 * THRESHOLD), "accuracy counted as solving the task (%)", "make_values.py: analysis choice (THRESHOLD)")
    add("valRampSolved", str(solved), "control runs that solve the task", RAMP_SRC + ": config=no_ramp_capped, accuracy >= 0.9")
    add("valRampUnsolved", str(len(ramp_rows) - solved), "control runs that do not", RAMP_SRC + ": config=no_ramp_capped, accuracy < 0.9")
    add("valRampSecondsMin", "%d" % math.floor(min(r["seconds"] for r in ramp_rows)), "fastest control run (s)", RAMP_SRC + ": floor(min(seconds))")
    add("valRampSecondsMax", "%d" % math.ceil(max(r["seconds"] for r in ramp_rows)), "slowest control run (s)", RAMP_SRC + ": ceil(max(seconds))")
    diff = max(max(abs(r["accuracy"] - original[r["seed"]]["accuracy"]), abs(r["final_loss"] - original[r["seed"]]["final_loss"])) for r in reruns)
    add("valRerunMaxDiff", "%.3f" % diff, "largest accuracy or final-loss difference, baseline rerun vs. original baseline",
        RAMP_SRC + ": config=baseline_rerun vs " + CSV)

tex = "% Generated by figures_scripts/make_values.py. Do not edit by hand.\n" + "".join(
    "\\newcommand{\\%s}{%s}\n" % (macro, value) for macro, value, _, _ in values)
(data.VENUE_DIR / "generated").mkdir(exist_ok=True)
(data.VENUE_DIR / "generated" / "values.tex").write_text(tex)

md = ["# Sources", "", "Generated by `figures_scripts/make_values.py`; regenerate, don't edit.", "",
      "## Numbers in the prose", "", "| Macro | Value | Meaning | Source |", "|---|---|---|---|"]
md += ["| `\\%s` | %s | %s | %s |" % (m, v.replace("|", "\\|"), meaning, src) for m, v, meaning, src in values]
md += ["", "## Figures and tables", "", "| Output | Script | Data |", "|---|---|---|",
       "| `generated/tables/results.tex` | `figures_scripts/results_table.py` | %s |" % CSV,
       "| `figures/loss_curves.pdf` | `figures_scripts/loss_curves.py` | inputs/results/loss_curves.csv, paper/ideas/experiments/01_ramp_vs_peak_lr/results/loss_curves.csv |",
       "| `figures/ablation_grid.pdf` | `figures_scripts/ablation_grid.py` (Graphviz) | %s (warmup values) |" % CSV,
       "| `figures/lr_schedule_concept.pdf` | `figures_scripts/lr_schedule_concept.py` (SVG → PDF) | environment.json (d_model, steps), %s (warmup) |" % CSV,
       "", "## Hand-typed numbers", "", "None: every number in `sections/` comes from a macro above.", ""]
(data.VENUE_DIR / "sources.md").write_text("\n".join(md))
print("wrote %d values" % len(values))
