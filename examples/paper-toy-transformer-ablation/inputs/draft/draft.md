# draft (very rough)

## abstract attempt
Transformers are trained with a learning-rate warmup and with attention scores scaled by 1/sqrt(d_k), and both tricks
are usually treated as essential. We test which of the two a small encoder-decoder Transformer actually needs. On a
sequence reversal task, removing warmup makes training fail in every run, while removing the scaling has no measurable
effect. The baseline reaches 100% accuracy on every seed.

## intro attempt
The original Transformer paper introduces several details that each get a single sentence but end up copied into
almost every implementation. Two of them are about keeping training stable: a learning-rate schedule that ramps up
linearly before decaying, and a 1/sqrt(d_k) factor on attention logits. It's often unclear which of these a given
model needs. We run a small, fully controlled ablation to find out.
