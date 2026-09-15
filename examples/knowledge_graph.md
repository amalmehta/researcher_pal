# Knowledge graph

> Maintained by researcher-pal: one map of what you've learned, across all papers.
> **Status:** ✅ learned · 🔶 learning · ☑️ known before (you said so)
> **Last updated:** 2026-09-15
>
> *Example file.* It shows the state after the two example runs in this folder. The learner's step-5 answers are
> simulated, and the reference solutions stand in for the learner's work. A real run writes
> `~/researcher-pal/knowledge_graph.md`.

## Map

Arrows go from prerequisite to topic. Colors show status; boxes group topics by field.

```mermaid
flowchart LR
  classDef learned fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef learning fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef known fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e

  subgraph math["Mathematics and probability"]
    probability_distribution["Probability distributions"]:::known
    softmax["Softmax"]:::known
    dot_product["Dot product as similarity"]:::known
    cross_entropy["Cross-entropy loss"]:::known
    differential_equations["Rate equations (ODEs)"]:::known
    graphs_and_degree["Graphs, vertices, edges, degree"]:::known
    power_law["Power laws and log-log plots"]:::learned
  end

  subgraph optimization["Optimization"]
    adam["Adam optimizer"]:::known
    lr_schedule["Warmup learning-rate schedule"]:::learned
    label_smoothing["Label smoothing"]:::learned
  end

  subgraph dl["Deep learning"]
    layer_norm["Layer normalization"]:::known
    residual["Residual connections"]:::known
    dropout["Dropout"]:::known
    token_embed["Token embeddings + output projection"]:::known
    encoder_decoder["Encoder-decoder, autoregressive generation"]:::learned
    attention_fn["Attention as a soft lookup"]:::learned
    dk_scaling["Scaling by sqrt(d_k)"]:::learned
    sdpa["Scaled dot-product attention"]:::learned
    causal_mask["Causal mask + shifted outputs"]:::learned
    mha["Multi-head attention"]:::learned
    attention_uses["Three uses of attention"]:::learned
    sublayer["Residual + dropout + LayerNorm"]:::learned
    ffn["Position-wise feed-forward"]:::learned
    shared_embeddings["Shared embeddings, times sqrt(d_model)"]:::learned
    pos_encoding["Sinusoidal positional encoding"]:::learned
    encoder_layer["Encoder layer + stack"]:::learned
    decoder_layer["Decoder layer + stack"]:::learned
    transformer["The full Transformer"]:::learned
  end

  subgraph netsci["Network science"]
    degree_distribution["Degree distribution P(k)"]:::learned
    growth["Growth"]:::learned
    preferential_attachment["Preferential attachment"]:::learned
    ba_model["Growth + preferential attachment model"]:::learned
    ablation_models_a_b["Models A and B"]:::learned
    degree_growth_law["Degree growth law"]:::learned
    degree_exponent_derivation["Deriving P(k) = 2m^2/k^3"]:::learned
  end

  probability_distribution --> softmax
  probability_distribution --> cross_entropy
  probability_distribution --> degree_distribution
  softmax --> attention_fn
  dot_product --> attention_fn
  softmax --> dk_scaling
  dot_product --> dk_scaling
  attention_fn --> sdpa
  dk_scaling --> sdpa
  sdpa --> causal_mask
  encoder_decoder --> causal_mask
  sdpa --> mha
  mha --> attention_uses
  causal_mask --> attention_uses
  residual --> sublayer
  layer_norm --> sublayer
  dropout --> sublayer
  attention_uses --> encoder_layer
  attention_uses --> decoder_layer
  sublayer --> encoder_layer
  sublayer --> decoder_layer
  ffn --> encoder_layer
  ffn --> decoder_layer
  token_embed --> shared_embeddings
  encoder_layer --> transformer
  decoder_layer --> transformer
  shared_embeddings --> transformer
  pos_encoding --> transformer
  adam --> lr_schedule
  cross_entropy --> label_smoothing
  graphs_and_degree --> degree_distribution
  graphs_and_degree --> preferential_attachment
  growth --> ba_model
  preferential_attachment --> ba_model
  ba_model --> ablation_models_a_b
  ba_model --> degree_growth_law
  differential_equations --> degree_growth_law
  degree_growth_law --> degree_exponent_derivation
  power_law --> degree_exponent_derivation
```

## Topics

