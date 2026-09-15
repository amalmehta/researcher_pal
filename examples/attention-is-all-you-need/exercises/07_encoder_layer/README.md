# 07 · Encoder layer and stack

**Goal:** assemble self-attention, the feed-forward network and the residual wrapper into one encoder layer, then
stack $N$ of them (§3.1, Figure 1 left).

**Read first:** [encoder_layer](../../concept_graph.md#encoder_layer-encoder-layer-and-stack),
[attention_uses](../../concept_graph.md#attention_uses-three-uses-of-attention) · §3.1, §3.2.3
**Builds on:** your exercises 02 (multi-head attention), 03 (FFN), 06 (sublayer connection)

## What to implement

`impl.py` → `EncoderLayer(d_model, h, d_ff, dropout=0.0)` and `Encoder(d_model, h, d_ff, N, dropout=0.0)`.

$$
x' = \mathrm{LN}(x + \mathrm{Drop}(\mathrm{MultiHead}(x, x, x))), \qquad \mathrm{EncoderLayer}(x) = \mathrm{LN}(x' + \mathrm{Drop}(\mathrm{FFN}(x')))
$$

| Argument | Shape | Meaning |
|---|---|---|
| `x` | `(batch, n, d_model)` | embedded source (or previous layer's output) |
| `mask` | bool, `(batch or 1, 1, n)` | source padding mask, `True` = real token |
| returns | `(batch, n, d_model)` | |

Conventions the tests rely on: `EncoderLayer` has `self_attn`, `ffn`, `sublayer1` (around attention) and `sublayer2`
(around the FFN). `Encoder` has `layers`, an `nn.ModuleList` of `N` layers.

## Run the tests

```bash
python3.9 -m pytest exercises/07_encoder_layer
```

## Things to think about

- `SublayerConnection.forward(x, sublayer)` wants a one-argument function, but attention takes `(query, key, value, mask)`.
  How do you pass it?
- "Six identical layers": identical in structure, but do they share weights? How do you create them so they don't?
- There are no positional encodings in this exercise. What happens to the output if you shuffle the input positions?
