# 06 · Residual connection, dropout and LayerNorm

**Goal:** build the wrapper used around *every* attention and feed-forward sub-layer, with the exact ordering from
§3.1 and §5.4.

**Read first:** [sublayer](../../concept_graph.md#sublayer-residual-connection-dropout-and-layernorm) · §3.1, §5.4 (Residual Dropout)

## What to implement

`impl.py` → `SublayerConnection(d_model, dropout=0.0)` with `forward(x, sublayer)`, where `sublayer` is any function
from `(batch, n, d_model)` to the same shape.

$$
\mathrm{output} = \mathrm{LayerNorm}\big(x + \mathrm{Dropout}(\mathrm{Sublayer}(x))\big)
$$

Conventions the tests rely on: `self.norm = nn.LayerNorm(d_model)`, `self.dropout = nn.Dropout(dropout)`.

## Run the tests

```bash
python3.9 -m pytest exercises/06_sublayer_connection
```

## Things to think about

- §5.4: "We apply dropout to the output of each sub-layer, before it is added to the sub-layer input and normalized."
  Which of the three operations happens first, second, third?
- Many modern codebases use *pre*-LN, $x + \mathrm{Sublayer}(\mathrm{LN}(x))$. One test tells them apart. Which one, and how?
