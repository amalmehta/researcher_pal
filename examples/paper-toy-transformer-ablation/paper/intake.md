# Intake: warmup vs. attention scaling in a small Transformer

> P1 of paper-writer. The researcher's answers at the pause are simulated and marked **(simulated)**.

## Inputs read
| Input | What it contains |
|---|---|
| `inputs/results/ablation_runs.csv` | 12 runs = 4 configurations × 3 seeds (0, 1, 2); 1,500 steps each; accuracy, alignment, final loss, seconds |
| `inputs/results/loss_curves.csv` | training loss at step 1 and every 25 steps, per run |
| `inputs/results/environment.json` | Python 3.9.1, PyTorch 2.2.2, CPU, 8 threads; model/data/eval settings |
| `inputs/code/run_ablation.py` | the 2×2 ablation: `warmup_steps` ∈ {200, 1}; scaled vs. unscaled attention; final loss = mean of the last 4 logged losses |
| `inputs/code/transformer/` | the model: post-LN encoder-decoder, tied embeddings, sinusoidal positions, Xavier init; Adam β = (0.9, 0.98), ε = 1e-9 (`10_lr_schedule/impl.py`); greedy decoding and alignment metric (`12_final_reversal/impl.py`) |
| `inputs/notes.md` | story, 4 claims, figure ideas, related work |
| `inputs/draft/draft.md`, `refs.bib` | rough abstract and introduction; 7 references |

## Claims
| # | Claim (researcher's wording) | Evidence | Status |
|---|---|---|---|
| C1 | Without warmup, training fails every time (accuracy 0) | `ablation_runs.csv`: all 6 runs with `warmup_steps=1` (with and without scaling) have accuracy 0.0; `loss_curves.csv`: loss flat at about 2.3 from roughly step 50 | supported |
| C2 | Removing √d_k scaling changes nothing here | `no_scaling` vs `baseline`: mean accuracy 100.0% vs 99.8%, final loss 0.526 vs 0.528; curves overlap | supported, **for d_k = 16, this task and budget** |
| C3 | The baseline learns the task perfectly and a cross-attention head finds the exact reversal alignment | `baseline`: accuracy 99.4–100%, alignment ≥ 99.98% | **partial**: "perfectly" is false for seed 1 (99.4%) |
| C4 | Scaling matters more as d_k grows, so big models still need it | no run varies d_k | **unsupported** |

## Disagreements between inputs
- `notes.md` says 5 seeds per configuration; the results contain 3.
- `draft.md` says the baseline "reaches 100% accuracy on every seed"; seed 1 reached 99.4%.
- `notes.md` calls the no-warmup runs failures, which is right, but the loss never becomes NaN: it plateaus. The paper should say "fails to learn", not "diverges".
- `refs.bib` entry `zhang2021warmup` lists arXiv 1706.03762, which is the ID of *Attention Is All You Need*. To be checked at P6.

## Facts I still need from you
1. Is 3 seeds correct, or are 2 more seeds per configuration missing from the results?
2. Will you release the code (as anonymized supplementary material)?
3. Did the project use compute beyond these 12 runs? (NeurIPS checklist item 8 asks.)
4. Should the paper cite PyTorch? It isn't in your .bib.
5. Author list and affiliations, needed only for camera-ready.

## Researcher decisions (simulated)
- C1 and C2 confirmed. C3 confirmed, reworded to "solves the task" with the measured range. **C4 dropped** as a finding, and mentioned as untested in Limitations.
- 3 seeds is correct ("5 was the plan; we ran 3").
- Code: yes, as anonymized supplementary material. Compute: nothing beyond these runs.
- PyTorch citation: undecided, so it stays a TODO in the checklist.
- Remove any reference that fails verification.
