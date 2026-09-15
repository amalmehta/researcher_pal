# 02 · Deriving γ = 3 (worked problem)

**Goal:** derive the model's degree distribution by hand, as ¶10 does in a few dense lines. First find how one vertex's
degree grows, then what that implies for $P(k)$.

**Read first:** [degree_growth_law](../../concept_graph.md#degree_growth_law-degree-growth-law),
[degree_exponent_derivation](../../concept_graph.md#degree_exponent_derivation-deriving-the-degree-exponent) · ¶10, E6–E8
**Watch:** [rich get richer: from k_i(t) to γ = 3](../../animations/degree_growth_law.html)

## Problem

In the model (¶8), each time step adds one vertex with $m$ edges. Each new edge lands on an existing vertex $i$ with probability
$\Pi(k_i) = k_i / \sum_j k_j$. Vertex $i$ arrives at time $t_i$ with $k_i(t_i) = m$. Treat $k_i$ and $t$ as continuous (large $t$) and show:

**(a)** $\dfrac{\partial k_i}{\partial t} = \dfrac{k_i}{2t}$, and hence $k_i(t) = m\left(\dfrac{t}{t_i}\right)^{1/2}$.

**(b)** $P\big(k_i(t) < k\big) = P\!\left(t_i > \dfrac{m^2 t}{k^2}\right)$.

**(c)** Vertices arrive at equal time intervals, so a randomly chosen vertex's $t_i$ is uniform over the $m_0 + t$ vertices present. Show that

$$
P(k) = \frac{\partial P(k_i(t) < k)}{\partial k} = \frac{2m^2 t}{m_0 + t}\,\frac{1}{k^3} \quad\longrightarrow\quad P(k) = \frac{2m^2}{k^3} \text{ at long times.}
$$

## A complete answer shows

- where "$m$ edges per step" enters the rate, and why $\sum_j k_j \approx 2mt$ (and what that approximation ignores);
- solving the rate equation with the initial condition $k_i(t_i) = m$;
- why the inequality flips direction in (b);
- the probability that a uniformly chosen vertex has $t_i \le x$, and the derivative in (c);
- why $\gamma = 3$ doesn't depend on $m$;
- a sanity check: does $2m^2/k^3$ integrate to 1 over $k \ge m$?

## Write your answer

In `answer.md`, in Markdown with `$…$` math. Plain steps are fine. Say which assumption each step uses.

## Things to think about

- The paper writes $\partial k_i/\partial t = k_i/2t$ directly. Which step did it skip?
- Simulations (Fig. 2A) give $\gamma = 2.9 \pm 0.1$, not 3. Name two reasons the numbers might differ.
