# 04 · Sinusoidal positional encoding

**Goal:** give every position a fixed fingerprint of sine waves and add it to the embeddings, so the model can use
word order.

**Read first:** [pos_encoding](../../concept_graph.md#pos_encoding-sinusoidal-positional-encoding) · §3.5, §5.4
**Watch:** [positional encoding animation](../../animations/pos_encoding.html)

## What to implement

1. `sinusoidal_positional_encoding(max_len, d_model)` returns the table, shape `(max_len, d_model)`:

$$
PE_{(pos,\,2i)} = \sin\!\left(\frac{pos}{10000^{2i/d_{model}}}\right), \qquad PE_{(pos,\,2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d_{model}}}\right)
$$

2. `PositionalEncoding(d_model, dropout=0.0, max_len=5000)` with `forward(x)`: add the first `n` rows of the table to
   `x` of shape `(batch, n, d_model)`, then apply dropout (§5.4). Store the table as a **buffer** named `pe`.

`d_model` is even.

## Run the tests

```bash
python3.9 -m pytest exercises/04_positional_encoding
```

## Things to think about

- $i$ counts *pairs* of dimensions. Which dimensions get sines and which get cosines?
- $10000^{2i/d_{model}}$ can be computed directly, or as $\exp\!\big(\tfrac{2i}{d_{model}} \ln 10000\big)$. Why do many implementations
  prefer the second?
- Why a buffer rather than an `nn.Parameter`? What would go wrong with the optimizer or with `.to(device)` otherwise?
