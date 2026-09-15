# Improvement ideas: *In a Small Transformer, Warmup Is Necessary but Attention Scaling Is Not*

> Mode: **own draft** · Generated 2026-09-15 after the first clean P7 (both `neurips2026/` and `iclr2027/`) · Budget: CPU,
> 30 min per experiment, 2 h per round. Researcher decisions in this example are simulated and marked **(simulated)**.

## Ranked ideas
| # | Idea | Type | Impact | Effort | Compute | Literature | Status |
|---|---|---|---|---|---|---|---|
| I-01 | Separate the warmup ramp from the learning-rate magnitude | evidence | High | 1 h | ~6 min est., 24.7 min actual | related work | **done**: mixed, claims revised (see card) |
| I-02 | Position against recent warmup analyses | reviewer | High | 2 h | none | related work | proposed |
| I-03 | Sweep d_k to test the scaling claim where it should matter | evidence | High | 3 h | ~40 min (over budget, shrink or ask) | related work | proposed |
| I-04 | Give the chance level for alignment | writing | Medium | 15 min | none | not applicable (presentation) | **applied** |
| I-05 | Quantify the loss spikes hidden by the final metrics | evidence | Medium | 45 min | none (existing curves) | related work | proposed |
| I-06 | Stop Figure 1's grid from being scaled up | writing | Medium | 20 min | none | not applicable (presentation) | proposed |
| I-07 | Find the minimum warmup length | evidence | Medium | 1 h | ~17 min | related work | proposed |
| I-08 | Pre-empt "three seeds, one toy task" | reviewer | Medium | 2 h | ~20 min | no close match (Crossref only) | proposed |
| I-09 | Measure attention entropy as the mechanism | direction | Medium | 2 h | ~5 min | related work | proposed |
| I-10 | Does pre-LN remove the need for warmup here? | direction | Medium | 2 h | ~6 min | related work | proposed |
| I-11 | Name the alignment metric for what it is | writing | Low | 15 min | none | not applicable (presentation) | proposed |
| I-12 | Can an optimizer fix replace warmup? | direction | Low | 1 h | ~3 min | related work | proposed |

Coverage: writing (I-04, I-06, I-11) · evidence (I-01, I-03, I-05, I-07) · reviewer (I-02, I-08) · direction (I-09, I-10, I-12).

## Details

### I-01 · Separate the warmup ramp from the learning-rate magnitude
- **Type:** evidence · **Impact:** High · **Effort:** 1 h · **Compute:** ~6 min (pilot: 100 steps ≈ 3 s per run)
- **Motivated by:** `sections/setup.tex`, Ablation: "which removes the ramp so the learning rate starts at 0.125 instead of peaking at
  8.8×10⁻³ after 200 steps". The no-warmup condition changes two things at once: it removes the ramp **and** starts about 14× higher.
- **Idea:** add a no-ramp control whose learning rate is capped at the baseline's peak (flat for the first 200 steps, then identical
  to the baseline), plus a baseline rerun to confirm the setup is unchanged. Plan: `experiments/01_ramp_vs_peak_lr/plan.md`.
- **Why it matters:** the title and contribution 1 attribute the failure to *warmup*. A reviewer can attribute it to the large
  initial learning rate instead.
- **What would change the conclusion:** if the capped runs learn, the claim becomes "a large initial learning rate is harmful". If they fail, the
  ramp itself matters and the confound is ruled out.
