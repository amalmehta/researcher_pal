# 03 · Position-wise feed-forward network

**Goal:** implement Eq. (2), the two-layer MLP that processes every position on its own after attention has mixed
information across positions.

**Read first:** [ffn](../../concept_graph.md#ffn-position-wise-feed-forward-network) · §3.3, Eq. (2)

## What to implement

`impl.py` → `PositionwiseFeedForward(d_model, d_ff)` with `forward(x)`.

$$
\mathrm{FFN}(x) = \max(0,\ xW_1 + b_1)\,W_2 + b_2 \tag{2}
$$

| Argument | Shape | Meaning |
|---|---|---|
| `x` | `(batch, n, d_model)` | one vector per position |
| returns | `(batch, n, d_model)` | |

Conventions the tests rely on: `linear1 = nn.Linear(d_model, d_ff)` holds $W_1, b_1$; `linear2 = nn.Linear(d_ff, d_model)`
holds $W_2, b_2$. The paper uses $d_{model} = 512$, $d_{ff} = 2048$.

## Run the tests

```bash
python3.9 -m pytest exercises/03_position_wise_ffn
```

## Things to think about

- `nn.Linear` acts on the last dimension. What does that mean for the `n` positions in the middle?
- What is $\max(0, \cdot)$ called, and where exactly does it go?
- Why does the paper call this "two convolutions with kernel size 1"?
