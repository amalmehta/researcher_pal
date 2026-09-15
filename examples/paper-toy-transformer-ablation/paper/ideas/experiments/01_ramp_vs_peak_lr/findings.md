# Findings: I-01 · Is it the warmup ramp, or the large initial learning rate?

> Every number below is read from `results/runs.csv`, `results/loss_curves.csv` and `results/environment.json`
> (Python 3.9.1, PyTorch 2.2.2, 8 threads, 1,500 steps, seeds 0–2, w = 200, d_model = 64).

## Outcome: mixed (the third row of the plan's outcome table)

| Config | Seed | Initial LR | Peak LR | Accuracy | Alignment | Final loss | Seconds |
|---|---|---|---|---|---|---|---|
| baseline_rerun | 0 | 4.42e-5 | 8.84e-3 | 100.0% | 100.0% | 0.526 | 36 |
| baseline_rerun | 1 | 4.42e-5 | 8.84e-3 | 99.4% | 99.98% | 0.531 | 216 |
| baseline_rerun | 2 | 4.42e-5 | 8.84e-3 | 100.0% | 100.0% | 0.526 | 65 |
| no_ramp_capped | 0 | 8.84e-3 | 8.84e-3 | 0.0% | 19.9% | 1.896 | 47 |
| no_ramp_capped | 1 | 8.84e-3 | 8.84e-3 | 0.0% | 17.1% | 2.075 | 1,051 |
| no_ramp_capped | 2 | 8.84e-3 | 8.84e-3 | 98.6% | 95.3% | 0.554 | 57 |

- **The setup is unchanged.** The baseline rerun matches the original baseline in `inputs/results/ablation_runs.csv`
  (largest difference in accuracy or final loss: 0.000, `\valRerunMaxDiff`).
- **The capped control solved the task in 1 of 3 seeds** (accuracy of at least 90%). The other two seeds end at 0% accuracy, and their
  alignment (19.9% and 17.1%) is near the 12.5% chance level.
- **Loss curves** (training loss at selected steps):

  | Run | 100 | 200 | 300 | 500 | 800 | 1000 | 1200 | 1500 |
  |---|---|---|---|---|---|---|---|---|
  | baseline_rerun, seed 0 | 1.27 | 0.79 | 0.55 | 0.54 | 0.53 | 0.53 | 0.53 | 0.53 |
  | no_ramp_capped, seed 0 | 2.34 | 2.26 | 2.21 | 2.18 | 2.10 | 1.99 | 2.01 | 1.86 |
  | no_ramp_capped, seed 1 | 2.36 | 2.38 | 2.28 | 2.21 | 2.12 | 2.08 | 2.06 | 2.05 |
  | no_ramp_capped, seed 2 | 2.29 | 2.16 | 2.06 | 1.73 | 1.27 | 0.69 | 0.54 | 0.53 |

  The baseline settles by step 300. Seed 2 of the control gets there only at about step 1,200. Seeds 0 and 1 fall slowly and
  finish far above the baseline, so longer training might rescue some of them. That wasn't tested.

## What it means for the paper
- **H0 (only the magnitude matters) is not supported.** The control never exceeds the baseline's peak learning rate, yet 2 of 3
  seeds fail within the training budget. The failures without warmup aren't explained by the 0.125 initial learning rate alone.
- **H1 (the ramp matters) holds only partly.** One seed learns without the ramp, just much later.
- **This undercuts a claim.** "Warmup is necessary" in the title, contribution 1, abstract and conclusion is too strong. The
  plan's reading for this outcome is "warmup helps". The evidence supports something slightly stronger for this setting: no run
  without warmup learned, and removing only the ramp left 2 of 3 seeds unsolved.
- **Stop-and-tell (I7 step 4).** Work stopped here before any claim was edited. The researcher in this example is simulated.
  The simulated decision was to reword to "warmup matters", report the control per seed and add the seed sensitivity to Limitations. The user then confirmed
  keeping this revision (2026-09-15).

## Compute
- Total wall time 1,479 s (24.7 min). That's within the 30-min budget, but about 4× the plan's estimate (5–6 min).
- Cause: the CPU was shared with the literature searches and the Barabási–Albert experiment. Seed 1 of the control took
  1,051 s, compared with 47–57 s for the other control seeds. Run times in the paper (`\valRampSecondsMin`–`\valRampSecondsMax`)
  therefore describe this shared machine, and the paper says so.

## Not tested
Longer training, a lower learning-rate cap, more seeds, and whether the control's failures depend on attention scaling
(the control always uses scaled attention).
