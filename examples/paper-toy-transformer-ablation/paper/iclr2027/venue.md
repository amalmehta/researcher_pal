# ICLR 2027: rules for this paper

> P2 of paper-writer, run as part of retargeting (P9) from `../neurips2026/`. Built-in profile:
> `references/venues/iclr.md`. Re-verified on **2026-09-15** against the [author guidelines](https://iclr.cc/Conferences/2027/AuthorGuidelines),
> the [AI policy for authors](https://iclr.cc/Conferences/2027/AIPolicyForAuthors) and the [official style files](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip).

## Differences from the built-in profile
- None found. **Deadline alert:** abstracts are due Sep 18, 2026 and full papers Sep 25, 2026 (AoE), three and ten days after this check.

## What changes from NeurIPS 2026
| | NeurIPS 2026 | ICLR 2027 | Action |
|---|---|---|---|
| Page limit | 9 content pages | 9 pages main text (10 camera-ready) | keep the 4-page target |
| Layout, \textwidth | one column, 397.48 pt | one column, 397.48 pt (measured) | same sizes; regenerate figures with `VENUE = "iclr"` anyway |
| Template | `neurips_2026.sty` | `iclr2027_conference.sty` + `.bst`, `\iclrfinalcopy` commented out | new `main.tex` from the official shell |
| Headings and captions | bold headings | small-caps headings; figure captions after, table titles before | template handles it |
| Required end matter | paper checklist (after references) | **AI use statement (required)**; ethics and reproducibility statements (recommended) | drop the checklist; add an AI use statement and a reproducibility statement before the references |
| AI disclosure | writing, editing and formatting help needs no declaration | required and recommended disclosure lists; must match the OpenReview form | disclose implementation help (required) and drafting, figures, references and structure (recommended) |
| Anonymity | anonymized, line numbers | desk rejection if identity is revealed | no author names; "Anonymous authors" |
| Citations | natbib | natbib `\citet` / `\citep` | unchanged |
