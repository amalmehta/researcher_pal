"""Make the skills' scripts importable: they live outside any package."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for scripts in (ROOT / "skills/paper-writer/scripts", ROOT / "skills/paper-ideas/scripts",
                ROOT / "skills/researcher-pal/scripts"):
    sys.path.insert(0, str(scripts))
