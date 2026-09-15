# Findings: I-01 · Does scaling appear only for linear attachment?

> Every number below is read from `results/runs.csv` and `results/degree_ccdf.csv`. Settings: complete-graph start,
> m₀ = m = 5, t = 20,000 (20,005 vertices, 100,010 edges), seeds 0–2; tail fit by the learner's maximum-likelihood
> `fit_power_law_exponent` (continuous approximation, k_min = 20).

![Degree CCDF, seed 0](results/degree_ccdf.png)

## Outcome: consistent with the paper's statement (the first row of the plan's outcome table)

| α | Fitted γ (k_min = 20) | Largest degree | Hub share of edge endpoints | Vertices with k ≥ 20 | Seconds per run |
|---|---|---|---|---|---|
| 0.5 | 3.91–4.00 | 90–104 | 0.045–0.052% | 1,535–1,579 | 4.9–5.3 |
| 1.0 | 2.92–2.93 | 463–644 | 0.23–0.32% | 1,443–1,456 | 4.8–5.4 |
| 1.5 | 1.72–1.77 | 16,400–16,812 | 8.2–8.4% | 71–82 | 11.6–12.3 |

Ranges are over the three seeds.

- **α = 1.** The CCDF is close to a straight line parallel to the slope −2 guide (P(k) ~ k⁻³) from k ≈ 10 to k ≈ 300. The fitted
  γ = 2.92–2.93 agrees with the paper's simulated γ = 2.9 ± 0.1 (¶8) and sits just below the analytic 3 (E8).
- **α = 0.5.** The CCDF bends down on log-log axes, and the largest degree stays near 100 in every seed. A fitted γ ≈ 4 exists,
  but the curve isn't a straight line, so it doesn't describe a power law. The tail is lighter than any power law over this
  range, as expected for a stretched exponential. Whether it truly is one wasn't tested.
- **α = 1.5.** One vertex gets an edge from 82–84% of all vertices (degree 16,400–16,812 of a possible 20,004). Only 71–82
  vertices reach degree 20, and the CCDF is a flat plateau ending in a jump at the hub. The fitted γ ≈ 1.7 is not
  meaningful here: the network is a hub attached to almost everything, not scale-free.
- **Across seeds** the pattern is the same for every α. Only the size of the largest hub at α = 1 varies noticeably (463–644).

## What it means for the learner
- The one-sentence claim in ¶10 (E9) holds up at this size. Of the three exponents tried, only linear attachment gives a
  straight power-law tail with γ near 3.
- It isn't a knife-edge result in the sense of "any α ≠ 1 gives a slightly different exponent". The two sides fail in
  *qualitatively different* ways: a light tail with no hubs, or a single dominant hub.
- **Related work.** *Connectivity of Growing Random Networks* (Krapivsky, 2000; [doi:10.1103/physrevlett.85.4629](https://doi.org/10.1103/physrevlett.85.4629)) was returned and verified by Crossref.
  Only its title was available from the search. The concept graph attributes the sublinear and superlinear behaviour to this
  paper from background knowledge, so read it before relying on the match.

## Compute
- Total wall time 69 s, well within the 30-min budget and faster than the plan's 3–6 min estimate. Per-run cost was 5–12 s,
  not the 20–40 s extrapolated from the pilot. The O(N)-per-step sampling is vectorized in numpy, so the quadratic term was smaller than assumed.

## Not tested
- **Only one network size.** The plan's expectation of a *growing* hub share for α = 1.5 wasn't checked (it needs several t).
- **No other values of α.** Values between 0.5 and 1.5 weren't tried, so the width of the "near-linear" range is unknown.
- **A single tail-fitting method.** The fit is the learner's estimator at a single k_min.
