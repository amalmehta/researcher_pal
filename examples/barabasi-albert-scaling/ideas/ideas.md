# Improvement ideas: *Emergence of Scaling in Random Networks* (Barabási & Albert, arXiv:cond-mat/9910332v1)

> Mode: **learned paper** · Generated 2026-09-15 after the final exercise (step 8) · Budget: CPU, 30 min per experiment,
> 2 h per round. Learner decisions in this example are simulated and marked **(simulated)**. Paragraph and equation labels
> (¶, E) follow [`concept_graph.md`](../concept_graph.md).

## Ranked ideas
| # | Idea | Type | Impact | Effort | Compute | Literature | Status |
|---|---|---|---|---|---|---|---|
| I-01 | Test "scaling only for α = 1" | evidence | High | 1 h | 3–6 min est., 69 s actual | related work | **done**: consistent with ¶10 |
| I-02 | Are Fig. 1's power laws really power laws? | reviewer | High | 2 h | < 1 min | related work | **noted** |
| I-03 | Check stationarity and the finite-size cutoff across network sizes | evidence | High | 1 h | ~5 min | related work | proposed |
| I-04 | Show model B instead of only describing it | reviewer | Medium | 1 h | ~3 min | related work | proposed |
| I-05 | Does the unstated starting graph matter? | evidence | Medium | 1 h | ~1 min | related work | proposed |
| I-06 | Say how γ_model = 2.9 ± 0.1 was measured | writing | Medium | 20 min | none | not applicable (presentation) | proposed |
| I-07 | Specify the starting edges and how "m different vertices" are drawn | writing | Medium | 15 min | none | not applicable (presentation) | proposed |
| I-08 | Test rich-get-richer on time-resolved data | direction | Medium | 1 day | < 5 min (needs a dataset) | related work | proposed |
| I-09 | Add fitness: can young vertices overtake old ones? | direction | Medium | 2 h | < 1 min | related work | proposed |
| I-10 | Add aging and initial attractiveness | direction | Low | 2 h | ~1 min | related work | proposed |
| I-11 | Fix the printed λ in the Erdős–Rényi formula | writing | Low | 5 min | none | not applicable (presentation) | proposed |

Coverage: writing (I-06, I-07, I-11) · evidence (I-01, I-03, I-05) · reviewer (I-02, I-04) · direction (I-08, I-09, I-10).

Compute estimates other than I-01 are not piloted. They scale from I-01's measured 5 s per α = 1 run at t = 20,000, with cost growing about as t².

## Details

### I-01 · Test "scaling only for α = 1"
- **Type:** evidence · **Impact:** High · **Effort:** 1 h · **Compute:** 3–6 min estimated from a pilot; 69 s actual
- **Motivated by:** ¶10 (E9): for Π(k) ~ k^α, the paper says simulations show scaling only for α = 1. No parameters, figure or numbers are given.
- **Idea:** grow the ¶8 model with α ∈ {0.5, 1.0, 1.5} (m₀ = m = 5, t = 20,000, 3 seeds). Measure the maximum-likelihood tail exponent, the
  largest degree and the hub's share of edge endpoints. Plan: [`experiments/01_nonlinear_attachment/plan.md`](experiments/01_nonlinear_attachment/plan.md).
- **Why it matters:** it is the paper's only evidence that the attachment must be *linear*, and it rests on one unillustrated sentence.
- **What would change the conclusion:** a clean, stable power law at α = 0.5 or 1.5 would contradict the sentence at this size.
- **Result:** consistent with the paper.

  | α | Fitted γ | Largest degree | Hub share | CCDF shape |
  |---|---|---|---|---|
  | 0.5 | 3.91–4.00 | 90–104 | 0.045–0.052% | bends down: lighter than a power law, no hubs |
  | 1.0 | 2.92–2.93 | 463–644 | 0.23–0.32% | straight, parallel to k⁻³ (paper: 2.9 ± 0.1) |
  | 1.5 | 1.72–1.77 (not meaningful) | 16,400–16,812 | 8.2–8.4% | plateau, then one hub linked to 82–84% of all vertices |

  ![Degree CCDF, seed 0](experiments/01_nonlinear_attachment/results/degree_ccdf.png)

  The two sides of α = 1 fail in qualitatively different ways. This single size (t = 20,000) can't show whether the hub's share keeps growing.
  Details: [`findings.md`](experiments/01_nonlinear_attachment/findings.md). A natural follow-up is the same check for the directed-links
  claim γ(p) = 3 − p (¶10), which wasn't searched or run.
