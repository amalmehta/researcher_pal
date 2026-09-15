# 08 · Decoder layer, causal mask and stack

**Goal:** build the causal mask and a decoder layer with three sub-layers (masked self-attention, encoder-decoder
attention, feed-forward), then stack $N$ of them (§3.1, Figure 1 right).

**Read first:** [decoder_layer](../../concept_graph.md#decoder_layer-decoder-layer-and-stack),
[causal_mask](../../concept_graph.md#causal_mask-causal-mask-and-shifted-outputs),
[attention_uses](../../concept_graph.md#attention_uses-three-uses-of-attention) · §3.1, §3.2.3
**Watch:** [attention step by step](../../animations/sdpa.html) (turn on the causal mask)
**Builds on:** your exercises 02, 03, 06

## What to implement

1. `subsequent_mask(n)` returns a bool tensor `(1, n, n)`, `True` where position $i$ may attend to position $j$, i.e. $j \le i$.
2. `DecoderLayer(d_model, h, d_ff, dropout=0.0)` with `forward(x, memory, src_mask=None, tgt_mask=None)`:

$$
a = \mathrm{LN}(x + \mathrm{Drop}(\mathrm{MHA}(x, x, x, \text{tgt\_mask}))),\quad
b = \mathrm{LN}(a + \mathrm{Drop}(\mathrm{MHA}(a, z, z, \text{src\_mask}))),\quad
\mathrm{out} = \mathrm{LN}(b + \mathrm{Drop}(\mathrm{FFN}(b)))
$$

3. `Decoder(d_model, h, d_ff, N, dropout=0.0)`: $N$ layers with separate weights, all reading the same `memory`.

| Argument | Shape | Meaning |
|---|---|---|
| `x` | `(batch, n_tgt, d_model)` | embedded (shifted) target |
| `memory` | `(batch, n_src, d_model)` | final encoder output $z$ |
| `src_mask` | bool, `(batch or 1, 1, n_src)` | source padding |
| `tgt_mask` | bool, `(batch or 1, n_tgt, n_tgt)` | causal (and target padding) |

Conventions the tests rely on: `self_attn`, `cross_attn`, `ffn`, `sublayer1`, `sublayer2`, `sublayer3`; `Decoder.layers`.

## Run the tests

```bash
python3.9 -m pytest exercises/08_decoder_layer
```

## Things to think about

- In encoder-decoder attention, which argument is the query and which are the keys and values? If $n_{src} = n_{tgt}$,
  would a swap even crash?
- Does the encoder-decoder attention need the causal mask? Why or why not?
