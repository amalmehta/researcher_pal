# 11 · Label smoothing

**Goal:** train toward a slightly unsure target instead of a one-hot one (§5.4, $\epsilon_{ls} = 0.1$).

**Read first:** [label_smoothing](../../concept_graph.md#label_smoothing-label-smoothing) · §5.4

## What to implement

`impl.py` → `LabelSmoothingLoss(vocab_size, smoothing=0.1, ignore_index=None)` with `forward(logits, target)`.

$$
q'(k) = (1 - \epsilon)\,[k = y] + \frac{\epsilon}{V}, \qquad \mathcal{L} = -\sum_{k=1}^{V} q'(k)\,\log \mathrm{softmax}(\text{logits})_k
$$

| Argument | Shape | Meaning |
|---|---|---|
| `logits` | `(..., V)` | unnormalized scores |
| `target` | `(...)`, long | correct token IDs |
| returns | scalar | mean loss over positions whose target isn't `ignore_index` |

`ignore_index` is a real token ID (e.g. padding), so padded positions don't count toward the loss or the mean.

The paper doesn't say whether $\epsilon$ is spread over all $V$ tokens or only the $V-1$ wrong ones. This exercise uses all
$V$, which matches `torch.nn.CrossEntropyLoss(label_smoothing=…)` (**not in paper**).

## Run the tests

```bash
python3.9 -m pytest exercises/11_label_smoothing
```

## Things to think about

- $-\sum_k q'(k) \log p(k)$ splits into two familiar terms. What are they?
- Why is `log_softmax` better than `log(softmax(...))`?
- The loss is minimized when the model predicts exactly $q'$. Why does that "hurt perplexity but improve BLEU"?
