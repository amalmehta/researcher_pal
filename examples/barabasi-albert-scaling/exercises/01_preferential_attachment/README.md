# 01 · Preferential attachment

**Goal:** implement the rule at the heart of the model. A new vertex links to existing vertex $i$ with probability
proportional to its degree, choosing $m$ *different* vertices.

**Read first:** [preferential_attachment](../../concept_graph.md#preferential_attachment-preferential-attachment) · ¶8, E4
**Watch:** [the network growing](../../animations/ba_model.html) (step 2)
**Stack:** Python + NumPy (a numerical model)

## What to implement

1. `attachment_probabilities(degrees)`:

$$
\Pi(k_i) = \frac{k_i}{\sum_j k_j}
$$

2. `choose_targets(degrees, m, rng)` picks `m` distinct vertex indices. Each draw has probability ∝ degree among the vertices
   not picked yet. Raise `ValueError` if fewer than `m` vertices have a nonzero degree.

| Argument | Type | Meaning |
|---|---|---|
| `degrees` | 1-D NumPy int array | current degree $k_i$ of every existing vertex |
| `m` | int | number of distinct targets |
| `rng` | `numpy.random.Generator` | the only source of randomness |
| returns | float array summing to 1 / int array of `m` distinct indices | |

## Run the tests

From `examples/barabasi-albert-scaling/`:

```bash
python3.9 -m pytest exercises/01_preferential_attachment
```

## Things to think about

- A vertex with degree 0 can never be chosen. What does that mean for the very first step if the $m_0$ starting vertices have no edges?
- "$m$ different vertices": after one target is picked, how should the probabilities of the others change?
- Why pass `rng` in instead of calling `np.random` directly?
