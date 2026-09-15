# Plan: I-01 · Does scaling appear only for linear attachment?

> I7 of paper-ideas, learned-paper mode. The learner approved idea I-01 (simulated; see `../../ideas.md`).

## Hypothesis
¶10 (E9) states that with Π(k) ~ k^α, "simulations indicate that scaling is present only for α = 1", with no parameters or
figure. **Expected from the model:** sublinear attachment (α < 1) gives a faster-than-power-law tail and no dominant hub,
while superlinear attachment (α > 1) concentrates the edges on a few hubs.

## Which claim it tests
The E9 sentence, and with it the paper's framing that *linear* preferential attachment is what produces scale-free networks.

## What would change the conclusion
| Outcome | Reading |
|---|---|
| α = 1 gives γ ≈ 3; α = 0.5 gives a steeper tail with no big hub; α = 1.5 gives one hub holding a large, growing share | consistent with the paper's statement |
| α = 0.5 or 1.5 also gives a clean power law with a stable exponent | the "only α = 1" claim would be contradicted at this size |

## Design
- The model from ¶8 (complete-graph start, m₀ = m = 5, t = 20,000), with Π(k_i) ∝ k_i^α for α ∈ {0.5, 1.0, 1.5}.
- Seeds: 0, 1, 2. Tail fit: the learner's `fit_power_law_exponent` (k_min = 20) from `.solutions/03_final_scale_free`, imported read-only.
- Metrics:
  - fitted γ, which is only meaningful if the tail looks straight on the CCDF;
  - the largest degree;
  - the hub's share of all edge endpoints;
  - the number of vertices with degree ≥ 20;
  - degree CCDF plot.

## Compute estimate
- Pilot (`results/runs_pilot.csv`, t = 2,000): about 0.35 s per run. Cost grows about quadratically with t (it's O(N) per step), so expect about 20–40 s per run at t = 20,000.
- 9 runs ≈ 3–6 min on CPU, within the budget.

## Outputs
`results/runs.csv`, `results/degree_ccdf.csv`, `results/degree_ccdf.png`, then `findings.md`.
