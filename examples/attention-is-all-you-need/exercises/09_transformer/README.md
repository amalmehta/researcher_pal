# 09 · The full Transformer

**Goal:** wire everything into Figure 1: embeddings, positional encodings, the encoder and decoder stacks, and the
tied output projection.

**Read first:** [transformer](../../concept_graph.md#transformer-the-full-transformer),
[shared_embeddings](../../concept_graph.md#shared_embeddings-embeddings-weight-tying-and-scaling) · Figure 1, §3.4, Table 3
**Builds on:** your exercises 04, 05, 07, 08

## What to implement

`impl.py` → `Transformer(vocab_size, d_model=512, h=8, d_ff=2048, N=6, dropout=0.1, max_len=5000)` with
`encode`, `decode` and `forward`.

```
src ─► src_embed (×√d_model) ─► + PE ─► dropout ─► Encoder ─────────────► memory
tgt ─► tgt_embed (×√d_model) ─► + PE ─► dropout ─► Decoder(·, memory) ─► generator ─► logits
```

$$
\mathrm{logits} = \mathrm{Decoder}(\cdot)\,E^\top, \qquad E = \texttt{src\_embed.lut.weight} = \texttt{tgt\_embed.lut.weight} = \texttt{generator.weight}
$$

| Method | Input | Output |
|---|---|---|
| `encode(src, src_mask=None)` | `src` `(batch, n_src)` long | memory `(batch, n_src, d_model)` |
| `decode(memory, tgt, src_mask=None, tgt_mask=None)` | `tgt` `(batch, n_tgt)` long | `(batch, n_tgt, d_model)` |
| `forward(src, tgt, src_mask=None, tgt_mask=None)` | both | logits `(batch, n_tgt, vocab_size)` |

Conventions the tests rely on: `src_embed`, `tgt_embed` (exercise 05), `pos_encoding` (exercise 04), `encoder`,
`decoder`, `generator = nn.Linear(d_model, vocab_size, bias=False)`. The three weight matrices must be **the same
Parameter object**.

Initialize every weight matrix (`p.dim() > 1`) with `nn.init.xavier_uniform_`. This is **not in paper**, but it's a common
choice, and without it the √d_model scaling makes the default `nn.Embedding` init (std 1) far too large.

## Run the tests

```bash
python3.9 -m pytest exercises/09_transformer
```

The base-configuration parameter count test builds a 63M-parameter model, which takes a few seconds.

## Things to think about

- `forward` returns logits, not probabilities. Why leave the softmax to the loss function?
- If you initialize *after* tying, how many times does the shared matrix get initialized? Does it matter?
- Table 3 says the base model has 65M parameters. Count yours for a 37,000-token vocabulary. Where could the difference come from?
