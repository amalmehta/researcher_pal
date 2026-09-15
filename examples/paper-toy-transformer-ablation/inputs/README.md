# Researcher inputs (simulated)

This folder plays the part of what a researcher hands to paper-writer. Everything here is a **test fixture**.

| Input | Path | Real or simulated |
|---|---|---|
| Code repository | `code/` (the Attention example's reference implementation + `run_ablation.py`) | real code |
| Results data | `results/ablation_runs.csv`, `results/loss_curves.csv`, `results/environment.json` | real runs (4 configs × 3 seeds, CPU) |
| Notes / outline | `notes.md` | simulated researcher notes |
| Existing draft + .bib | `draft/draft.md`, `draft/refs.bib` | simulated |

## Planted problems the skill must catch

1. **Seed count mismatch:** `notes.md` says 5 seeds per config; the results have 3. Intake must flag it, and the paper must say 3.
2. **Unsupported claim:** `notes.md` claim 4 ("scaling matters more as d_k grows") has no experiment behind it.
   Intake must mark it unsupported, and it must not appear in the paper as a finding.
3. **Wrong hand-typed number:** `draft/draft.md` says the baseline reaches 100% accuracy on every seed. One seed
   reached 99.4%. The paper must use the generated value instead.
4. **Fake citation:** `draft/refs.bib` entry `zhang2021warmup` doesn't exist (its arXiv ID belongs to a different paper).
   Citation verification must flag it, and it must not be cited.
