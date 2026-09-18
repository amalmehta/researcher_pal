# Venue report: ICLR 2027

> P7 of paper-writer after retargeting (P9) from `../neurips2026/`, 2026-09-15. PDF: `main.pdf` (3 pages of main text,
> then the AI use and reproducibility statements, then references).
> ⏰ **ICLR 2027 deadlines:** abstract Sep 18, 2026, full paper Sep 25, 2026 (AoE).

## 1. Automated checks (`checks.md`)
| | Check | Detail |
|---|---|---|
| ✅ PASS | LaTeX errors | none |
| ✅ PASS | undefined references/citations | none |
| ✅ PASS | missing files | none |
| ✅ PASS | fonts | no font substitutions |
| ✅ PASS | overfull lines > 5pt | none |
| ✅ PASS | page limit | main text ends on page 3 (target 4; venue limit 9) |
| ✅ PASS | anonymity | no identifying text found (`\iclrfinalcopy` commented out) |
| ✅ PASS | numbers in prose are sourced | all listed in `sources.md` |
| ✅ PASS | value macros | 39 macros, all defined and listed |
| ✅ PASS | figures have scripts | all figures have a generating script (regenerated with `VENUE = "iclr"`) |
| ✅ PASS | citations verified | 6/6 verified |
| ⚠️ WARN | open TODOs | 2 in the AI use statement (below) |

## 2. Venue rule changes found at P2
None versus the built-in profile. See `venue.md` for the NeurIPS → ICLR differences.

## 3. What retargeting changed
| Change | Where |
|---|---|
| New `main.tex` from the official ICLR shell; `iclr2027_conference.bst` bibliography style | `main.tex`, `template/` |
| NeurIPS checklist removed | — |
| **AI use statement** (required) and **reproducibility statement** (recommended) added after the conclusion, outside the page limit | `sections/statements.tex` |
| All values, tables and figures regenerated for the ICLR layout (same 397.48 pt text width) | `../figures_scripts/` (shared; venue passed in by `make_all.py`) |
| Sections copied unchanged: the page budget and section structure fit ICLR as is | `sections/*.tex` |

## 4. What the review found (P7 read-through)
- **Font substitution (fixed).** The first ICLR compile set body text, headings and bold in fallback fonts, with no LaTeX error. The template loads `times` for
  pdfLaTeX, but Tectonic runs XeTeX, whose default encoding has no Times shapes. The fix is `\usepackage[T1]{fontenc}` in `main.tex`,
  with the style file untouched. `check_paper.py` now fails on any font substitution, so this is caught automatically next time.
- All wording and figure fixes from the NeurIPS review are carried over.

## 5. Open items for the researcher
- [ ] **AI use statement, implementation:** state how much of the model and training code was AI-generated and how it was verified.
      (It's required disclosure under "implement methods".)
- [ ] **AI use statement, review:** confirm that all authors reviewed the AI-assisted text, code and figures before keeping the
      responsibility sentence. Don't keep it unless it's true.
- [ ] **OpenReview form:** the "AI assistance" answers must match the statement in the paper.
- [ ] **Supplementary material:** the reproducibility statement promises anonymized code, results and scripts. Package them without identifying paths or names.
- [ ] **Eligibility:** check the 20-submission cap per author and the reciprocal-reviewer requirement.
- [ ] Author list and affiliations (camera-ready only).

## 6. Needs human judgment
- **Reviewer expectations (convention):** ICLR reviewers often ask for broader ablations. A sweep over d_k, or more seeds, would turn the
  untested question in Limitations into a result, but it's new work, not something to write around.
- **Figure polish:** as in the NeurIPS report (grid font size, concept-illustration labels).
- **Discussion is public on OpenReview:** keep the claims scoped to the small model, as they are now.
