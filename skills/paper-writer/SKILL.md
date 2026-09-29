---
name: paper-writer
description: Help a researcher write their own research paper for a specific venue. Built-in profiles cover NeurIPS, ICML and ICLR; any other conference or journal works from its call for papers or template. Turns results data, notes, a code repository and existing drafts into a venue-formatted LaTeX paper. Generates figures, tables and in-text numbers from the data with re-runnable scripts, verifies citations against arXiv and Crossref, compiles with Tectonic, and checks page limits, anonymity, unsourced numbers, required statements and checklists. It can also retarget a finished paper to a different venue. Use this whenever someone wants to write, draft, structure, shorten, format or resubmit their own paper, e.g. "help me write my NeurIPS paper from these results", "turn my notes and plots into an ICLR submission", "convert my ICML paper to NeurIPS format", "make publication figures for my paper", "is my paper within the page limit", even if they never mention LaTeX. Never invents results, numbers or citations. Not for learning or explaining someone else's paper (use researcher-pal), and not for writing peer reviews.
---

# paper-writer

The researcher is the author: they own every claim, every number and every sentence that goes out. This
skill removes the labor (drafting, figures, tables, formatting, checks), but never supplies the
science. When something is missing, it becomes a visible `\TODO{...}` and a question, never a guess. A
visible gap costs the researcher minutes; a plausible invented number or citation can cost them their
reputation.

## Output layout

```
paper/<slug>/
├── intake.md                         # P1: claims ↔ evidence, missing pieces (confirmed by the researcher)
├── figures_scripts/*.py              # one script per figure/table/values file, shared by every venue,
│                                     #   plus figure_style.py and make_all.py
└── <venue>/                          # one folder per target venue, e.g. iclr2027/
    ├── venue.md                      # P2: this cycle's rules, verified against the live CFP
    ├── outline.md                    # P3: page budget + figure/table plan (approved by the researcher)
    ├── template/                     # official style files, unmodified
    ├── main.tex                      # official template shell that \input{}s the sections
    ├── sections/*.tex                # prose (P5)
    ├── generated/values.tex          # \newcommand{\valName}{...}, written by scripts (P4)
    ├── generated/tables/*.tex        # tables written by scripts (P4)
    ├── figures/*.pdf                 # figures (P4)
    ├── figures/src/*.svg | *.dot     # editable sources for concept illustrations and diagrams
    ├── refs.bib, citations_verification.md
    ├── sources.md                    # every number/macro → data file, column, filter, script
    └── venue_report.md               # P7: checks, rule changes, open TODOs, statements
```

## Ground rules

- **Never invent** results, numbers, experimental details, quotes, citations or author information.
  Use `\TODO{}` (define it as a red `\textbf` macro in `main.tex`) and list open items for the researcher.
- **Numbers come from data.** In-text results use `\val...` macros written by
  `figures_scripts/make_values.py`. Tables are written by scripts. Every macro and every hand-typed
  setting (e.g. "batch size 64") gets a row in `sources.md`: value, meaning, file, and how it was
  computed. `scripts/check_paper.py` enforces this.
- **Tools.** LaTeX: `tectonic` (on PATH or `~/.local/bin/tectonic`). If it's missing, ask before
  installing anything. Figures: Python 3.9+ with matplotlib and NumPy (read CSV and JSON with the standard library).
  Diagrams: TikZ, or Graphviz `dot -Tpdf`. Concept illustrations: SVG, converted with
  `rsvg-convert -f pdf`. Ask before adding other libraries.
- **External calls:** only official venue pages and template downloads, the arXiv API and api.crossref.org
  (citation checks), and Tectonic's package downloads. **The researcher's unpublished content never
  leaves the machine**: don't paste their text, results or ideas into web searches or any online service.
  Citation checks send only the cited works' public metadata.
- **Official templates stay untouched.** Never change margins, fonts, spacing or style files, and never
  add hidden text or anything aimed at manipulating AI reviewers (venues desk-reject prompt injection).
- **Never submit anything.** Submission is the researcher's act.

## P1: Intake (then pause)

