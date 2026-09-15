"""Regenerate every value, table and figure. Run before each compile."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for script in ["make_values.py", "results_table.py", "loss_curves.py", "ablation_grid.py", "lr_schedule_concept.py"]:
    subprocess.run([sys.executable, "-W", "ignore", str(HERE / script)], check=True, cwd=HERE)
