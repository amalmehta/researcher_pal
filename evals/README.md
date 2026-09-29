# Evaluation: does researcher-pal help on papers the model has never seen?

Run on 2026-09-18. Protocol and scoring: [`rubric.md`](rubric.md).

Until this run, every claim about the skills rested on two famous papers (Attention Is All You Need,
Barabási–Albert) that the model can largely recall. This evaluation uses papers published **after the
model's training cutoff**, so recall can't carry the result.

## Setup

| | |
|---|---|
| Papers | arXiv 2608.13995 (multi-strain epidemics), 2608.13953 (heterogeneous-agent econometrics), 2608.14850 (graphene thermoelectrics), all August 2026 |
| Conditions | **with skill**: follow `researcher-pal/SKILL.md`; **baseline**: same task, no skill |
| Held equal | same model, same bounded task, same 20-minute budget, paper text supplied as a local file, no network |
| Task | concept map, 3 exercises with solutions, and the 3 places a careful reader gets stuck |
| Not exercised | animations, the tutor loop, the cross-paper knowledge graph |

## What the outputs look like

Counted mechanically across all Markdown each run produced:

| Paper | Condition | Words | Dependency mentions | Mermaid map | "Check yourself" prompts | Limitation flags | Coded exercises with tests |
|---|---|---|---|---|---|---|---|
| 13995 | with skill | 7,089 | 38 | 1 | 16 | 9 | 2 |
| 13995 | baseline | 7,172 | 5 | 0 | 0 | 0 | 0 |
| 13953 | with skill | 11,102 | 24 | 1 | 17 | 10 | 0 |
| 13953 | baseline | 7,690 | 4 | 0 | 0 | 3 | 0 |
| 14850 | with skill | 9,545 | 28 | 1 | 16 | 13 | 0 |
| 14850 | baseline | 7,156 | 1 | 0 | 0 | 4 | 0 |

"Limitation flags" counts phrases like *not stated in the paper*, *the authors call this an ansatz*,
*we did not*, *unverified*. "Dependency mentions" counts *depends on* / *prerequisite*.

**What this shows:** the skill's structure transfers to unfamiliar papers. Every run with the skill produced a
dependency-ordered map with a diagram, self-check questions, and explicit flags separating what the paper
proves from what it assumes or asserts; no baseline run produced a diagram or a self-check, and baselines
flagged limits far less often. On the epidemics paper the skill also produced runnable exercises with tests
and reference solutions (the agent reported stubs failing and 10 solution tests passing), which no baseline did.

**What this does not show:** that the material teaches a human better. Length is not quality, and a
dependency-ordered map with self-checks can still mislead if its content is wrong.

## Faithfulness check

Every decimal number in each run's prose was checked against the paper's text. Numbers that don't appear in
the paper were inspected by hand: in every case sampled they were the run's *own* derivations (arithmetic
steps like `(15/7)^(1/4)=1.20983`, toy-model parameters like `θ₀=(0.6,0.3)`, or simulation outputs), not
claims attributed to the paper. No fabricated result, equation or citation was found in any run, in either
condition.

## Blind grading

A separate agent scored each pair without being told which side was which, working only from the files and
the paper text (18 points per side; criteria in `rubric.md`).

| Paper | With skill | Baseline | Preference |
|---|---|---|---|
| 13995 epidemics | **17** | 13 | with skill |
| 13953 econometrics | **18** | 13 | with skill |
| 14850 thermoelectrics | **18** | 14 | with skill |
| **Total** | **53 / 54** | 40 / 54 | 3–0 |

No grader found a fabricated result, equation or citation on either side.

**Why the skill's runs won**, in the graders' words: they reproduced the papers' own tables and hedges
verbatim, quoted the authors' caveats (*"we do not formally prove bootstrap validity"*, *"exact within the
model"*), named what they had not read, and encoded the paper's real distinctions in test assertions. The
baselines lost points on specific slips: calling a 0.990 coverage figure "under-coverage", and inverting a
parity convention at exactly the step it flagged as a trap.

**Where the baselines were better**, and worth stealing: one baseline reported honestly that its symbolic
derivation failed and told the learner to validate numerically instead — better than anything the skill's run
had on that passage; another caught a notation collision the skill's run missed; two baselines wrote a harder
single exercise. The skill's own faults were real too: one run described an attribution as its own inference
when the paper states it outright.

## Honest limits of this run

- **The grader is an AI model**, not a subject expert and not a learner. It checks material against the
  paper's text; it cannot tell you whether anyone learns faster from it.
- **Three papers, one run each.** No variance estimate; a difference on a single paper is not a result.
- **The scope was bounded** so runs stay comparable, which leaves the skill's most distinctive parts
  (animations, tutoring, knowledge graph) unmeasured.
- Raw outputs live outside the repo (they're large and derived); regenerate them with the protocol above.
