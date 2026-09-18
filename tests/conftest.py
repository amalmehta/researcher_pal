"""Make the skills' scripts importable: they live outside any package."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for scripts in (ROOT / ".claude/skills/paper-writer/scripts", ROOT / ".claude/skills/paper-ideas/scripts"):
    sys.path.insert(0, str(scripts))
