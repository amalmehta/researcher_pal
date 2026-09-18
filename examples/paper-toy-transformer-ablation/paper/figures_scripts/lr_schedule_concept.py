"""Concept illustration: the learning-rate schedule with and without warmup.

Writes an editable SVG (figures/src/lr_schedule_concept.svg) with curves computed from Eq. 3, then converts it
to PDF with rsvg-convert. Sized to 0.48 of the venue text width, so it's included without scaling.
"""
import math
import subprocess

import data
import figure_style as fs
from data import VENUE

env = data.environment()
rows = data.runs()
d_model, steps = env["d_model"], env["steps"]
warmup = rows["baseline"][0]["warmup_steps"]
no_warmup = rows["no_warmup"][0]["warmup_steps"]

W = 0.48 * fs.VENUES[VENUE]["textwidth_pt"]
H = W * 0.62
LEFT, RIGHT, TOP, BOTTOM = 30.0, 6.0, 6.0, 22.0
LOG_MIN, LOG_MAX = -5.0, 0.0


def x(step):
    return LEFT + (step / steps) * (W - LEFT - RIGHT)


def y(lr):
    return TOP + (LOG_MAX - math.log10(lr)) / (LOG_MAX - LOG_MIN) * (H - TOP - BOTTOM)


def path(w):
    points = [(s, data.learning_rate(s, d_model, w)) for s in list(range(1, 50)) + list(range(50, steps + 1, 10))]
    return " ".join("%s%.2f,%.2f" % ("M" if i == 0 else "L", x(s), y(lr)) for i, (s, lr) in enumerate(points))


FONT = 'font-family="Times New Roman, Times, serif"'
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="%.2fpt" height="%.2fpt" viewBox="0 0 %.2f %.2f">' % (W, H, W, H),
    '<g %s font-size="7" fill="#222222">' % FONT,
    '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#444444" stroke-width="0.6"/>' % (LEFT, H - BOTTOM, W - RIGHT, H - BOTTOM),
    '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#444444" stroke-width="0.6"/>' % (LEFT, TOP, LEFT, H - BOTTOM),
]
for exp in range(int(LOG_MIN), int(LOG_MAX)):
    ty = y(10 ** exp)
    parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#444444" stroke-width="0.6"/>' % (LEFT - 2, ty, LEFT, ty))
    parts.append('<text x="%.2f" y="%.2f" text-anchor="end">10<tspan dy="-2.5" font-size="5">%d</tspan></text>' % (LEFT - 3, ty + 2.5, exp))
for s in (0, steps // 2, steps):
    anchor = "start" if s == 0 else "end" if s == steps else "middle"
    parts.append('<text x="%.2f" y="%.2f" text-anchor="%s">%s</text>' % (x(s), H - BOTTOM + 8, anchor, "{:,}".format(s)))
parts.append('<text x="%.2f" y="%.2f" text-anchor="middle">training step</text>' % ((LEFT + W - RIGHT) / 2, H - 3))
parts.append('<text transform="translate(7,%.2f) rotate(-90)" text-anchor="middle">learning rate</text>' % ((TOP + H - BOTTOM) / 2))
for w, color, label, label_step in [(warmup, fs.PALETTE[0], "warmup (w = %d)" % warmup, steps * 0.45),
                                    (no_warmup, fs.PALETTE[1], "no warmup (w = %d)" % no_warmup, steps * 0.45)]:
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2"/>' % (path(w), color))
    lr = data.learning_rate(int(label_step), d_model, w)
    offset = -4 if w == no_warmup else 9
    parts.append('<text x="%.2f" y="%.2f" fill="%s">%s</text>' % (x(label_step), y(lr) + offset, color, label))
parts += ["</g>", "</svg>", ""]

src = data.VENUE_DIR / "figures" / "src" / "lr_schedule_concept.svg"
src.parent.mkdir(parents=True, exist_ok=True)
src.write_text("\n".join(parts))
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(data.VENUE_DIR / "figures" / "lr_schedule_concept.pdf"), str(src)], check=True)
print("wrote lr_schedule_concept.pdf")
