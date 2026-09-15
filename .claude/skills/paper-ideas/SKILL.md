---
name: paper-ideas
description: Generate ranked, evidence-grounded ideas for improving a research paper. For the user's own draft that means writing and presentation fixes, missing experiments, baselines and statistics, and the objections the target venue's reviewers are likely to raise. For a published paper they are studying it means weaknesses, open questions and follow-up research directions. Each idea is checked against existing literature on arXiv, Semantic Scholar and Crossref using keyword-only searches. With approval, it applies edits to the draft, or designs and runs the extra experiments and folds the results back in. Use this whenever someone asks how to improve, strengthen, extend or stress-test a paper, what reviewers will criticize, what experiments are missing, or what to do next, e.g. "how can I make my ICLR submission stronger", "what would reviewers attack in this draft", "suggest follow-up experiments for the Barabási–Albert paper", "what's missing from my paper", "give me research ideas building on this". Also runs automatically after paper-writer's first clean compile check and after researcher-pal's final exercise. Never invents evidence, related work or novelty.
---

# paper-ideas

A good improvement idea is **specific** (you can act on it tomorrow), **grounded** (it points at the exact
sentence, figure or number that motivates it) and **honest about novelty** (it says what related work exists and never
claims nobody has done it). Generic advice like "add more experiments" or "improve clarity" is not an idea. Ten sharp,
ranked ideas beat forty vague ones.

## Two modes

| | Own draft | Learned paper |
|---|---|---|
| Called from | paper-writer (after its first P7 pass with no FAILs), or on request | researcher-pal (after step 8), or on request |
| Reads | `paper/<slug>/intake.md`, each `<venue>/` folder (sections, `main.pdf`, `venue.md`, `venue_report.md`, `sources.md`), the results and code | `papers/<slug>/paper.pdf` (+ LaTeX source), `concept_graph.md`, the learner's exercises and solutions, the knowledge graph |
| Output folder | `paper/<slug>/ideas/` (shared by all venue folders) | `papers/<slug>/ideas/` |
| Applying an idea (I6) | edit the draft through paper-writer's rules | add an "Open questions and extensions" note to `concept_graph.md` |
| Experiments (I7) | fold new results into values, tables, figures and claims | report findings in `ideas.md`; build on the learner's implementation |

## Output layout

```
ideas/
├── ideas.md                          # the ranked report (I5), updated as ideas are applied or run
├── literature/<group>.json | .md     # raw search results from scripts/lit_search.py (I4)
└── experiments/NN_<idea-slug>/       # one folder per approved experiment (I7)
    ├── plan.md                       # hypothesis, design, metrics, compute estimate
    ├── run.py                        # new code; imports the original code read-only
    ├── results/                      # new results only
    └── findings.md                   # what happened, with numbers from results/
```

## Ground rules

- **Evidence.** Every idea cites the exact passage (a short quote with section, or file and line), figure, table cell or
  number that motivates it. For your own draft, quote freely. For published papers, keep quotes under 15 words and
  paraphrase the rest.
- **Novelty is never asserted.** Label every idea with one of:
  - `related work: <verified records>`;
  - `no close match in searched sources (not proof of novelty)`;
  - `unverified (search failed)`;
  - `not applicable (presentation)`, only for writing ideas that make no research claim.

  A record counts only if `lit_search.py` returned it with an arXiv ID, DOI or Semantic Scholar ID. Judge relevance from its
  title and abstract, and say how it relates.
- **Privacy.** For an unpublished draft, searches use short topic keywords only. Always run `lit_search.py` with
  `--guard-text` pointing at the draft's sections, and list every query in the report. Titles of published papers may
  be searched directly.
- **Approval before action.** Generating and ranking ideas is automatic; applying an edit or running an experiment is not.
- **Compute budget:** CPU, at most 30 minutes per experiment and 2 hours per round, unless the user sets a different
  one. Estimate first by timing a short pilot. If the estimate exceeds the budget, shrink the design or ask.
  Ask before installing anything.
- **Originals are read-only.** New code and results go in `ideas/experiments/`. Never overwrite the researcher's
  results, code or the paper's generated files by hand.
- **Results are reported as they come out.** If an experiment contradicts or weakens a claim, **stop and tell the
  user before editing any claim**. Then revise the claim; don't bury the result.