- **Literature:** related work. *Why Warmup the Learning Rate? Underlying Mechanisms and Improvements* (Kalra, 2024;
  [doi:10.52202/079017-3549](https://doi.org/10.52202/079017-3549)) and *Analyzing & Reducing the Need for Learning Rate Warmup in GPT Training*
  (Kosson, 2024; [doi:10.52202/079017-0096](https://doi.org/10.52202/079017-0096)) both study why warmup is needed. Relevance is judged from
  titles only (the search returned no abstracts), so read both before citing.
- **Result:** **mixed**, the third row of the plan's outcome table. The baseline rerun reproduced the original runs exactly.
  The capped no-ramp control solved the task in 1 of 3 seeds: accuracy 0.0%, 0.0% and 98.6%, final loss 1.90, 2.08 and 0.55,
  against 100/99.4/100% and 0.53 for the baseline. So the large initial learning rate doesn't explain the failure by
  itself, because the ramp matters even at a capped learning rate. But the ramp isn't strictly necessary for every seed either.
  Details and per-seed loss curves: [`experiments/01_ramp_vs_peak_lr/findings.md`](experiments/01_ramp_vs_peak_lr/findings.md).
- **Undercuts a claim:** yes, partly. "Warmup is necessary" (title, contribution 1, abstract, conclusion) is too strong. Per
  the I7 rule the run stopped here, and the researcher decided **(simulated)** to reword the claim to "warmup matters" and report the control per
  seed. In a real session this decision is the researcher's.
- **Folded back in (both venues):** new table row and loss curve (*No ramp, capped*); macros `\valRampSolved`, `\valRampRuns`,
  `\valRampUnsolved`, `\valAccNoRampCapped` (and min/max), `\valRerunMaxDiff`, `\valRampSecondsMin/Max`, `\valSolveThreshold`; revised title,
  abstract, contribution 1, setup (control definition and its compute), results (new paragraph), limitations and conclusion; the NeurIPS
  checklist's compute answer; the ICLR AI-use statement (an AI tool proposed the control).
- **Status:** done

### I-02 · Position against recent warmup analyses
- **Type:** reviewer · **Impact:** High · **Effort:** 2 h · **Compute:** none
- **Motivated by:** `sections/related_work.tex` cites only work from 2020 or earlier (Xiong et al.; Liu et al.) for warmup, and says "the original post-LayerNorm
  design relies on it". That is exactly the result a reviewer will say is already known.
- **Idea:** *A reviewer may say "warmup is known to be necessary for post-LN Transformers (Xiong et al., 2020)" →* sharpen the
  contribution to what prior work doesn't isolate: the joint 2×2 design and, after I-01, the ramp-vs-magnitude control. Read and
  (if relevant) cite the 2024 warmup analyses found in I-01.
- **Why it matters:** novelty and significance scores.
- **Literature:** related work: the two 2024 records in I-01 (verified DOIs).
- **Status:** proposed

### I-03 · Sweep d_k to test the scaling claim where it should matter
- **Type:** evidence · **Impact:** High · **Effort:** 3 h · **Compute:** ~40 min estimated, over the 30-min budget (see below)
- **Motivated by:** `sections/limitations.tex`: "We did not vary the key dimension, so our results say nothing about whether attention scaling
  becomes necessary for larger $d_k$"; the only setting is d_k = 16 (`generated/values.tex`, `\valDk`).
- **Idea:** scaled vs. unscaled attention at d_k ∈ {16, 64, 256} (one head per layer, or wider d_model), with warmup on, 3 seeds.
- **Why it matters:** the second finding is the most surprising, and the easiest to dismiss as a small-d_k artifact. Footnote 4 of Vaswani et al.
  predicts the effect grows with d_k.
- **What would change the conclusion:** if unscaled attention fails at d_k = 256, the finding becomes "scaling is unnecessary only at small d_k".
- **Compute note:** the widest models are several times slower per step. To fit the budget, use 2 seeds, or shorter runs for d_k = 256, or ask for a larger budget.
- **Literature:** related work. *Stabilizing Transformer Training by Preventing Attention Entropy Collapse* (Zhai, 2023;
  [arXiv:2303.06296](https://arxiv.org/abs/2303.06296)): its abstract links low attention entropy to training instability, a plausible mechanism if large d_k
  without scaling fails. *Variance Sensitivity Induces Attention Entropy Collapse and Instability in Transformers* (Hong, 2025;
  [doi:10.18653/v1/2025.emnlp-main.421](https://doi.org/10.18653/v1/2025.emnlp-main.421)): title only.
- **Status:** proposed

### I-04 · Give the chance level for alignment
- **Type:** writing · **Impact:** Medium · **Effort:** 15 min · **Compute:** none
- **Motivated by:** `sections/results.tex`: "For the failed runs the value is 13.2%." With 8 source positions, a head whose strongest attention
  lands on a random position is right 12.5% of the time, so a reader can't tell that 13.2% means "no alignment".
- **Idea:** state the chance level, 1/sequence length, generated from `environment.json` as `\valChanceAlign`, in the results sentence.
- **Why it matters:** readers can interpret the number correctly.
- **Literature:** not applicable (presentation). No novelty is involved.
- **Status:** applied. `\valChanceAlign` (12.5%, from `sequence_length` in `environment.json`) was added to `make_values.py` and
  `sources.md`, and the results sentence now reads "close to the 12.5% expected if the strongest attention fell on a random source
  position", in both venues.

### I-05 · Quantify the loss spikes hidden by the final metrics
- **Type:** evidence · **Impact:** Medium · **Effort:** 45 min · **Compute:** none (uses `inputs/results/loss_curves.csv`)
- **Motivated by:** Figure 2 caption: "the shaded bands show brief loss spikes in single seeds". The spikes are in the no-scaling band
  (around steps 350 and 780 in the rendered figure), while the text says scaling "does not change the outcome".
- **Idea:** report, for each configuration with warmup, the largest loss increase between logged steps after step 200 and how many seeds show one.
- **Why it matters:** if the spikes only occur without scaling, "no effect" should become "no effect on the outcome, but less stable training", which is
  more informative and harder to attack.
- **Literature:** related work: Zhai (2023, arXiv:2303.06296), whose abstract links low attention entropy to instability.
- **Status:** proposed

### I-06 · Stop Figure 1's grid from being scaled up
- **Type:** writing · **Impact:** Medium · **Effort:** 20 min · **Compute:** none
- **Motivated by:** `neurips2026/venue_report.md` §7, and the rendered page 2: the Graphviz grid's text is larger than the caption text, because the PDF
  is scaled to 0.48 of the text width.
- **Idea:** in `ablation_grid.py`, set `fontsize=8` and a fixed `size`/`ratio` matching 0.48 × `\textwidth`, so the figure is included at its natural size.
- **Literature:** not applicable (presentation).
- **Status:** proposed

### I-07 · Find the minimum warmup length
- **Type:** evidence · **Impact:** Medium · **Effort:** 1 h · **Compute:** ~17 min (18 runs × ~55 s)
- **Motivated by:** `sections/limitations.tex`: "We tested only ... a single warmup length"; the ablation uses w ∈ {1, 200}.
- **Idea:** sweep w ∈ {10, 25, 50, 100, 200, 400} with scaled attention, 3 seeds; report the smallest w for which all seeds learn.
- **Why it matters:** it turns a yes/no finding into a practical threshold.
- **Literature:** related work: Kosson (2024; doi:10.52202/079017-0096), on reducing the need for warmup (title only).
- **Status:** proposed

### I-08 · Pre-empt "three seeds, one toy task"
- **Type:** reviewer · **Impact:** Medium · **Effort:** 2 h · **Compute:** ~20 min
- **Motivated by:** Table 1 caption "Mean over 3 seeds"; `sections/limitations.tex` "one task, one model size".
- **Idea:** *A reviewer may say "three seeds on sequence reversal can't support a general claim" →* add 2 seeds per configuration (~8 min), and
  repeat the 2×2 design on a second synthetic task (e.g. sorting, ~12 min), or explicitly frame the paper as a workshop note.
- **Literature:** no close match in searched sources (not proof of novelty). Only Crossref answered: arXiv and Semantic Scholar were
  rate-limited. It returned nothing relevant for synthetic algorithmic tasks (`literature/architecture_tasks.md`). Retry the other services
  before claiming anything about how common such toy studies are.
- **Status:** proposed

### I-09 · Measure attention entropy as the mechanism
- **Type:** direction · **Impact:** Medium · **Effort:** 2 h · **Compute:** ~5 min (one seed per configuration)
- **Motivated by:** `sections/introduction.tex`: the scaling exists to stop the softmax being pushed "into regions with small gradients". The paper
  gives this motivation but never measures it.
- **Idea:** log per-head attention entropy during training for all four configurations, as a first mechanism experiment.
- **Literature:** related work. Zhai (2023, arXiv:2303.06296) tracks per-head attention entropy during training. *Two failure modes of deep transformers and
  how to avoid them* (Giorlandino, 2025; [arXiv:2505.24333](https://arxiv.org/abs/2505.24333)): its abstract names entropy collapse from "highly
  concentrated attention scores" as a failure mode.
- **Status:** proposed

### I-10 · Does pre-LN remove the need for warmup here?
- **Type:** direction · **Impact:** Medium · **Effort:** 2 h · **Compute:** ~6 min
- **Motivated by:** `sections/limitations.tex`: "We tested only the post-LayerNorm architecture"; related work cites Xiong et al. (2020) on pre-LN
  training without warmup.
- **Idea:** swap the sublayer order to pre-LN (a new sublayer module, with the original untouched) and rerun warmup vs. no warmup, 3 seeds.
- **Literature:** related work: *On Layer Normalization in the Transformer Architecture* (Xiong, 2020; [arXiv:2002.04745](https://arxiv.org/abs/2002.04745),
  verified at P6) reports pre-LN training without warmup. The pre-LN keyword search returned no further relevant records (Crossref only; arXiv and
  Semantic Scholar rate-limited).
- **Status:** proposed

### I-11 · Name the alignment metric for what it is
- **Type:** writing · **Impact:** Low · **Effort:** 15 min · **Compute:** none
- **Motivated by:** `sections/setup.tex`, Metrics: "strongest encoder--decoder attention (best layer and head)". Taking the best head is an optimistic summary.
- **Idea:** call it "best-head alignment", or also report the mean over heads (a small analysis addition).
- **Literature:** not applicable (presentation).
- **Status:** proposed

### I-12 · Can an optimizer fix replace warmup?
- **Type:** direction · **Impact:** Low · **Effort:** 1 h · **Compute:** ~3 min
- **Motivated by:** `sections/related_work.tex`: Liu et al. (2020) "relate the need for warmup to the high variance of the adaptive learning rate"; the paper
  doesn't test this.
- **Idea:** no warmup with RAdam (available in PyTorch 2.2) instead of Adam, 3 seeds.
- **Literature:** related work: Liu et al. (2020, already cited and verified); Kosson (2024, title only).
- **Status:** proposed

## Literature searched
All queries used keywords only, and the privacy guard (`--guard-text neurips2026/sections`) refused one test query that quoted the draft.

| Group | Queries | Services that answered | Results |
|---|---|---|---|
| warmup | `learning rate warmup transformer`; `warmup adaptive learning rate variance` | Crossref 2/2 · arXiv 0/2 (HTTP 429, timeout) · Semantic Scholar 0/2 (429) | [literature/warmup.md](literature/warmup.md) |
| attention scaling | `attention softmax temperature scaling`; `attention entropy collapse training instability` | Crossref 2/2 · Semantic Scholar 1/2 · arXiv 0/2 (429) | [literature/attention_scaling.md](literature/attention_scaling.md) |
| architecture and tasks | `pre-LN post-LN layer normalization transformer`; `transformer synthetic algorithmic tasks sequence reversal` | Crossref 2/2 · arXiv 0/2 (429, timeout) · Semantic Scholar 0/2 (429) | [literature/architecture_tasks.md](literature/architecture_tasks.md) (no relevant records) |

Most Crossref keyword hits were unrelated (e.g. solar-radiation forecasting); only the records named in the cards were judged relevant.

## Log
- 2026-09-15 · I5 pause. The researcher approved **I-01** (run) and **I-04** (apply) **(simulated)**.
- 2026-09-15 · I7 **I-01 run**: 6 runs, 1,479 s wall time. That's within the 30-min budget, but about 4× the estimate because the CPU was shared.
  The baseline rerun reproduced the original exactly. The capped no-ramp control solved the task in 1 of 3 seeds. **Outcome mixed, and it undercuts
  "warmup is necessary".** Stopped and reported. The researcher **(simulated)** chose to reword to "warmup matters" and report the control per seed.
- 2026-09-15 · I6 **I-04 applied** and I7 **I-01 folded in**, in `neurips2026/` and `iclr2027/`. Values and figures were regenerated (`make_all.py`, 61
  values). The title changed to *In a Small Transformer, Warmup Matters but Attention Scaling Does Not*, and the abstract, contributions, setup,
  results, limitations, conclusion, NeurIPS checklist and ICLR AI-use statement were revised. Recompiled. `check_paper.py --page-limit 4
  --anonymous --verify-citations` passes in both folders: main text ends on page 4, 6/6 citations verified, and only the intended TODO warnings
  remain. The changed pages were read. `inputs/` was not modified.
- 2026-09-15 · The user (real, not simulated) confirmed keeping the I-01 revision.
