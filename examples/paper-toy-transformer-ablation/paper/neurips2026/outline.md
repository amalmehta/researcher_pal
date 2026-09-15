# Outline: NeurIPS 2026 format

> P3 of paper-writer. The researcher's approval is simulated and marked **(simulated)**.

**Working title:** In a Small Transformer, Warmup Is Necessary but Attention Scaling Is Not.
(The researcher's title said "can't do without". This version keeps the finding and states its scope.)

## Page budget (4 pages)
| Section | Purpose | Claims | Budget |
|---|---|---|---|
| Abstract | problem, ablation, both findings with numbers, scope | C1–C3 | 0.25 |
| 1 Introduction | two one-sentence stabilizers; why it's unclear which matters; contributions | C1–C3 | 0.6 |
| 2 Related work | Transformer; warmup and post-LN (Xiong); warmup and Adam variance (Liu); training tips (Popel) | — | 0.3 |
| 3 Experimental setup | task, model, training, ablation, metrics, compute (+ Figure 1) | — | 1.2 |
| 4 Results | table, loss curves, alignment | C1–C3 | 1.2 |
| 5 Limitations | scale, d_k not varied (the former C4), post-LN only, no learning-rate search | — | 0.3 |
| 6 Conclusion | findings in scope; next step | — | 0.15 |
| After the page limit | references, checklist | — | — |

## Figure and table plan
| ID | Takeaway (first caption sentence) | Data | Script | Width |
|---|---|---|---|---|
| Fig. 1a | The 2×2 ablation grid | configs in `ablation_runs.csv` | `ablation_grid.py` (Graphviz) | 0.48 text |
| Fig. 1b | Without warmup the schedule starts at its maximum | Eq. 3 with `d_model` from `environment.json`, warmup from `ablation_runs.csv` | `lr_schedule_concept.py` (SVG → PDF) | 0.48 text |
| Table 1 | Warmup is necessary and attention scaling is not | `ablation_runs.csv` | `results_table.py` | text |
| Fig. 2 | Without warmup, training stalls early | `loss_curves.csv` | `loss_curves.py` | text |
| values | every number in the prose | `ablation_runs.csv`, `loss_curves.csv`, `environment.json`, `10_lr_schedule/impl.py` | `make_values.py` | — |

## Required items for this venue
- NeurIPS paper checklist after the references (all 16 items).
- A Limitations section (checklist item 2).
- No acknowledgments, no author information.

## Researcher decision (simulated)
Approved, including the retitled version and dropping C4 to Limitations.

## Changelog
- 2026-09-15: outline created and approved.
