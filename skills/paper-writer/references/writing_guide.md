# Writing guide

How to draft each part of a research paper from the researcher's material, and how to adjust for a venue.
The researcher is the author: the skill drafts, the researcher decides.

## Contents
1. Ground rules for every sentence
2. Section by section
3. Calibrating claims to evidence
4. Venue tone and structure
5. Fitting the page budget and retargeting
6. Statements, checklists and disclosures

---

## 1. Ground rules for every sentence

- **No invented content.** Every result, number, experimental detail, quote and citation comes from the
  researcher's files or a verified reference. If something is needed but missing, write
  `\TODO{what is needed and from whom}` and list it for the researcher. A visible gap is recoverable;
  a plausible fabrication can end a career.
- **Numbers come from macros.** Values in the text are generated from the data (for example
  `\valBaselineAcc`, defined in `generated/values.tex` by a script) and logged in `sources.md`, so
  prose and tables can't drift from the results. Hand-typed numbers are only allowed for fixed settings
  (e.g. "batch size 64"), and each still needs a `sources.md` entry pointing to the config or code line.
- **One claim, one piece of evidence.** Each claim in the abstract and introduction points to a figure,
  table, theorem or citation that supports it. If there isn't one, weaken the claim or add a `\TODO`.
- **Keep the researcher's voice.** Reuse their terminology and framing from notes and drafts. Don't
  rename their method or add a contribution they didn't list.
- **Plain, precise prose.** Prefer active voice and concrete verbs. Define each symbol once, near first use.
  Avoid filler and hype ("groundbreaking", "paradigm shift", "novel" in every paragraph).

## 2. Section by section

**Title.** Say what the paper shows, not just the topic. Keep it under about 12 words, using the method
name only if the researcher has one.

**Abstract** (one paragraph, 4–6 sentences for ICML; about 150–250 words elsewhere):
1. the problem and why it matters;
2. the gap in current approaches;
3. what this paper does;
4. the main result, with the key number(s) via macros;
5. what it implies or enables.

**Introduction.**
- Open with the problem in terms the target community cares about.
- State the gap concretely, with citations.
- Give a one-paragraph preview of the approach.
- List **the contributions the researcher confirmed at P1**, as 2–4 bullets, each pointing to the section
  or figure that supports it.
- Optionally, a teaser figure (Figure 1) with the one picture a reviewer should remember.

**Related work.** Group by idea, not by paper. End each group by saying how this paper differs. Cite prior
work by the authors in the third person when the venue is anonymous.

**Method.** Notation first, then the approach, then the design choices and why they were made. Use pseudocode if
steps matter. Anything that would be needed to reimplement it goes here or in the appendix.

**Experiments.**
- *Setup:* data, models, hyperparameters, training budget, hardware, number of seeds, and how error bars
  are computed. All of it comes from the code and `environment.json` or config files.
- *Results:* one subsection or paragraph per claim, each opening with the takeaway, then the figure or table.
- *Ablations:* which component was removed or changed, and what happened, including null results.

**Limitations.** Be honest and specific: scale, datasets, assumptions, compute, failure cases. Reviewers trust
papers that name their own limits, and the NeurIPS checklist asks for them.

**Conclusion.** Restate what was shown, with no new claims. Mention future work only if it's substantive.

**Figure and table captions.** The first sentence states the takeaway ("Warmup is necessary: without it, all
runs diverge."), then what's plotted, and what error bars mean.

## 3. Calibrating claims to evidence

| Evidence | Wording |
|---|---|
| Proof | "we prove", "X holds" |
| Many seeds, datasets or settings, consistent, with error bars | "X improves Y", "consistently" |
| A few seeds, one setting | "in our experiments, X improved Y", "on <task>" |
| One run, a toy scale, or mixed results | "we observe", "suggests", "in this setting" |
| No experiment | "we hypothesize", or leave it out |

Always state the scale (e.g. "on a 2-layer model trained for 1,500 steps") when results are small.

## 4. Venue tone and structure

| Venue | Format | What reviewers look for | Structural must-haves |
|---|---|---|---|
| NeurIPS | one column; see profile for limits | clear significance to a broad ML audience; rigor: error bars, compute, limitations (the checklist asks) | paper checklist after appendices; limitations discussed somewhere; no acknowledgements at submission |
| ICML | two columns, dense | technical depth, theory welcome; clean experiments; short abstract | impact statement before references; 4–6 sentence abstract; financial conflicts at the end of the introduction |
| ICLR | one column; see profile | strong empirical evidence and ablations; clarity, since reviews and discussion are public on OpenReview | AI use statement (required); ethics and reproducibility statements (recommended) |
| Workshops | usually 4 pages | an interesting idea or early result, clearly scoped | check the specific workshop CFP |

These are conventions (**convention**), not written rules. The written rules are in each venue profile.

## 5. Fitting the page budget and retargeting

Plan the budget at P3: a line count per section, plus figure and table space. When over the limit, cut in this order:
1. redundant sentences and restated claims;
2. over-long related work (move detail to the appendix);
3. secondary results and extra ablations (to the appendix, keeping a one-line summary and a pointer);
4. figure sizes, but never below legible text (at least about 7 pt in figures).

Never shrink margins, fonts or spacing: every venue forbids it.

**Retargeting** (P9):
- Re-run P2 for the new venue and diff the profiles: page limit, columns, required sections, anonymity, citation style.
- Regenerate every figure at the new widths (one column vs. two column), rather than scaling PDFs.
- Rebuild the outline for the new budget: e.g. 9 one-column pages → 8 two-column pages is roughly the same
  word count but less figure area.
- Swap the statements: e.g. ICLR's AI use statement → ICML's impact statement → NeurIPS's checklist.
- Recompile, re-run the checks, and list anything still unresolved.

## 6. Statements, checklists and disclosures

- Draft each required statement from facts: what AI tools were used for (including this skill's drafting,
  figure scripts and citation checks), and what the researcher reviewed. The researcher must read and
  edit it; never claim reviews or checks that didn't happen.
- Checklists (e.g. NeurIPS): answer each item from the paper's actual content, pointing to the section
  that justifies the answer. Mark anything uncertain as `\TODO` for the researcher.
- Never add hidden text, white-on-white instructions or anything aimed at manipulating automated
  reviewers. Venues treat prompt injection as grounds for desk rejection.
