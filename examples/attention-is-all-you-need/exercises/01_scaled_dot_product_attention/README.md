# 01 · Scaled dot-product attention

**Goal:** implement Eq. (1), the attention function the rest of the Transformer is built from, including the
mask the decoder will need.

**Read first:** [sdpa](../../concept_graph.md#sdpa-scaled-dot-product-attention) and
[dk_scaling](../../concept_graph.md#dk_scaling-scaling-by-the-square-root-of-d_k) · §3.2.1, Eq. (1), footnote 4, §3.2.3
**Watch:** [attention step by step](../../animations/sdpa.html) · [why divide by sqrt(d_k)](../../animations/dk_scaling.html)

## What to implement

`impl.py` → `scaled_dot_product_attention(q, k, v, mask=None)`: score every query against every key, turn each
query's scores into weights, and return the weighted sum of the values together with the weights.

$$
\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V \tag{1}
$$

| Argument | Shape | Meaning |
|---|---|---|
| `q` | `(..., n_q, d_k)` | queries |
| `k` | `(..., n_k, d_k)` | keys |
| `v` | `(..., n_k, d_v)` | values, one per key |
| `mask` | bool, broadcastable to `(..., n_q, n_k)` | `True` = this query may attend to this key |
| returns | `(..., n_q, d_v)` and `(..., n_q, n_k)` | outputs, attention weights |

`...` stands for any leading dimensions: batch now, batch and heads in exercise 02.

## Run the tests

From `examples/attention-is-all-you-need/`:

```bash
python3.9 -m pytest exercises/01_scaled_dot_product_attention
```

## Things to think about

- Which axis should the softmax normalize over so that *each query's* weights sum to 1?
- §3.2.3 sets illegal connections to −∞ "in the input of the softmax". Why before the softmax and not after?
- With extra leading dimensions, which two axes does $K^\top$ swap?
