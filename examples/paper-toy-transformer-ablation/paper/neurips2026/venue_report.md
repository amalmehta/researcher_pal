# Venue report: NeurIPS 2026 (main track format)

> P7 of paper-writer, 2026-09-15. PDF: `main.pdf` (3 pages of main text, then references and the checklist).
> **Not submission-ready:** the NeurIPS 2026 deadline has passed, and the open items below need the researcher.

## 1. Automated checks (`checks.md`)
| | Check | Detail |
|---|---|---|
| ✅ PASS | LaTeX errors | none |
| ✅ PASS | undefined references/citations | none |
| ✅ PASS | missing files | none |
| ✅ PASS | overfull lines > 5pt | none |
| ✅ PASS | page limit | main text ends on page 3 (target 4; venue limit 9) |
| ✅ PASS | anonymity | no identifying text found |
| ✅ PASS | numbers in prose are sourced | all listed in `sources.md` |
| ✅ PASS | value macros | 39 macros, all defined and listed |
| ✅ PASS | figures have scripts | all figures have a generating script |
| ✅ PASS | citations verified | 6/6 verified against arXiv DOI records |
| ⚠️ WARN | open TODOs | 2 checklist justifications + 1 unanswered checklist item (below) |

## 2. Venue rule changes found at P2
None. The profile matched the live 2026 pages.

## 3. What the review changed (P7 read-through)
The automated checks passed on the first compile, but reading the rendered pages found three problems, all fixed at the source:
1. **Contradiction:** the text said the no-warmup loss plateaued "from step 750", while the figure shows it flat by about step 25.
   The metric in `make_values.py` was brittle, because one seed drifts late. It now reports the step at which every run is within 0.15 of the median of its
   remaining losses (step 25), plus the loss range after that.
2. **Overclaim:** the caption said the two warmup configurations "overlap almost exactly". The figure shows slower early progress
   without scaling and brief single-seed spikes. The caption, results paragraph, abstract and conclusion now limit the claim to the *outcome*.
3. **Clipped label:** the "1,500" tick in the learning-rate figure was cut off. The label anchor is fixed in `lr_schedule_concept.py`.

## 4. Planted input problems and how they were handled
| Problem | Resolution |
|---|---|
| Notes say 5 seeds; the results have 3 | flagged at intake; the paper says 3 (from `\valSeeds`) |
| Claim 4 ("scaling matters more as d_k grows") has no experiment | marked unsupported and dropped as a finding; stated as untested in Limitations |
| Draft says "100% accuracy on every seed" | replaced by generated values: 99.8% mean, range 99.4–100.0% |
| `zhang2021warmup` isn't a real paper (its arXiv ID is *Attention Is All You Need*) | flagged at P6 (`../p6_input_citations.md`, title mismatch); removed from `refs.bib`; never cited |

## 5. Open items for the researcher
- [ ] **Checklist item 6** (experimental details): confirm the hyperparameters were fixed in advance and not tuned, then edit the justification.
- [ ] **Checklist item 12** (licenses): decide whether to cite PyTorch (not in your .bib) and state its license; then answer.
- [ ] **Supplementary material:** the checklist promises anonymized code and results. Package `inputs/code` and `inputs/results`,
  and remove any names or paths that identify you.
- [ ] Author list and affiliations (camera-ready only; the paper is anonymous now).

## 6. Statements and checklist status
- **Checklist:** 16 items answered from the paper's content (`checklist.tex`): 9 Yes, 6 NA, 1 open. Instructions removed; questions and guidelines unmodified.
- **LLM declaration (item 16):** NA. LLMs aren't part of the method, and NeurIPS doesn't require declaring writing, editing or formatting help.
  If the training code itself was AI-assisted, that isn't a "core method component" under this policy, but check the handbook's wording before submitting.

## 7. Needs human judgment
- **Figure 1 (left):** the Graphviz grid's text is slightly larger than the caption text. Consider a smaller font or width in `ablation_grid.py`.
- **Figure 1 (right):** the concept illustration is a draft (SVG in `figures/src/`). Polish the label placement if desired.
- **Framing:** the title states a finding, with the scope ("In a Small Transformer") in the title itself. Decide whether that's the tone you want for this venue.
- **Significance:** with 3 seeds and one model size, this reads as a workshop note rather than a main-track paper.
