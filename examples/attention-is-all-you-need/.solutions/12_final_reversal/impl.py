"""12 · Final: a small Transformer learns to reverse sequences. See README.md."""
import time

import torch

from _load import load

# Your work from earlier exercises.
Transformer = load("09_transformer").Transformer
subsequent_mask = load("08_decoder_layer").subsequent_mask
make_optimizer = load("10_lr_schedule").make_optimizer
LabelSmoothingLoss = load("11_label_smoothing").LabelSmoothingLoss

# ---- Provided: the toy task (not from the paper) --------------------------------------------
PAD, BOS = 0, 1   # special tokens
FIRST_DIGIT = 2   # tokens 2..11 are ten "digits"
VOCAB_SIZE = 12
SEQ_LEN = 8


def make_batch(batch_size, generator):
    """Random digit sequences and their reversals.

    Returns:
        src:    (batch, SEQ_LEN) source digits
        tgt_in: (batch, SEQ_LEN) decoder input: BOS, then the reversed sequence without its last token
        tgt:    (batch, SEQ_LEN) what the decoder should predict: the reversed sequence
    """
    src = torch.randint(FIRST_DIGIT, VOCAB_SIZE, (batch_size, SEQ_LEN), generator=generator)
    tgt = src.flip(1)
    tgt_in = torch.cat([torch.full((batch_size, 1), BOS, dtype=torch.long), tgt[:, :-1]], dim=1)
    return src, tgt_in, tgt


def reversal_alignment(model):
    """Best fraction, over decoder layers and heads, of target positions j whose strongest
    encoder-decoder attention lands on source position SEQ_LEN - 1 - j (the token being copied).

    Call right after a teacher-forced forward pass in eval mode, so last_weights is filled.
    """
    expected = torch.arange(SEQ_LEN - 1, -1, -1)
    best = 0.0
    for layer in model.decoder.layers:
        weights = layer.cross_attn.last_weights                       # (batch, h, n_tgt, n_src)
        hits = (weights.argmax(-1) == expected).float().mean(dim=(0, 2))  # one score per head
        best = max(best, hits.max().item())
    return best


# ---- Your part -------------------------------------------------------------------------------
@torch.no_grad()
def greedy_decode(model, src, max_len=SEQ_LEN):
    """Generate max_len tokens auto-regressively (§3), always taking the most likely next token.

    Args:
        model: a Transformer from exercise 09
        src: (batch, n_src) long

    Returns:
        (batch, max_len) long, without the leading BOS
    """
    was_training = model.training
    model.eval()
    memory = model.encode(src)  # the source is encoded once and reused at every step
    ys = torch.full((src.size(0), 1), BOS, dtype=torch.long)
    for _ in range(max_len):
        # Re-run the decoder on everything generated so far; the causal mask makes this match training.
        hidden = model.decode(memory, ys, tgt_mask=subsequent_mask(ys.size(1)))
        next_token = model.generator(hidden[:, -1]).argmax(-1, keepdim=True)  # only the newest position
        ys = torch.cat([ys, next_token], dim=1)
    model.train(was_training)
    return ys[:, 1:]


def train_and_evaluate(seed=0, steps=1500, batch_size=64):
    """Train a small Transformer on make_batch, then evaluate it.

    Use:
        torch.manual_seed(seed) for the model, and torch.Generator().manual_seed(seed) for make_batch
        Transformer(VOCAB_SIZE, d_model=64, h=4, d_ff=128, N=2, dropout=0.0, max_len=SEQ_LEN + 1)
        make_optimizer(model.parameters(), d_model=64, warmup_steps=200)     # exercise 10
        LabelSmoothingLoss(VOCAB_SIZE, smoothing=0.1, ignore_index=PAD)       # exercise 11

    Returns a dict:
        accuracy:  fraction of 500 fresh sequences that greedy_decode reverses exactly
        alignment: reversal_alignment(model) after a teacher-forced forward pass on those 500 sequences
        seconds:   wall-clock time for training and evaluation
    """
    start = time.time()
    torch.manual_seed(seed)
    data = torch.Generator().manual_seed(seed)
    model = Transformer(VOCAB_SIZE, d_model=64, h=4, d_ff=128, N=2, dropout=0.0, max_len=SEQ_LEN + 1)
    optimizer, scheduler = make_optimizer(model.parameters(), d_model=64, warmup_steps=200)
    loss_fn = LabelSmoothingLoss(VOCAB_SIZE, smoothing=0.1, ignore_index=PAD)
    tgt_mask = subsequent_mask(SEQ_LEN)

    model.train()
    for _ in range(steps):
        src, tgt_in, tgt = make_batch(batch_size, data)
        # Teacher forcing: the decoder gets the true previous tokens, shifted right by one (§3.1).
        loss = loss_fn(model(src, tgt_in, tgt_mask=tgt_mask), tgt)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()

    model.eval()
    src, tgt_in, tgt = make_batch(500, data)  # fresh sequences, never trained on (with overwhelming odds)
    with torch.no_grad():
        model(src, tgt_in, tgt_mask=tgt_mask)  # teacher-forced pass fills cross_attn.last_weights
        alignment = reversal_alignment(model)
        accuracy = (greedy_decode(model, src) == tgt).all(dim=1).float().mean().item()
    return {"accuracy": accuracy, "alignment": alignment, "seconds": time.time() - start}
