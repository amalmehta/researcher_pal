# 02 · Multi-head attention

**Goal:** run $h$ attention heads in parallel, each in its own learned subspace, then concatenate and mix them.
This is the block used in every attention sub-layer of the model.

**Read first:** [mha](../../concept_graph.md#mha-multi-head-attention) · §3.2.2, Figure 2 (right)
**Builds on:** your `scaled_dot_product_attention` from exercise 01

## What to implement

`impl.py` → `MultiHeadAttention(d_model, h)` with `forward(query, key, value, mask=None)`.

$$
\mathrm{MultiHead}(Q,K,V) = \mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_h)\,W^O, \qquad \mathrm{head}_i = \mathrm{Attention}(QW_i^Q,\ KW_i^K,\ VW_i^V)
$$

| Argument | Shape | Meaning |
|---|---|---|
| `query` | `(batch, n_q, d_model)` | where queries come from |
| `key`, `value` | `(batch, n_k, d_model)` | where keys and values come from |
| `mask` | bool, `(batch or 1, n_q or 1, n_k)` | `True` = may attend; the same mask for every head |
| returns | `(batch, n_q, d_model)` | |

Conventions the tests rely on:
- `w_q`, `w_k`, `w_v`, `w_o` are `nn.Linear(d_model, d_model, bias=False)`. The paper's projections are plain matrices.
- `d_k = d_v = d_model // h`. Output features `0 … d_k-1` of `w_q` belong to head 1, the next `d_k` to head 2, and so on.
  (This is exactly $h$ separate $W_i^Q$ matrices stacked.)
- After `forward`, `self.last_weights` holds the attention weights, shape `(batch, h, n_q, n_k)`.
- Raise `ValueError` if `d_model` isn't divisible by `h`.

## Run the tests

```bash
python3.9 -m pytest exercises/02_multi_head_attention
```

## Things to think about

- Your attention function from 01 already handles leading dimensions. What shape should $Q$, $K$, $V$ have so that the
  heads become one of those leading dimensions?
- After attention you have `(batch, h, n_q, d_k)`. What has to happen before a `view` can give `(batch, n_q, h*d_k)`?
- The mask is `(batch, n_q, n_k)` but the scores are `(batch, h, n_q, n_k)`. How do you make one mask cover every head?