- **Literature:** related work. *Connectivity of Growing Random Networks* (Krapivsky, 2000;
  [doi:10.1103/physrevlett.85.4629](https://doi.org/10.1103/physrevlett.85.4629)) and *Organization of growing random networks* (Krapivsky, 2001;
  [doi:10.1103/physreve.63.066123](https://doi.org/10.1103/physreve.63.066123)) are verified records with titles only. The concept graph's claim that
  the first one analyzes sublinear and superlinear attachment comes from background knowledge, so read it before citing.
- **Status:** approved (simulated) · done

### I-02 · Are Fig. 1's power laws really power laws?
- **Type:** reviewer · **Impact:** High · **Effort:** 2 h · **Compute:** < 1 min (on simulated networks)
- **Motivated by:** Fig. 1 caption: the dashed lines "have slopes" 2.3, 2.1 and 4. They are reference lines, and no fitting procedure,
  fitted range or goodness-of-fit test is reported (concept graph, `empirical_scale_free`). ¶4's motivation depends on these being power laws.
- **Idea:** *A reviewer may say "a straight-looking log-log plot is not evidence of a power law" →* fit the tail by maximum likelihood with
  a goodness-of-fit test, and compare the power law against log-normal and stretched-exponential fits by likelihood ratio. As an exercise, first
  apply it to the learner's own α = 1 network, where the answer is known, then to the actor or web data if the learner obtains them.
- **Why it matters:** if an alternative fits as well, the paper's motivation weakens, though the model itself is unaffected.
- **What would change the conclusion:** a power law rejected or not preferred for the empirical networks.
- **Literature:** related work.
  - *Power-Law Distributions in Empirical Data* (Clauset, 2009; [doi:10.1137/070710111](https://doi.org/10.1137/070710111)). Abstract read: it
    combines maximum-likelihood fitting with Kolmogorov–Smirnov and likelihood-ratio tests, and warns that least-squares fits can be substantially inaccurate.
  - *Scale-free networks are rare* (Broido, 2019; [doi:10.1038/s41467-019-08746-5](https://doi.org/10.1038/s41467-019-08746-5)). Abstract read: across
    nearly 1,000 networks, strongly scale-free structure is rare, and log-normal fits are often as good or better.
  - *Rare and everywhere: Perspectives on scale-free networks* (Holme, 2019; [doi:10.1038/s41467-019-09038-8](https://doi.org/10.1038/s41467-019-09038-8)): title only, a perspective on that debate.
- **Status:** approved (simulated) · noted in [`concept_graph.md`](../concept_graph.md#open-questions-and-extensions)

### I-03 · Check stationarity and the finite-size cutoff across network sizes
- **Type:** evidence · **Impact:** High · **Effort:** 1 h · **Compute:** ~5 min (3 sizes × 3 seeds, dominated by t = 80,000 at ~80 s per run)
- **Motivated by:** ¶8 concludes that P(k) is independent of time from Fig. 2A, which shows only t = 150,000 and t = 200,000, a factor of 1.33 apart.
- **Idea:** α = 1 at t ∈ {5,000, 20,000, 80,000}, 3 seeds. Overlay the CCDFs, refit γ at each size, and check that the largest degree grows
  about as t^0.5, as E6 predicts for the earliest vertices.
- **Why it matters:** "stationary" is the property that lets one model describe networks of very different sizes (¶8).
- **What would change the conclusion:** a γ that drifts with t would mean stationarity holds only asymptotically. A largest degree off
  t^0.5 would mean the cutoff, not the exponent, dominates tail fits at these sizes.
- **Literature:** related work (both title only).
  - *Size-dependent degree distribution of a scale-free growing network* (Dorogovtsev, 2001; [doi:10.1103/physreve.63.062101](https://doi.org/10.1103/physreve.63.062101))
  - *Simple rules govern finite-size effects in scale-free networks* (Cuenda, 2011; [doi:10.1209/0295-5075/95/38002](https://doi.org/10.1209/0295-5075/95/38002))
- **Status:** proposed

### I-04 · Show model B instead of only describing it
- **Type:** reviewer · **Impact:** Medium · **Effort:** 1 h · **Compute:** ~3 min (N = 1,000, up to 10⁶ steps)
- **Motivated by:** ¶9 says model B, with fixed N and no growth, shows power-law scaling at early times and fills in after T ≃ N² steps.
  Fig. 2 has no panel for it: (A) is the full model, (B) model A, (C) degree growth. The claim that *growth* is necessary rests on this unshown run.
- **Idea:** *A reviewer may say "the necessity of growth is asserted, not shown" →* plot model B's P(k) at t = N, 10N and 100N for
  N = 1,000. State how the first step works, since with no edges every k_j = 0 (the same 0/0 issue as the full model).
- **Why it matters:** half of the ablation argument (¶9) has no figure.
- **What would change the conclusion:** a model B distribution that looked stationary for a long window would weaken "growth is needed".
- **Literature:** related work. *Preferential attachment without vertex growth: Emergence of the giant component* (Janson, 2021;
  [doi:10.1214/20-aap1610](https://doi.org/10.1214/20-aap1610)): title only. It studies preferential attachment in the fixed-vertex setting of model B.
- **Status:** proposed

### I-05 · Does the unstated starting graph matter?
- **Type:** evidence · **Impact:** Medium · **Effort:** 1 h · **Compute:** ~1 min
- **Motivated by:** ¶8 starts from "a small number (m₀) of vertices" without saying which edges they have, and "mt edges" suggests none,
  which makes Π undefined at the first step (concept graph, `ba_model`).
- **Idea:** compare a complete graph, a ring and a star on m₀ = 5, plus a complete graph on m₀ = 50. Use α = 1, t = 20,000 and 3 seeds, and
  measure γ, the degrees of the first vertices, and the largest degree.
- **Why it matters:** it decides whether the paper's simulations are reproducible from the text or depend on an unreported choice.
- **What would change the conclusion:** a start-dependent γ at this size. If only the earliest vertices differ, the omission is cosmetic.
- **Literature:** related work (both title only, and both directly on topic, so read them before treating any result as new).
  - *The effect of the initial network configuration on preferential attachment* (Berset, 2013; [doi:10.1140/epjb/e2013-30998-1](https://doi.org/10.1140/epjb/e2013-30998-1))
  - *Network growth with arbitrary initial conditions: Degree dynamics for uniform and preferential attachment* (Fotouhi, 2013; [doi:10.1103/physreve.88.062801](https://doi.org/10.1103/physreve.88.062801))
- **Status:** proposed

### I-06 · Say how γ_model = 2.9 ± 0.1 was measured
- **Type:** writing · **Impact:** Medium · **Effort:** 20 min · **Compute:** none
- **Motivated by:** ¶8 reports γ_model = 2.9 ± 0.1, and the Fig. 2A caption says only that the dashed line's slope is 2.9. No estimator,
  fitted range, number of runs or meaning of "± 0.1" is given.
- **Idea:** state the estimator, the k range, the number of runs, and whether ± 0.1 is a standard error, a spread over runs or a visual range.
- **Why it matters:** readers can't tell whether 2.9 differs from the analytic 3 (E8), or reproduce the number.
- **Literature:** not applicable (presentation). The choice of estimator itself is covered by I-02.
- **Status:** proposed

### I-07 · Specify the starting edges and how "m different vertices" are drawn
- **Type:** writing · **Impact:** Medium · **Effort:** 15 min · **Compute:** none
- **Motivated by:** ¶8 says a new vertex links to "m different vertices" with Π(k_i) = k_i/Σ_j k_j, but gives neither the initial edges nor the
  sampling rule without replacement (concept graph, `preferential_attachment` and `ba_model`).
- **Idea:** one sentence naming the starting graph, and one saying targets are drawn one at a time with Π renormalized over the vertices not yet chosen, or whichever rule was used.
- **Why it matters:** it is the minimum needed to reimplement the model. I-05 tests whether it changes the results.
- **Literature:** not applicable (presentation).
- **Status:** proposed

### I-08 · Test rich-get-richer on time-resolved data
- **Type:** direction · **Impact:** Medium · **Effort:** 1 day · **Compute:** < 5 min, but it needs a public dated network (downloading one needs the learner's approval)
- **Motivated by:** ¶10: k_i(t) = m(t/t_i)^0.5 is a scaling property the authors say could be tested directly once time-resolved connectivity data exist.
- **Idea:** on a dated citation or collaboration network, estimate the attachment rate as a function of degree (is Π(k) linear?) and the growth of k_i(t) for vertices of different ages.
- **Why it matters:** it tests the mechanism, not just the degree distribution it produces.
- **Literature:** related work. *A Preferential Attachment Paradox: How Preferential Attachment Combines with Growth to Produce Networks with Log-normal
  In-degree Distributions* (Sheridan, 2018; [doi:10.1038/s41598-018-21133-2](https://doi.org/10.1038/s41598-018-21133-2)). Abstract read: a citation network
  reported to grow by preferential attachment still has a log-normal in-degree distribution, which the authors trace to how attachment was measured.
  So measuring Π(k) from data is subtle.
- **Status:** proposed

### I-09 · Add fitness: can young vertices overtake old ones?
- **Type:** direction · **Impact:** Medium · **Effort:** 2 h · **Compute:** < 1 min
- **Motivated by:** ¶10: older vertices gain connectivity "at the expense of the younger" ones, because in the model a vertex's degree is set
  by its arrival time alone. The concept graph (`ba_model`) notes that real hubs can be young.
- **Idea:** give each vertex a fitness η_i drawn from a distribution, with Π ∝ η_i k_i. Measure how often a late arrival ends among the top
  10 degrees, and how P(k) changes.
- **Literature:** related work (both title only).
  - *Mechanisms of complex network growth: Synthesis of the preferential attachment and fitness models* (Golosovsky, 2018; [doi:10.1103/physreve.97.062310](https://doi.org/10.1103/physreve.97.062310))
  - *Intrinsic fitness and preferential attachment in scale-free networks* (Liu, 2006; [doi:10.1109/icact.2006.206395](https://doi.org/10.1109/icact.2006.206395))

  The concept graph cites Bianconi & Barabási (2001) from background knowledge. This search didn't return it, so that citation is unverified here.
- **Status:** proposed

### I-10 · Add aging and initial attractiveness
- **Type:** direction · **Impact:** Low · **Effort:** 2 h · **Compute:** ~1 min
- **Motivated by:** E6: every vertex keeps gaining links forever, as k_i ∝ t^0.5, while ¶11 invites system-specific extensions.
- **Idea:** multiply Π by an aging factor τ_i^(−ν) (τ_i is the vertex's age) and add an initial attractiveness A, then find the ν range where the power law survives.
- **Why it matters:** it is a good learning exercise, but not a new question. The model below already exists.
- **Literature:** related work. *Preferential attachment network model with aging and initial attractiveness* (Peng, 2022;
  [doi:10.1088/1572-9494/ac5322](https://doi.org/10.1088/1572-9494/ac5322)). Abstract read: it generalizes the growing model with Π ∝ (k_i + A)·τ_i^(−α).
- **Status:** proposed

### I-11 · Fix the printed λ in the Erdős–Rényi formula
- **Type:** writing · **Impact:** Low · **Effort:** 5 min · **Compute:** none
- **Motivated by:** ¶5 (E2): the printed λ depends on k, so it can't be the Poisson parameter (concept graph, `er_random_graph`).
- **Idea:** replace it with λ = (N − 1)p ≈ Np, and keep the printed expression as the expected number of vertices with degree k.
- **Literature:** not applicable (presentation).
- **Status:** proposed (the correction is already recorded as a gotcha in the concept graph)

## Literature searched
All queries used keywords only. Crossref answered every query, while arXiv (HTTP 429 or timeouts) and Semantic Scholar (HTTP 429) answered none,
despite retries with backoff. Crossref returns abstracts for only a few records, so most links above are judged from titles and marked that way.

| Group | Queries | Services that answered | Results |
|---|---|---|---|
| nonlinear attachment | `nonlinear preferential attachment`; `Krapivsky Redner Leyvraz connectivity growing random networks` | Crossref 2/2 · arXiv 0/2 · Semantic Scholar 0/2 | [literature/nonlinear_attachment.md](literature/nonlinear_attachment.md) |
| power-law evidence | `scale-free networks are rare`; `power-law distributions empirical data` | Crossref 2/2 · arXiv 0/2 · Semantic Scholar 0/2 | [literature/power_law_evidence.md](literature/power_law_evidence.md) |
| fitness and aging | `fitness model competition scale-free networks`; `aging vertices preferential attachment` | Crossref 2/2 · arXiv 0/2 · Semantic Scholar 0/2 | [literature/fitness_aging.md](literature/fitness_aging.md) |
| model assumptions | `preferential attachment initial conditions network growth`; `finite size effects scale-free network degree cutoff`; `preferential attachment fixed number of vertices without growth` | Crossref 3/3 · arXiv 0/3 · Semantic Scholar 0/3 | [literature/model_assumptions.md](literature/model_assumptions.md) |

Many Crossref hits were off-topic (e.g. log-returns, polydisperse fluids, software networks). Only the records named in the cards were judged relevant.

## Log
- 2026-09-15 · I5 pause. The learner approved **I-01** (run) and **I-02** (note) **(simulated)**.
- 2026-09-15 · I7 **I-01 run**: 9 runs, 69 s wall time, within budget. The result is consistent with ¶10: only α = 1 gives a straight tail
  (γ = 2.92–2.93), α = 0.5 gives no hubs, and α = 1.5 gives one dominant hub. Findings are in the card and in `findings.md`. The learner's solution code was
  imported read-only, and no file in `exercises/` or `.solutions/` changed after the experiment folder was created.
- 2026-09-15 · I6 **I-02 noted** in `concept_graph.md` under "Open questions and extensions", together with the I-01 result. The Mermaid map was not changed.