| Topic | Status | Field | Papers | Evidence | Updated |
|---|---|---|---|---|---|
| `cross_entropy`: Cross-entropy loss | ☑️ known | Mathematics and probability | [Attention](attention-is-all-you-need/concept_graph.md#cross_entropy-cross-entropy-loss) | said known at start of Attention | 2026-09-15 |
| `differential_equations`: Rate equations | ☑️ known | Mathematics and probability | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#differential_equations-rate-equations) | said known at start of Barabási–Albert | 2026-09-15 |
| `dot_product`: Dot product as similarity | ☑️ known | Mathematics and probability | [Attention](attention-is-all-you-need/concept_graph.md#dot_product-dot-product-as-similarity) | said known at start of Attention | 2026-09-15 |
| `graphs_and_degree`: Graphs, vertices, edges and degree | ☑️ known | Mathematics and probability | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#graphs_and_degree-graphs-vertices-edges-and-degree) | said known at start of Barabási–Albert | 2026-09-15 |
| `power_law`: Power laws and log-log plots | ✅ learned | Mathematics and probability | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#power_law-power-laws-and-log-log-plots) | exercise 03 passed (fitted γ) | 2026-09-15 |
| `probability_distribution`: Probability distributions | ☑️ known | Mathematics and probability | [Attention](attention-is-all-you-need/concept_graph.md#probability_distribution-probability-distributions); [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#probability_distribution-probability-distributions) | said known at start of Attention; reused as known in Barabási–Albert | 2026-09-15 |
| `softmax`: Softmax | ☑️ known | Mathematics and probability | [Attention](attention-is-all-you-need/concept_graph.md#softmax-softmax) | said known at start of Attention | 2026-09-15 |
| `adam`: Adam optimizer | ☑️ known | Optimization | [Attention](attention-is-all-you-need/concept_graph.md#adam-adam-optimizer) | said known at start of Attention | 2026-09-15 |
| `label_smoothing`: Label smoothing | ✅ learned | Optimization | [Attention](attention-is-all-you-need/concept_graph.md#label_smoothing-label-smoothing) | exercise 11 passed | 2026-09-15 |
| `lr_schedule`: Warmup learning-rate schedule | ✅ learned | Optimization | [Attention](attention-is-all-you-need/concept_graph.md#lr_schedule-warmup-learning-rate-schedule) | exercise 10 passed | 2026-09-15 |
| `attention_fn`: Attention as a soft lookup | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#attention_fn-attention-as-a-soft-lookup) | covered in exercise 01 (passed) | 2026-09-15 |
| `attention_uses`: Three uses of attention | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#attention_uses-three-uses-of-attention) | exercises 07–09 passed | 2026-09-15 |
| `causal_mask`: Causal mask and shifted outputs | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#causal_mask-causal-mask-and-shifted-outputs) | exercise 08 passed | 2026-09-15 |
| `decoder_layer`: Decoder layer and stack | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#decoder_layer-decoder-layer-and-stack) | exercise 08 passed | 2026-09-15 |
| `dk_scaling`: Scaling by the square root of d_k | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#dk_scaling-scaling-by-the-square-root-of-d_k) | exercise 01 passed (scaling test) | 2026-09-15 |
| `dropout`: Dropout | ☑️ known | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#dropout-dropout) | said known at start of Attention | 2026-09-15 |
| `encoder_decoder`: Encoder-decoder and autoregressive generation | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#encoder_decoder-encoder-decoder-and-autoregressive-generation) | exercise 12 passed (greedy decoding) | 2026-09-15 |
| `encoder_layer`: Encoder layer and stack | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#encoder_layer-encoder-layer-and-stack) | exercise 07 passed | 2026-09-15 |
| `ffn`: Position-wise feed-forward network | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#ffn-position-wise-feed-forward-network) | exercise 03 passed | 2026-09-15 |
| `layer_norm`: Layer normalization | ☑️ known | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#layer_norm-layer-normalization) | said known at start of Attention | 2026-09-15 |
| `mha`: Multi-head attention | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#mha-multi-head-attention) | exercise 02 passed | 2026-09-15 |
| `pos_encoding`: Sinusoidal positional encoding | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#pos_encoding-sinusoidal-positional-encoding) | exercise 04 passed | 2026-09-15 |
| `residual`: Residual connections | ☑️ known | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#residual-residual-connections) | said known at start of Attention | 2026-09-15 |
| `sdpa`: Scaled dot-product attention | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#sdpa-scaled-dot-product-attention) | exercise 01 passed | 2026-09-15 |
| `shared_embeddings`: Embeddings, weight tying and scaling | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#shared_embeddings-embeddings-weight-tying-and-scaling) | exercises 05 and 09 passed | 2026-09-15 |
| `sublayer`: Residual connection, dropout and LayerNorm | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#sublayer-residual-connection-dropout-and-layernorm) | exercise 06 passed | 2026-09-15 |
| `token_embed`: Token embeddings and output projection | ☑️ known | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#token_embed-token-embeddings-and-output-projection) | said known at start of Attention | 2026-09-15 |
| `transformer`: The full Transformer | ✅ learned | Deep learning | [Attention](attention-is-all-you-need/concept_graph.md#transformer-the-full-transformer) | exercises 09 and 12 passed | 2026-09-15 |
| `ablation_models_a_b`: Models A and B | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#ablation_models_a_b-models-a-and-b) | exercise 03 passed (model A has no hubs) | 2026-09-15 |
| `ba_model`: The growth and preferential attachment model | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#ba_model-the-growth-and-preferential-attachment-model) | exercise 03 passed | 2026-09-15 |
| `degree_distribution`: The degree distribution P(k) | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#degree_distribution-the-degree-distribution-pk) | exercise 03 passed | 2026-09-15 |
| `degree_exponent_derivation`: Deriving the degree exponent | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#degree_exponent_derivation-deriving-the-degree-exponent) | problem 02 accepted | 2026-09-15 |
| `degree_growth_law`: Degree growth law | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#degree_growth_law-degree-growth-law) | problem 02 accepted; exercise 03 measured slope −0.51 | 2026-09-15 |
| `growth`: Growth | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#growth-growth) | exercise 03 passed | 2026-09-15 |
| `preferential_attachment`: Preferential attachment | ✅ learned | Network science | [Barabási–Albert](barabasi-albert-scaling/concept_graph.md#preferential_attachment-preferential-attachment) | exercise 01 passed | 2026-09-15 |

## Papers

| Paper | Folder | Started | Topics learned / concepts in paper |
|---|---|---|---|
| Attention Is All You Need (arXiv 1706.03762v7) | `examples/attention-is-all-you-need/` | 2026-09-15 | 16 learned + 9 known / 31 |
| Emergence of Scaling in Random Networks (arXiv cond-mat/9910332v1) | `examples/barabasi-albert-scaling/` | 2026-09-15 | 8 learned + 3 known / 15 |
