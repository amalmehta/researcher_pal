# 12 · Final: a small Transformer learns to reverse sequences

**Goal:** put every piece together (your model from 09, schedule from 10, loss from 11), train it on a CPU, and
reproduce one qualitative result from the paper at toy scale.

**Read first:** [results](../../concept_graph.md#results-results-and-attention-visualizations),
[encoder_decoder](../../concept_graph.md#encoder_decoder-encoder-decoder-and-autoregressive-generation) · §3 (intro), Figures 3–5
**Builds on:** exercises 08, 09, 10, 11

## The result we reproduce

Figures 3–5 show attention heads that learn meaningful structure without being told to, for example a head following
"making … more difficult". A toy task shows the same effect cleanly. Trained only on pairs
`sequence → reversed sequence`, with no recurrence and no alignment supervision, the model:

1. learns the task, reversing unseen sequences exactly; and
2. develops an **encoder-decoder attention head that looks at exactly the source token it's about to copy**, an
   anti-diagonal alignment.

**Not reproduced:** translation, BLEU, anything at the paper's scale, beam search, checkpoint averaging.

## What's provided and what you implement

Provided in `impl.py` (toy task, not from the paper): `make_batch`, `reversal_alignment`, and the constants
`PAD, BOS, FIRST_DIGIT, VOCAB_SIZE, SEQ_LEN`.

You implement:
1. `greedy_decode(model, src, max_len=SEQ_LEN)`: generate one token at a time, starting from `BOS`, each step
   feeding everything generated so far back into the decoder with a causal mask, and taking the most likely next
   token. Return `(batch, max_len)` without the `BOS`.
2. `train_and_evaluate(seed=0, steps=1500, batch_size=64)`: build the model and training loop with the settings in the
   docstring, then evaluate on 500 fresh sequences. Return `{"accuracy", "alignment", "seconds"}`.

Toy settings (**not in paper**): `d_model=64, h=4, d_ff=128, N=2, dropout=0.0`, `warmup_steps=200`, 1500 steps of 64
sequences of length 8.

## Run the tests

```bash
python3.9 -m pytest exercises/12_final_reversal
```

The reference solution takes about 40–60 seconds on a laptop CPU (Intel Mac, PyTorch 2.2). The time limit is 5 minutes.

## Things to think about

- In training, the decoder sees `BOS, y_1, …, y_7` all at once. At generation it sees only what it produced. Why do both
  give the same predictions for a well-trained model, and what makes that true?
- Which decoder layer and head would you expect to show the anti-diagonal? Look at `reversal_alignment`, then check.
- Try `warmup_steps=1`. What happens to training?
