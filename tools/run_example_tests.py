"""Run an example's exercise tests against the reference solutions.

    python3 tools/run_example_tests.py examples/barabasi-albert-scaling [--stubs]

The exercises ship as stubs, so pytest is expected to FAIL on them and PASS once the reference
solutions from .solutions/ are swapped in. This copies the exercises to a temporary folder, overlays
the solutions (or not, with --stubs) and runs pytest there, leaving the originals untouched.

Exit code 0 if the run matched expectations (solutions pass / stubs fail), 1 otherwise.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("example", type=Path, help="folder with exercises/ and .solutions/")
    parser.add_argument("--stubs", action="store_true", help="run the untouched stubs, which must fail")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    exercises = args.example / "exercises"
    solutions = args.example / ".solutions"
    if not exercises.is_dir():
        sys.exit("no exercises in %s" % args.example)

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "exercises"
        shutil.copytree(exercises, work)
        swapped = []
        if not args.stubs:
            for impl in sorted(solutions.glob("*/impl.py")):
                target = work / impl.parent.name / "impl.py"
                if target.exists():
                    shutil.copy(impl, target)
                    swapped.append(impl.parent.name)
        done = subprocess.run([args.python, "-m", "pytest", "-p", "no:hydra_pytest", "-q"], cwd=str(work))

    what = "stubs" if args.stubs else "solutions for %s" % ", ".join(swapped)
    passed = done.returncode == 0
    expected = not args.stubs
    print("\n%s: pytest %s (%s)" % (args.example.name, "passed" if passed else "failed", what))
    if passed != expected:
        print("UNEXPECTED: %s were supposed to %s" % (what, "pass" if expected else "fail"))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
