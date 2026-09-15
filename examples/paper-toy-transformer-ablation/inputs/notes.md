# notes for the workshop paper (rough)

working title: Warmup, not attention scaling, is what a small Transformer can't do without

target: 4-page workshop-style paper. want to see it in NeurIPS format and in ICLR format.

## story
- Vaswani et al. have two one-sentence "stabilizers": the warmup schedule (Eq. 3) and dividing attention scores by
  sqrt(d_k) (Eq. 1). everyone copies both. which one actually matters for a small model?
- task: reverse length-8 digit sequences. tiny encoder-decoder (2 layers, d_model 64, 4 heads, d_ff 128), post-LN,
  Adam + Eq. 3 schedule, label smoothing 0.1.
- 2x2 ablation: warmup {200 steps, none} x scaling {on, off}. 1500 steps each. we ran 5 seeds per config.

## claims I want to make
1. without warmup, training fails every time (accuracy 0).
2. removing sqrt(d_k) scaling changes nothing here — same accuracy, same loss.
3. the baseline learns the task perfectly and one cross-attention head finds the exact reversal alignment.
4. scaling matters more as d_k grows, so big models still need it.

## figures I'm imagining
- loss curves for the 4 configs (mean + band over seeds)
- table: accuracy / alignment / final loss per config
- small method diagram of the 2x2 grid
- concept picture: what the lr schedule looks like with and without warmup

## related work
Vaswani 2017; Xiong et al. 2020 (pre-LN trains without warmup); Liu et al. 2020 (RAdam, warmup vs Adam variance);
Popel & Bojar 2018 (training tips); Kingma & Ba (Adam); Szegedy et al. 2016 (label smoothing).
also Zhang & Kumar 2021 "warmup is all you need" — in the bib.

## misc
- code: ../code/run_ablation.py (uses my transformer implementation in ../code/transformer)
- compute: my laptop, CPU only
- no human subjects, no new datasets, everything synthetic
