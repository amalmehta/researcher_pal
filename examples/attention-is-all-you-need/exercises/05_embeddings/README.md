# 05 · Token embeddings scaled by sqrt(d_model)

**Goal:** turn token IDs into vectors the way §3.4 does, including the easy-to-miss $\sqrt{d_{model}}$ factor. In exercise
09 this same weight matrix is shared with the output projection.

**Read first:** [shared_embeddings](../../concept_graph.md#shared_embeddings-embeddings-weight-tying-and-scaling) · §3.4

## What to implement

`impl.py` → `Embeddings(vocab_size, d_model)` with `forward(tokens)`.

$$
\mathrm{embed}(t) = \sqrt{d_{model}}\; E_t
$$

| Argument | Shape | Meaning |
|---|---|---|
| `tokens` | `(batch, n)`, long | token IDs |
| returns | `(batch, n, d_model)` | scaled embedding vectors |

Convention the tests rely on: the table is `self.lut = nn.Embedding(vocab_size, d_model)`.

## Run the tests

```bash
python3.9 -m pytest exercises/05_embeddings
```

## Things to think about

- The paper never explains the $\sqrt{d_{model}}$ factor. Compare the typical size of an embedding entry with a positional
  encoding entry (between −1 and 1). What might go wrong without it?
- Later, `lut.weight` will also be the output projection. What shape does that force the matrix to have?