Read everything the researcher provides:
- **results** (CSV, JSON, logs): what was measured, over how many seeds or runs, and any provenance files
  like `environment.json`;
- **notes or outline**: the intended story and claims, in the researcher's own words;
- **code**: the method as actually implemented, hyperparameters and training setup. Code beats notes
  when they disagree; flag the disagreement;
- **existing draft and .bib**: structure, terminology and voice to keep.

Write `paper/<slug>/intake.md`:

```markdown
# Intake: <working title>

## Claims
| # | Claim (researcher's wording) | Evidence (file → columns/rows) | Status |
|---|---|---|---|
| C1 | ... | results/x.csv → config=baseline, accuracy | supported / partial / **unsupported** |

## Facts I still need from you
- <e.g. compute budget for the full runs, dataset license, author list for camera-ready>

## Disagreements between inputs
- <e.g. notes say 5 seeds, results contain 3>
```

**PAUSE.** Show the claims table and ask the researcher to confirm, edit or drop each claim, and to answer the
open facts. Only confirmed claims go into the paper.

## P2: Venue rules

1. Load `references/venues/<venue>.md` if it exists. For any other venue (or when the researcher gives a CFP link
   or template zip), build a profile with `references/venue_profile_template.md`.
2. **Always re-check the live rules**: fetch the current CFP, author guide and AI/LLM policy from the venue's
   own site, and download the official template. Profiles are dated snapshots, and rules change every
   cycle. If the current cycle's CFP isn't published yet, say so and use the latest official one,
   clearly labeled.
3. Compile the unmodified template example with Tectonic, then measure `\textwidth` and `\columnwidth`
   with the probe from the profile template. Tectonic runs XeTeX, so check the log for `Font shape ... undefined`.
   Templates written for pdfLaTeX that load `times` need `\usepackage[T1]{fontenc}` in `main.tex` (never in the
   style file); without it, bold, italics and small caps silently fall back to other fonts.
4. Write `<venue>/venue.md` for this cycle, and list every difference from the built-in profile at the top.

## P3: Outline (then pause)

Write `<venue>/outline.md` using `references/writing_guide.md`:
- **page budget**: each section's share of the page limit, including figures and tables;
- **section plan**: the purpose of each section, the confirmed claims it carries, and its evidence;
- **figure and table plan**:

| ID | Takeaway (the caption's first sentence) | Data | Script | Width |
|---|---|---|---|---|

- **required statements and checklist items** for this venue, and where they go.

**PAUSE.** The researcher approves or edits the outline before any drafting.

## P4: Figures, tables and values

- Copy `assets/figure_style.py` into `figures_scripts/`. If you measured widths for a venue not in the
  helper, register them with `register_venue()`. One script per output, named after it
  (`figures_scripts/loss_curves.py` → `<venue>/figures/loss_curves.pdf`), reading data straight from the
  researcher's files. **The scripts are shared by every venue**: they take the venue folder from `$VENUE_DIR`
  and the style name from `$VENUE`, both set by `make_all.py`, so a fix or a new number lands in every venue
  at once. Never copy a script per venue: the copies drift. Include figures in LaTeX at the exact width they were made for
  (`\includegraphics[width=\linewidth]`), never scaled.
- **Data plots:** say the takeaway in the caption, not in a title inside the figure; label axes with units;
  use the colorblind-safe palette plus markers or line styles; state what error bars show (min/max, std,
  95% CI) and over how many runs.
- **Tables:** a script writes `generated/tables/<name>.tex` with booktabs and bolds the best value per
  column automatically. Numbers are never typed by hand.
- **Values:** `make_values.py` writes `generated/values.tex` (`\newcommand{\valBaselineAcc}{99.8}`) and
  adds matching rows to `sources.md`.
- **Method diagrams:** TikZ inside `figures/<name>.tex`, or Graphviz `figures/src/<name>.dot` rendered by a
  script with `dot -Tpdf`.
- **Concept illustrations:** editable SVG in `figures/src/<name>.svg`, converted by a script with
  `rsvg-convert -f pdf`. Treat these as drafts the researcher will polish; say so in `venue_report.md`.
- Every figure regenerates from its script. Re-run all scripts before each compile.

## P5: Draft

Draft one section at a time in the outline's order, following `references/writing_guide.md`
(ground rules, section guidance, claim calibration, venue tone). Reuse the researcher's terminology.
After each section, list what you assumed or left as `\TODO`. The researcher may review section by section
or all at the end; ask which they prefer.

Write the venue's statements (e.g. ICLR's AI use statement, ICML's impact statement, the NeurIPS
checklist) from facts only. The AI-use disclosure must truthfully include this skill's role: drafting text,
generating figure and table scripts, formatting references. Tell the researcher that the submission form
disclosure must match the paper.

