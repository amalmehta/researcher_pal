# Exercise templates

## Contents
1. Choosing the form and stack
2. Shared harness (`exercises/pytest.ini`, `conftest.py`, `_load.py`)
3. Coded exercise: `README.md`
4. Coded exercise: `impl.py` stub and the matching `.solutions/…/impl.py`
5. Coded exercise: `test_impl.py`
6. Worked problem: `README.md`, `answer.md`, `.solutions/…/solution.md`
7. Final exercise
8. Verification

---

## 1. Choosing the form and stack

| The concept is… | Form |
|---|---|
| something you can compute, simulate, or check numerically | coded exercise |
| a derivation, proof, or argument with nothing meaningful to run | worked problem |
| a derived result that *can* be checked numerically | coded exercise that checks the claim (e.g. simulate and compare with the derived exponent) |

| The paper is about | Stack | Float comparison in tests | Seeding |
|---|---|---|---|
| ML / deep learning | PyTorch | `torch.testing.assert_close(a, b)` | `torch.manual_seed(0)` |
| numerical / scientific models | NumPy (+ SciPy) | `numpy.testing.assert_allclose(a, b, rtol=1e-6)` | `rng = numpy.random.default_rng(0)`, passed in |
| algorithms / CS theory | standard library | `math.isclose(a, b, rel_tol=1e-9)` | `random.Random(0)`, passed in |

Pass random generators into functions as arguments (`rng`) instead of using global state,
so tests are reproducible and a learner's extra random call can't shift every later
number.

---

## 2. Shared harness (coded exercises only)

Write these three files once per paper into `papers/<slug>/exercises/`. They let every
exercise use the same file names (`impl.py`, `test_impl.py`) without import clashes,
and let later exercises reuse earlier ones.

**`exercises/pytest.ini`**
```ini
[pytest]
addopts = -q --import-mode=importlib -p no:cacheprovider
```
If pytest crashes on startup because of an unrelated globally installed plugin, append
`-p no:<plugin-name>` to `addopts`. Blocking a plugin that isn't installed is harmless.

**`exercises/conftest.py`**
```python
import sys
from pathlib import Path

# Make _load importable from every exercise's tests.
sys.path.insert(0, str(Path(__file__).parent))
```

**`exercises/_load.py`**
```python
"""Load an exercise's impl.py by folder name, e.g. load("01_softmax").

Paths are resolved next to this file, so the same code works in exercises/ and in a
copy with the reference solutions swapped in.
"""
import importlib.util
from pathlib import Path

_HERE = Path(__file__).parent
_cache = {}


def load(folder):
    if folder not in _cache:
        path = _HERE / folder / "impl.py"
        spec = importlib.util.spec_from_file_location("ex_" + folder, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _cache[folder] = module
    return _cache[folder]
```

---

## 3. Coded exercise: `exercises/NN_<concept-id>/README.md`

```markdown
# NN · <Concept name>

**Goal:** <one sentence: what you'll build and why the paper needs it>

**Read first:** [concept entry](../../concept_graph.md#<anchor>) · <§x.y, Eq. (n)>
**Watch:** [animation](../../animations/<concept-id>.html)  ← if one exists
**Builds on:** <earlier exercises, if any>

## What to implement

`impl.py` → `<function_name>(<args>)`: <plain-language description of inputs and outputs>

$$
<the equation(s) this exercise covers>
$$

| Argument | Shape / type / units | Meaning |
|---|---|---|

## Run the tests

​```bash
<python> -m pytest exercises/NN_<concept-id>
​```

## Things to think about

- <A question pointing at the nuance>
- <A question about an assumption, edge case, or numerical issue>
```

Don't include code or pseudo-code that gives the answer away. Point at equations and
properties instead.

---

## 4. `impl.py` stub and reference solution

**`exercises/NN_<concept-id>/impl.py`** (what the learner edits):
```python
"""NN · <Concept name>. See README.md and <§x.y, Eq. (n)> of the paper."""
<imports for the chosen stack>

from _load import load  # only if this exercise builds on earlier ones

# Earlier work this exercise builds on (your own code from those exercises):
# earlier = load("MM_<earlier-concept-id>")


def <function_name>(<args>):
    """<One-line summary>.

    Args:
        <arg>: <meaning>, <shape / type / units>

    Returns:
        <meaning>, <shape / type / units>
    """
    raise NotImplementedError("TODO: implement <Eq. (n)>")
```

**`.solutions/NN_<concept-id>/impl.py`**: same module docstring, imports and
signatures, with the body filled in. Keep it idiomatic and commented at the level a
learner reading it after solving would appreciate. It is also shown in step 7 if the
learner asks.

For class-based exercises (e.g. `nn.Module`), the stub keeps `__init__` signatures and lists
the attributes to create in the docstring (tests use those names), with the method bodies
raising `NotImplementedError`. Anything the exercise *provides* rather than asks for (data
generators, plotting helpers, constants for a toy task) goes above a
`# ---- Your part ----` line and is identical in stub and solution.

