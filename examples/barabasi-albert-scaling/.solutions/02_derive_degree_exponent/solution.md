# Solution: 02 · Deriving γ = 3

Target: ¶10, E6–E8 of arXiv:cond-mat/9910332v1, ending at $P(k) = 2m^2/k^3$.

## (a) How one vertex's degree grows

1. **Rate.** Each time step adds $m$ edges. Each one lands on vertex $i$ with probability $\Pi(k_i)$, so the expected
   gain per step is $m\,\Pi(k_i)$. In the continuum approximation this expected gain is the derivative:
   $$\frac{\partial k_i}{\partial t} = m\,\Pi(k_i) = \frac{m\,k_i}{\sum_j k_j}.$$
   (This ignores that the $m$ targets must be distinct, a small effect once the network is large.)
2. **Degree sum.** Every edge adds 2 to $\sum_j k_j$. After $t$ steps, $mt$ edges have been added, so
   $\sum_j k_j = 2mt + (\text{starting degrees}) \approx 2mt$ for large $t$. The approximation ignores the starting edges.
3. **Combine:** $\dfrac{\partial k_i}{\partial t} = \dfrac{m\,k_i}{2mt} = \dfrac{k_i}{2t}$. The $m$ cancels. This is the step the paper skips.
4. **Solve by separation:** $\dfrac{dk_i}{k_i} = \dfrac{dt}{2t} \Rightarrow \ln k_i = \tfrac12 \ln t + C \Rightarrow k_i = A\,t^{1/2}$.
5. **Initial condition:** $k_i(t_i) = m \Rightarrow A = m\,t_i^{-1/2}$, so $k_i(t) = m\,(t/t_i)^{1/2}$. ✔ (E6)

## (b) From degrees to arrival times

With $m, t, t_i, k > 0$:
$$k_i(t) < k \iff m\left(\frac{t}{t_i}\right)^{1/2} < k \iff \frac{t}{t_i} < \frac{k^2}{m^2} \iff t_i > \frac{m^2 t}{k^2}.$$
The inequality flips because $t_i$ is in the denominator: *later* arrivals have *smaller* degrees. Since each vertex's degree
is a decreasing function of its arrival time, the two events are the same, so their probabilities are equal. ✔ (E7, first equality)

## (c) Uniform arrival times give the distribution

1. **Uniform arrivals.** A uniformly chosen vertex among the $m_0 + t$ present has $t_i$ uniform, so $P(t_i \le x) = \dfrac{x}{m_0 + t}$.
2. **Cumulative distribution:**
   $$P(k_i(t) < k) = 1 - P\!\left(t_i \le \frac{m^2 t}{k^2}\right) = 1 - \frac{m^2 t}{k^2 (t + m_0)}. \quad ✔ \text{(E7)}$$
3. **Density:** differentiate with respect to $k$ (not $t$):
   $$P(k) = \frac{\partial}{\partial k}\left[1 - \frac{m^2 t}{t + m_0}\,k^{-2}\right] = \frac{m^2 t}{t + m_0}\cdot 2k^{-3} = \frac{2m^2 t}{m_0 + t}\,\frac{1}{k^3}.$$
4. **Long times:** $t/(m_0 + t) \to 1$, so $P(k) = \dfrac{2m^2}{k^3}$ and $\gamma = 3$. ✔ (E8)
5. **Why not $m$:** $m$ only appears in the prefactor $2m^2$, so the exponent can't depend on it. The time dependence also
   disappears as $t \to \infty$, which is the analytic version of "stationary".

## Sanity check

Every vertex has degree at least $m$, and
$$\int_m^\infty \frac{2m^2}{k^3}\,dk = 2m^2 \left[-\frac{1}{2k^2}\right]_m^\infty = 2m^2 \cdot \frac{1}{2m^2} = 1.$$
The distribution is normalized.

## Why simulations give 2.9 ± 0.1 (discussion)

- Finite size: at $t = 200{,}000$ the tail is cut off near $k \approx m\sqrt{t}$, and few vertices sit in it.
- The continuum approximation treats degrees as continuous and ignores fluctuations, and it's rough near $k = m$. The exact
  discrete result is $P(k) = \frac{2m(m+1)}{k(k+1)(k+2)}$, which only behaves like $2m^2/k^3$ for $k \gg m$. **not in paper**
- Reading slopes off noisy log-log plots is biased. **not in paper**

## Common wrong turns (for hints)

- **Dropping the $m$** in $m\,\Pi(k_i)$ gives $\partial k_i/\partial t = k_i/(2mt)$, so $k_i \propto t^{1/(2m)}$, an exponent that wrongly depends on $m$.
- **Not flipping the inequality**, which gives $P(t_i < m^2t/k^2)$ and then a *negative* density.
- **Differentiating in $t$** instead of $k$. The distribution over $k$ is what's wanted, at fixed $t$.
- **Forgetting the normalization** $1/(m_0 + t)$ of the uniform arrival time, which leaves the prefactor wrong or $t$-dependent at long times.
- **Using $\sum_j k_j = mt$** (edges, not ends), which gives $k_i \propto t$ and a wrong exponent.
