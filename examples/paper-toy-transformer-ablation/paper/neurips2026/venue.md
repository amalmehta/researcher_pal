# NeurIPS 2026: rules for this paper

> P2 of paper-writer. Built-in profile: `references/venues/neurips.md`. Re-verified on **2026-09-15** against the
> [call for papers](https://neurips.cc/Conferences/2026/CallForPapers), the [main track handbook](https://neurips.cc/Conferences/2026/MainTrackHandbook)
> and the [official style files](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip).

## Differences from the built-in profile
- None found.
- The 2026 deadlines (May 2026) have passed and the 2027 call isn't out yet, so this paper uses the 2026 format as a formatting test.

## Rules that shape this paper
| Rule | Value | Consequence here |
|---|---|---|
| Page limit | 9 content pages, figures included | Target is a 4-page workshop-style paper, so check against 4 (stricter) and report 9 as the venue limit |
| Not counted | acknowledgments, references, appendices, checklist | `\label{pw:mainend}` goes after the conclusion |
| Layout | one column; `\textwidth` = 397.48 pt (measured by compiling the template) | figures sized with `figure_style.py` venue `neurips` |
| Submission mode | `\usepackage{neurips_2026}` (main track): anonymized with line numbers | no author names in the source; no acknowledgments |
| Checklist | required, after references; 16 items with 1–2 sentence justifications | filled from the paper's content, with open items left as TODO |
| Limitations | encouraged (checklist item 2) | a short Limitations section |
| LLM policy | writing, editing and formatting help doesn't need a declaration | checklist item 16: NA, with justification |
| Fonts | Type 1 or embedded TrueType only | matplotlib `pdf.fonttype = 42`; check the Graphviz and SVG figures |