---

## 5. `exercises/NN_<concept-id>/test_impl.py`

```python
"""Tests for NN · <Concept name>. Run: <python> -m pytest exercises/NN_<concept-id>"""
import pytest
<stack imports>

from _load import load

impl = load("NN_<concept-id>")


def test_output_shape_or_type():
    out = impl.<function_name>(<small inputs>)
    assert <shape / type check>, "expected <...>; check <which step>"


def test_hand_computed_case():
    # Tiny input worked out by hand in the README's notation.
    <compare with the float comparison for the stack>


def test_property_from_paper():
    # e.g. probabilities sum to 1, a conserved quantity, a symmetry, a known limit.
    ...


def test_matches_trusted_routine():
    # Only if a trusted routine exists in the allowed stack; skip cleanly if the version lacks it.
    ...
```

Guidelines:
- 3–6 tests per exercise. Each checks a distinct thing the paper implies.
- Use small sizes so hand checks are possible and runs are fast.
- Assertion messages should teach: say what should hold and what to check.
- Don't test private helper names or intermediate values the paper doesn't define.
- For stochastic claims (a fitted exponent, a mean over runs), use a fixed seed, enough
  samples that the answer is stable, and a tolerance that a correct solution clears easily.
  Run the reference solution with a few other seeds too, to confirm the threshold isn't luck.

---

## 6. Worked problem

**`exercises/NN_<concept-id>/README.md`**
```markdown
# NN · <Concept name> (worked problem)

**Goal:** <what you'll derive or prove, and why the paper needs it>

**Read first:** [concept entry](../../concept_graph.md#<anchor>) · <§x.y, Eq. (n)>
**Watch:** [animation](../../animations/<concept-id>.html)  ← if one exists

## Problem

<Precise statement. Give the starting point (definitions, assumptions, earlier results) and
the target (the equation or claim to reach), citing the paper.>

## A complete answer shows

- <A step the answer must justify, e.g. "why the continuum approximation is valid for large t">
- <Which assumption each key step uses>
- <The result, in the paper's notation>

## Write your answer

In `answer.md`, in Markdown with `$…$` math. Plain steps are fine. Say which assumption each step uses.

## Things to think about

- <A guiding question pointing at the crux>
```

**`exercises/NN_<concept-id>/answer.md`**
```markdown
# Answer: NN · <Concept name>

<!-- Write your derivation here. -->
```

**`.solutions/NN_<concept-id>/solution.md`**: the full derivation, one justified step
at a time, ending at the paper's result (cite it). Include a short "Common wrong turns"
list (the steps learners usually fumble); it guides the hint ladder.

Accept the learner's answer when every "A complete answer shows" point is covered and each
step is justified. A different valid route is fine.

---

## 7. Final exercise (`NN_final_<name>/`)

**Coded papers:** same files as a coded exercise, plus:
- `impl.py` exposes a top-level function such as `train_and_evaluate(seed=0)` or
  `simulate_and_measure(seed=0)` that returns a metrics dict; its body raises
  `NotImplementedError`. The README describes the toy setup, sizes and budget, and what is
  *not* reproduced.
- `test_impl.py` computes the metrics once in a `scope="module"` fixture, then checks the
  qualitative claim with thresholds (e.g. `accuracy > 0.9`, or a fitted exponent within
  a stated tolerance of the paper's) and the runtime.
- Time the reference solution and keep it under 5 minutes on CPU. Say in the README how long it takes.

**Theory papers:** a capstone worked problem (section 6) whose target is the paper's main
theorem or central argument, broken into parts that reuse the earlier problems.

---

## 8. Verification

Run from `papers/<slug>/` with the chosen interpreter. Both checks must be clean before
the learner sees any coded exercise.

```bash
PY=python3   # the interpreter picked in the ground rules
# 1) Every untouched stub must fail.
for d in exercises/[0-9]*/; do
  [ -f "$d/test_impl.py" ] || continue   # worked problems have no tests
  if $PY -m pytest "$d" >/dev/null 2>&1; then echo "BAD  stub passes: $d"; else echo "ok   stub fails:  $d"; fi
done
# 2) Every reference solution must pass: copy the exercises and overlay the solutions.
TMP="$(mktemp -d)"; cp -R exercises/. "$TMP/"
for f in .solutions/*/impl.py; do cp "$f" "$TMP/$(basename "$(dirname "$f")")/impl.py"; done
$PY -m pytest "$TMP"; echo "solutions exit code: $?"
```

A stub "failing" because pytest itself crashed doesn't count. Check that the output
shows real test failures (`N failed`), not a startup error.

For worked problems, re-read `solution.md` against the paper: the final result must
match the cited equation, and every point in "A complete answer shows" must be covered.
