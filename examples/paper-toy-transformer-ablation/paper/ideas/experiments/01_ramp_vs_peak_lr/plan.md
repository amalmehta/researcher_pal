# Plan: I-01 · Is it the warmup ramp, or the large initial learning rate?

> I7 of paper-ideas. The researcher approved idea I-01 (simulated; see `../../ideas.md`).

## Hypothesis
The paper attributes the failure of the no-warmup runs to the missing warmup. But with `w = 1`, Eq. 3 also starts at
a learning rate of 0.125, about 14× the baseline's peak, so the original ablation changes two things at once.
**H0:** only the *magnitude* matters, so skipping the ramp while capping the learning rate at the baseline's peak trains fine.
**H1:** the *ramp* matters, so even a capped learning rate fails without it.

## Which claim it tests
Contribution 1 and the title: "warmup is necessary". The abstract, results, limitations and conclusion depend on it.

## What would change the conclusion
| Outcome | Consequence for the paper |
|---|---|
| Capped no-ramp runs **learn** (like the baseline) | The claim must change from "warmup is necessary" to "a large initial learning rate is harmful". Title and abstract change. |
| Capped no-ramp runs **fail** (like no warmup) | The ramp itself matters at this peak learning rate. The claim gets stronger, and the confound is ruled out. |
| Mixed across seeds | Report per seed; the claim weakens to "warmup helps". |

## Design
- **New condition** `no_ramp_capped`: η(t) = d_model^-0.5 · min(t^-0.5, w^-0.5) with w = 200. It's identical to the baseline for t ≥ 200, and flat at the peak before that.
- **Control** `baseline_rerun`: Eq. 3 with w = 200. It must reproduce the original baseline results, checking the setup is the same.
- **Held fixed:** the researcher's model, data, optimizer, loss, scaled attention and 1,500 steps, imported read-only from `inputs/code/`.
- **Seeds:** 0, 1, 2 (the same as the original runs).
- **Metrics:** exact-match accuracy, alignment, final loss, loss curves (the same definitions as the paper).

## Compute estimate
- Pilot (`results/runs_pilot.csv`): 100 steps took about 3 s per run → about 45–60 s per 1,500-step run.
- 6 runs ≈ 5–6 min on CPU, within the budget (30 min per experiment).

## Outputs
`results/runs.csv`, `results/loss_curves.csv`, `results/environment.json`, then `findings.md`.
