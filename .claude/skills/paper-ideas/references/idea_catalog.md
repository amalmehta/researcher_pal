# Idea catalog

What to look for when generating improvement ideas. Each prompt is a question to ask of the paper. An idea is only
worth keeping if you can point at the evidence that raised it and state the concrete change.

## Contents
1. Writing and presentation
2. Evidence and experiments
3. Simulated reviewer critique
4. New research directions
5. Ranking guide
6. Anti-patterns

---

## 1. Writing and presentation

| Look at | Ask | Typical idea |
|---|---|---|
| Title and abstract | Does the abstract contain the key numbers and the scope? Does the title overstate? | add the headline number; put the scope ("in small models") into the title |
| Contribution bullets | Does each bullet point at a figure, table or section that proves it? | re-point or merge bullets; drop one that nothing supports |
| Claims vs evidence | Is any verb stronger than the evidence ("shows", "always") given the seeds, scale or datasets? | calibrate the wording (see the writing guide in paper-writer) |
| Figures | Is the takeaway in the caption's first sentence? Is text at least 7 pt? Are there color-only encodings, clipped labels, or unexplained shading or error bars? | rewrite the caption; add markers; enlarge fonts; explain the bands |
| Tables | Is the best value marked? Are ranges or uncertainty explained? Are there too many digits? | round consistently; explain the brackets; move the table next to its first mention |
| Structure | Is the setup buried? Are results repeated? Is related work too long or too thin? | reorder; cut repetition; position against the closest work |
| Page budget | Space left under the limit? | use it for the most-requested analysis, not padding |
| Notation | Is each symbol defined before use? Is any symbol used for two things? | a notation line in the setup section |
| Limitations and statements | Honest and specific? Do they match what the checklist or statement answers claim? | fix mismatches; name the untested regimes |

## 2. Evidence and experiments

| Look at | Ask | Typical idea |
|---|---|---|
| Seeds and variance | How many runs? Is variance reported and explained? Is any claim sensitive to one seed? | more seeds; report std or CI; say what error bars mean |
| Baselines | Is the strongest reasonable baseline included and tuned as carefully as the method? | add the baseline, with equal tuning effort |
| **Confounds** | Does the manipulated factor change something else too (learning rate, parameter count, compute, data order)? | a control condition that separates the two |
| Ablations | Is each component's contribution shown? | remove one component at a time |
| Sensitivity | Are the results robust to key hyperparameters and scale? | a sweep over the one knob reviewers will ask about |
| Generality | One task, dataset or size? | a second task or size, at the same compute |
| Mechanism | Is the *why* shown, or only the outcome? | a diagnostic (gradient norms, attention entropy, degree over time) |
| Statistics | Are comparisons made without a test when differences are small? | a paired test or bootstrap CI |
| Reproducibility | Are code, data, environment and compute reported? | fill the gaps (checklist items) |

For each experiment idea, state **what result would change the conclusion**. If no outcome would change anything,
the experiment isn't worth running.

## 3. Simulated reviewer critique

Write as a reviewer for the target venue, using its profile's reviewer expectations. Cover the standard review dimensions:

| Dimension | Reviewer question | Answer with |
|---|---|---|
| Soundness | Do the experiments support the claims? Any confound or missing control? | control experiment, calibrated claim |
| Significance | Why does this matter beyond the toy setting? | a scale or generality experiment, a sharper motivation |
| Novelty | How is this different from <closest work found in I4>? | a positioning paragraph; the experiment prior work didn't run |
| Clarity | Could someone reimplement it from the paper alone? | setup details, pseudocode, notation |
| Reproducibility | Code, seeds, compute? | supplement, statements |

Venue notes (**convention**): NeurIPS reviewers use the checklist lens (error bars, compute, limitations). ICLR
reviewers push on ablations, and reviews are public. ICML reviewers value technical depth and precise claims.

For a **published paper**, criticize it the way a careful reviewer would today, and check the literature for later work
that already raised or resolved the point. Cite it if found (verified records only), and never present a known
critique as your own discovery.

## 4. New research directions

| Direction | Prompt |
|---|---|
| Relax an assumption | Which assumption does the result depend on most (linearity, a fixed size, post-LN, uniform arrival)? What happens without it? |
| Scale or transfer | Does the effect grow, shrink or flip with size, data or domain? |
| Mechanism | What explains the effect, and what measurement would show it? |
| Combine | Which related record from I4 suggests a combination or a contradiction worth testing? |
| Practical | Is there a practitioner's rule of thumb this could become, and what evidence would it need? |

Each direction needs a **first experiment** small enough to fit the compute budget, or it belongs in "future work" only.

## 5. Ranking guide

| Impact | Meaning |
|---|---|
| High | changes whether a main claim holds, answers the most likely reviewer objection, or opens a clearly testable direction |
| Medium | strengthens a claim or noticeably improves clarity or reviewer confidence |
| Low | polish |

Order by impact, then by effort and compute. Within the same impact, put ideas that fit the budget first.

## 6. Anti-patterns

- **Generic ideas:** "add more experiments", "improve the writing". Name *which* experiment or *which* sentence.
- **Hidden claims of novelty:** "this has never been studied". Use the literature labels instead.
- **Uncited critiques:** repeating a well-known critique of a published paper without citing where it was made.
- **Unapproved changes:** editing the draft or running experiments before approval.
- **Overpromising:** experiment ideas with compute estimates guessed rather than measured with a pilot.
