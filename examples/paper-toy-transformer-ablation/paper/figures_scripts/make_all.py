"""Regenerate every value, table and figure of one venue folder, from the data.

    python3 make_all.py ../neurips2026

These scripts are shared by every venue of this paper: the venue folder is passed in, and the venue style
(neurips, iclr, ...) is its folder name without the year, or $VENUE.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["make_values.py", "results_table.py", "loss_curves.py", "ablation_grid.py", "lr_schedule_concept.py"]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    venue_dir = Path(sys.argv[1]).resolve()
    if not (venue_dir / "main.tex").exists():
        sys.exit("%s is not a venue folder (no main.tex)" % venue_dir)
    # SOURCE_DATE_EPOCH makes matplotlib and Cairo (Graphviz, rsvg-convert) stamp a fixed date, so a
    # rebuild from unchanged data is byte-identical and check_paper.py --regenerate can compare it.
    env = dict(os.environ, VENUE_DIR=str(venue_dir), MPLBACKEND="Agg",
               SOURCE_DATE_EPOCH=os.environ.get("SOURCE_DATE_EPOCH", "0"),
               VENUE=os.environ.get("VENUE") or re.sub(r"\d+$", "", venue_dir.name))
    for script in SCRIPTS:
        subprocess.run([sys.executable, "-W", "ignore", str(HERE / script)], cwd=str(HERE), env=env, check=True)


if __name__ == "__main__":
    main()