## P6: Citations

- Keep `refs.bib` clean: one key per work, with `doi` or `eprint` (arXiv ID) fields wherever they exist.
- Run `python3 scripts/check_paper.py <venue-dir> --verify-citations`. It checks each entry against arXiv or
  Crossref and writes `citations_verification.md`. For each flagged entry, show the researcher what was
  found and ask. Never silently "fix" an entry to match a different paper.
- Related work: suggest candidates from the researcher's references and from the papers in
  `~/researcher-pal/knowledge_graph.md` (if present), with a sentence on why each is relevant. Add only
  the ones the researcher approves, and verify them first.

## P7: Compile and check

```bash
python3 ../figures_scripts/make_all.py <venue-dir>     # regenerate values, tables, figures from the data
tectonic -Z search-path=template main.tex --keep-logs --keep-intermediates   # template/ stays unmodified
python3 <skill>/scripts/check_paper.py . --page-limit <N> [--anonymous --author "<name>" ...] \
    --verify-citations --regenerate --python python3.9 --report checks.md
```

`--regenerate` re-runs the scripts and fails if any figure or value changes, which is what proves the paper
matches its data rather than a stale build. Pass the project's interpreter with `--python`: another
matplotlib version draws different bytes. `make_all.py` pins `SOURCE_DATE_EPOCH` so rebuilds are identical.

Put `\label{pw:mainend}` right where the page-limited main text ends (before references, or before
statements that don't count).

Then **read the compiled PDF like a reviewer**. Render the pages to images (on macOS a PDFKit one-off
works without installs; otherwise use a browser tool). Compare every sentence about a figure or table with what
the figure or table actually shows. The checks can't catch a caption that overclaims, a derived number that
contradicts a plot, or a clipped label. Fix what you find at the source (script, metric or wording), then
regenerate, recompile and re-run the checks.

Then write `venue_report.md`:
1. the checks table from `check_paper.py`;
2. rule changes found at P2;
3. open `\TODO`s and facts still needed;
4. required statements and checklist status, with a draft of each for the researcher to edit;
5. things only a human can judge (figure polish, tone, novelty framing).

Fix every FAIL before calling a draft ready. If a fix needs the researcher (e.g. content must be cut to
fit), propose options instead of cutting their claims yourself.

## Improvement ideas (after the first clean P7)

After the first P7 pass with no FAILs, use the **paper-ideas** skill in own-draft mode. It produces
`paper/<slug>/ideas/ideas.md`: ranked writing, evidence, reviewer and research-direction ideas, each checked
against the literature. Show the top ideas and ask which to act on. The researcher can also ask for ideas at any time.
Approved edits and experiments are carried out by paper-ideas and re-checked through P7.

## P8: Revision loop

Apply the researcher's edits and requests one round at a time. After each round, re-run the figure scripts,
recompile, re-run the checks and update `venue_report.md`. Keep a short changelog at the bottom of `outline.md`.

## P9: Retarget to another venue

1. Run P2 for the new venue. Diff the two `venue.md` files: page limit, columns, widths, required statements,
   anonymity rules, citation commands.
2. Copy `<venue_a>/` to `<venue_b>/`, replace `template/` and rebuild `main.tex` from the new official
   shell. Keep `sections/`, the scripts, `refs.bib` and `sources.md`.
3. Regenerate every figure at the new widths; don't scale the old PDFs.
4. Re-outline for the new page budget and swap the statements (see the retargeting section of the writing guide).
   Show the researcher what moved to the appendix or was cut before cutting their text.
5. Compile, check, and write the new `venue_report.md`.