- **External services:** arXiv API, Semantic Scholar Graph API (no key) and Crossref, via `scripts/lit_search.py` only.
- **Environment:** reuse the interpreter and libraries the calling skill found (Python 3.9+, pytest, the field's stack).

## I1: Gather context

Read everything in the "Reads" row for your mode. Also note:
- the paper's main claims and the evidence behind each one (for a draft, `intake.md` has this);
- the venue's reviewer expectations (`references/venues/` in paper-writer), for a draft;
- what's cheap to run: the existing code, how long one run takes, which knobs exist.

## I2: Generate candidates

Read `references/idea_catalog.md` and work through all four types:
(a) writing and presentation, (b) evidence and experiments, (c) simulated reviewer critique, (d) new research directions.
Draft 10–20 candidates, then prune anything generic, duplicated, already done in the paper, or impossible to act on.
Keep at least one per type. For a draft, also re-read `venue_report.md`'s "needs human judgment" section.

## I3: Ground each idea

Write each surviving idea as a card:

```markdown
### I-NN · <short, specific title>
- **Type:** writing | evidence | reviewer | direction · **Impact:** High/Medium/Low · **Effort:** <hours> · **Compute:** <estimate or none>
- **Motivated by:** <quote/figure/table/number with its location>
- **Idea:** <the concrete change or experiment>
- **Why it matters:** <which claim, reviewer concern or open question it addresses>
- **What would change the conclusion:** <experiments only: which outcome supports or undercuts which claim>
- **Literature:** <label> — <records, with how each relates>
- **Status:** proposed
```

Reviewer ideas are phrased as the objection plus the change that answers it: "*A reviewer may say … → do …*".

## I4: Check the literature

Group ideas by topic. For each group, write 1–3 keyword queries of 3–8 topic words, then run:

```bash
python3 <skill>/scripts/lit_search.py "<query 1>" "<query 2>" --guard-text <draft sections dir> --limit 5 --out ideas/literature/<group>
```

The script refuses queries that quote the draft. Read the returned titles and abstracts, attach only records that
really relate, and set each idea's label. If a service fails, say which one in the report. For a group where every
search failed, use `unverified (search failed)`.

## I5: Rank and report (then pause)

Rank by impact first (does it change whether a claim holds or a reviewer's score?), then by effort and compute. Write `ideas/ideas.md`:

```markdown
# Improvement ideas: <paper>

> Mode: own draft | learned paper · Generated <date> · Budget: <budget>

## Ranked ideas
| # | Idea | Type | Impact | Effort | Compute | Literature | Status |
|---|---|---|---|---|---|---|---|

## Details
<the cards>

## Literature searched
<queries per group, services that answered, links to ideas/literature/*.md>

## Log
<applied edits and experiments, with dates and outcomes>
```

Before pausing, run `python3 <skill>/scripts/check_ideas.py ideas/ideas.md` and fix everything it reports. It checks
that cards are complete, all four types are covered, labels are valid, cited IDs are verified records and links work.
Re-run it whenever you update `ideas.md`.

**PAUSE.** Show the top of the ranked table and ask which ideas to apply or run. Multiple choices are fine.

## I6: Apply approved non-experiment ideas

- **Own draft:** follow paper-writer's rules. Numbers come through `\val` macros and `sources.md`, and figures through
  their scripts. Apply the change in **every venue folder** that shares the section. Then regenerate, recompile,
  run `check_paper.py` in each folder, and read the changed pages. Set the card's status to `applied` with a
  one-line summary of the change.
- **Learned paper:** add the idea to an "Open questions and extensions" section at the end of `concept_graph.md`, linking
  its card, and set the status to `noted`.

## I7: Run approved experiments

1. **Plan** (`plan.md`): hypothesis; which claim it tests; what result would support or undercut it; design (what
   varies, what stays fixed, seeds); metrics; a compute estimate from a timed pilot (e.g. one seed with few steps). If
   it's within budget, go ahead; if not, shrink it or ask.
2. **Code** (`run.py`): import the original implementation read-only and write only to `results/`. Record the
   environment and settings next to the results.
3. **Run**, respecting the budget, and log the real wall time.
4. **Findings** (`findings.md`): what happened, with every number read from `results/`. If a result undercuts a claim
   in the paper, stop here and tell the user.
5. **Fold back in:**
   - *Own draft:* add the new results to the value, table and figure scripts (reading from
     `ideas/experiments/NN/results/`), and revise the affected text, including Limitations and statements
     such as checklists. Apply it in every venue folder, recompile, run the checks, and read the changed pages.
   - *Learned paper:* put the findings and figures in the card and link `findings.md`.
6. Set the card's status to `done` and add a log entry with the outcome, including negative or null results.
