"""Figure: training loss per configuration, mean over seeds with a min-max band."""
import numpy as np

import data
import figure_style as fs
from data import VENUE

curves = data.curves()
STYLE = {  # (palette index, line style, marker): the two warmup runs overlap, so they differ in dash and marker
    "baseline": (0, "-", "o"),
    "no_scaling": (2, "--", "s"),
    "no_warmup": (1, "-", "^"),
    "no_warmup_no_scaling": (3, ":", "D"),
    "no_ramp_capped": (4, "-.", "v"),
}

fig, ax = fs.figure(VENUE, width="text", aspect=0.32)
for config, label in data.CONFIGS:
    seeds = curves[config]
    steps = [step for step, _ in seeds[min(seeds)]]
    losses = np.array([[loss for _, loss in seeds[s]] for s in sorted(seeds)])
    color, linestyle, marker = STYLE[config]
    ax.plot(steps, losses.mean(axis=0), color=fs.PALETTE[color], linestyle=linestyle, marker=marker,
            markevery=(color * 2, 8), label=label)
    ax.fill_between(steps, losses.min(axis=0), losses.max(axis=0), color=fs.PALETTE[color], alpha=0.2, linewidth=0)
ax.set_xlabel("training step")
ax.set_ylabel("training loss")
ax.set_xlim(0, max(steps))
ax.legend(ncol=len(data.CONFIGS), loc="lower center", bbox_to_anchor=(0.5, 1.0), columnspacing=1.2, handlelength=2.2)
fs.save(fig, data.VENUE_DIR / "figures" / "loss_curves.pdf")
print("wrote loss_curves.pdf")
