# 03 · Final: grow the network and measure its scaling

**Goal:** simulate the model and reproduce its three central numerical claims at laptop scale.

**Read first:** [ba_model](../../concept_graph.md#ba_model-the-growth-and-preferential-attachment-model),
[ablation_models_a_b](../../concept_graph.md#ablation_models_a_b-models-a-and-b),
[degree_growth_law](../../concept_graph.md#degree_growth_law-degree-growth-law) · ¶8–¶10, Fig. 2
**Watch:** [the network growing](../../animations/ba_model.html) · [rich get richer](../../animations/degree_growth_law.html)
**Builds on:** your `choose_targets` from exercise 01, and the result you derived in 02

## The results we reproduce

With $t = 20{,}000$ and $m_0 = m = 5$:
1. **Scale-free:** the fitted degree exponent is close to 3 (the paper: 2.9 ± 0.1 in simulation, 3 analytically).
2. **Rich get richer:** mean degree against arrival time has slope ≈ −1/2 on log-log axes, from $k_i(t) = m(t/t_i)^{1/2}$.
3. **Both ingredients are needed:** model A (growth with uniform attachment) has no hubs. Its largest degree is far below the model's.

**Not reproduced:** the real-network data (Fig. 1), model B, $t = 200{,}000$.

## What's provided and what you implement

Provided in `impl.py` (measurement tools, not from the paper):
- `fit_power_law_exponent(degrees, k_min)` gives the standard maximum-likelihood estimate of $\gamma$. The paper read slopes off plots instead.
- `growth_exponent(degrees, m0)` gives the log-log slope of mean degree against arrival time.

You implement:
1. `grow_network(t, m, m0, rng, preferential=True)`: start from $m_0$ vertices joined as a **complete graph** (the paper never says
   how the first vertices are connected; **not in paper**). Then run $t$ steps, each adding one vertex with $m$ edges to $m$ different
   existing vertices: preferentially with your `choose_targets`, or uniformly for model A. Return every vertex's final degree in arrival order.
2. `simulate_and_measure(seed=0, t=20000, m=5, m0=5)` grows both models with one `numpy.random.default_rng(seed)` and returns
   `{"gamma", "growth_slope", "max_degree_ba", "max_degree_a"}`.

## Run the tests

```bash
python3.9 -m pytest exercises/03_final_scale_free
```

## Things to think about

- Your `choose_targets` rebuilds probabilities over all vertices each step, which is $O(N)$. It's fine here. How would you make each
  step $O(1)$? (Hint: pick a random *end* of a random edge.)
- Why does a complete-graph start need $m_0 \ge 2$, and why does the model require $m \le m_0$?
- The fitted γ changes a little with `k_min`. Why can't you use `k_min = 1`?
