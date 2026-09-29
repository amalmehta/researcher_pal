#!/usr/bin/env bash
# Every check this repo can run, in one place. CI runs exactly this script, so a green run here means
# a green run there.
#
#   tools/checks.sh          # everything the installed tools allow
#   tools/checks.sh --quick  # skip the paper compile and the PyTorch exercises
#
# PY overrides the interpreter (default python3.9 locally, python3 in CI).
set -uo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-$(command -v python3.9 >/dev/null 2>&1 && echo python3.9 || echo python3)}
QUICK=${1:-}
FAILED=()

step() {  # step <name> <command...>
  local name=$1; shift
  echo ""
  echo "=== $name"
  if "$@"; then echo "--- $name: OK"; else echo "--- $name: FAILED"; FAILED+=("$name"); fi
}

step "unit tests (skill scripts)" "$PY" -m pytest

step "ideas reports" "$PY" skills/paper-ideas/scripts/check_ideas.py \
  examples/paper-toy-transformer-ablation/paper/ideas/ideas.md \
  examples/barabasi-albert-scaling/ideas/ideas.md

step "static site builds" "$PY" site/build_site.py

step "Barabasi-Albert exercises (solutions pass)" "$PY" tools/run_example_tests.py examples/barabasi-albert-scaling
step "Barabasi-Albert exercises (stubs fail)" "$PY" tools/run_example_tests.py examples/barabasi-albert-scaling --stubs

if [ "$QUICK" != "--quick" ]; then
  if "$PY" -c "import torch" >/dev/null 2>&1; then
    step "Attention exercises (solutions pass)" "$PY" tools/run_example_tests.py examples/attention-is-all-you-need
  else
    echo ""; echo "=== Attention exercises: skipped (no PyTorch)"
  fi

  TECTONIC=$(command -v tectonic || echo "$HOME/.local/bin/tectonic")
  if [ -x "$TECTONIC" ]; then
    # Compile into a scratch folder: the PDFs, logs and compile.out in the paper folders are committed
    # results, and a check must not rewrite them.
    BUILD=$(mktemp -d)
    trap 'rm -rf "$BUILD"' EXIT
    for venue in neurips2026 iclr2027; do
      dir="examples/paper-toy-transformer-ablation/paper/$venue"
      mkdir -p "$BUILD/$venue"
      step "$venue compiles" bash -c "cd '$dir' && '$TECTONIC' -Z search-path=template main.tex --keep-logs \
        --keep-intermediates --outdir '$BUILD/$venue' > '$BUILD/$venue/compile.out' 2>&1 \
        || { tail -20 '$BUILD/$venue/compile.out'; false; }"
      step "$venue checks (figures and values match the data)" "$PY" skills/paper-writer/scripts/check_paper.py \
        "$dir" --build-dir "$BUILD/$venue" --page-limit 4 --anonymous --regenerate --python "$PY"
    done
  else
    echo ""; echo "=== paper compile: skipped (no tectonic)"
  fi
fi

echo ""
if [ ${#FAILED[@]} -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf 'FAILED: %s\n' "${FAILED[*]}"
exit 1
