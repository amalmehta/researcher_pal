"""Tests for researcher-pal's check_learning.py.

The integration tests copy the Barabasi-Albert example, break one thing, and require the checker to report it,
so they prove the checker catches real problems rather than only passing good material.
"""
import shutil
import sys
from pathlib import Path

import pytest

import check_learning as cl

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "barabasi-albert-scaling"
HAS_JS = cl.js_engine() is not None


@pytest.fixture(autouse=True)
def clear_results():
    cl.RESULTS.clear()
    yield
    cl.RESULTS.clear()


def failed():
    return {check: detail for status, check, detail in cl.RESULTS if status == "FAIL"}


# ---------------------------------------------------------------- Mermaid rules
GOOD = """flowchart TD
  classDef core fill:#dbeafe
  classDef novel fill:#fef3c7
  subgraph S3["§3 Model (main)"]
    sdpa["Scaled dot-product attention 🎬"]:::novel
  end
  softmax["Softmax & friends"]:::core
  softmax --> sdpa
"""


def test_a_template_diagram_passes():
    problems, nodes, edges = cl.lint_mermaid(GOOD)
    assert problems == []
    assert nodes["sdpa"] == ("Scaled dot-product attention 🎬", "novel")
    assert ("softmax", "sdpa") in edges


@pytest.mark.parametrize("change, expected", [
    (('softmax["Softmax & friends"]', 'softmax[Softmax]'), "isn't in double quotes"),
    (('softmax["Softmax & friends"]', 'end["Softmax"]'), "reserved word"),
    (('"Softmax & friends"', '"a <b> c"'), "`<` or `>`"),
    (('"Softmax & friends"', '"$\\sqrt{d_k}$"'), "LaTeX"),
    ((":::core", ":::missing"), "has no classDef"),
    (("  end\n", ""), "never closed"),
    (("softmax --> sdpa", "softmax --> sdap"), "never defined"),
    (("softmax --> sdpa", "softmax --oops"), "circle/cross edge"),
    (('"Softmax & friends"', '"say "hi"'), "unbalanced"),
    (("flowchart TD", "graph LR"), "flowchart TD"),
])
def test_each_rule_is_enforced(change, expected):
    problems, _, _ = cl.lint_mermaid(GOOD.replace(*change))
    assert any(expected in p for p in problems), problems


def test_github_anchor():
    assert cl.github_anchor("sdpa: Scaled dot-product attention") == "sdpa-scaled-dot-product-attention"
    assert cl.github_anchor("ba_model: Growth + preferential attachment 🎬") == "ba_model-growth--preferential-attachment-"


# ---------------------------------------------------------------- a broken copy of a real example
@pytest.fixture
def paper(tmp_path):
    copy = tmp_path / "ba"
    shutil.copytree(EXAMPLE, copy, ignore=shutil.ignore_patterns("paper.pdf", "__pycache__", ".pytest_cache"))
    return copy


def run(paper, *extra):
    sys_argv = sys.argv
    sys.argv = ["check_learning.py", str(paper), "--python", sys.executable] + list(extra)
    try:
        with pytest.raises(SystemExit) as exit_info:
            cl.main()
    finally:
        sys.argv = sys_argv
    return exit_info.value.code


def edit(path, old, new):
    text = path.read_text()
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, 1))


def test_the_example_passes(paper):
    assert run(paper, "--no-run") == 0, failed()


def test_an_uncited_entry_fails(paper):
    edit(paper / "concept_graph.md", '- **Source:** ¶3 ("the probability $P(k)$ that a vertex in the network interacts '
                                     'with $k$ other vertices"), Figs. 1–2', "- **Source:** the introduction")
    assert run(paper, "--no-run") == 1
    assert "degree_distribution" in failed()["every entry cites the paper"]


def test_a_node_without_an_entry_fails(paper):
    edit(paper / "concept_graph.md", "  subgraph model[", '  orphan["An idea with no entry"]:::core\n  subgraph model[')
    assert run(paper, "--no-run") == 1
    assert "orphan" in failed()["map and entries match"]


def test_a_broken_anchor_fails(paper):
    edit(paper / "concept_graph.md", "(#", "(#no-such-heading-")
    assert run(paper, "--no-run") == 1
    assert "#no-such-heading-" in failed()["links and anchors resolve"]


def test_a_stub_that_is_the_solution_fails(paper):
    shutil.copy(paper / ".solutions" / "01_preferential_attachment" / "impl.py",
                paper / "exercises" / "01_preferential_attachment" / "impl.py")
    assert run(paper, "--no-run") == 1
    assert "01_preferential_attachment" in failed()["solutions stay hidden"]


def test_a_test_file_that_cannot_be_collected_fails(paper):
    # The stub "fails" either way; this must not count, because the tests never ran.
    edit(paper / "exercises" / "01_preferential_attachment" / "test_impl.py", "def ", "def broken syntax(:\ndef ")
    assert run(paper) == 1
    assert "never really ran" in failed()["stubs fail, solutions pass"]


def test_a_wrong_solution_fails(paper):
    solution = paper / ".solutions" / "01_preferential_attachment" / "impl.py"
    solution.write_text(solution.read_text() + "\n\ndef _sabotage():\n    pass\n" +
                        "".join("\n%s = None" % name for name in ("attachment_probabilities",)))
    assert run(paper) == 1
    assert "01_preferential_attachment" in failed()["stubs fail, solutions pass"]


@pytest.mark.skipif(not HAS_JS, reason="needs node or JavaScriptCore")
def test_an_animation_that_throws_fails(paper):
    page = paper / "animations" / "ba_model.html"
    edit(page, "function draw({ S, C, step, p, params, lerp, during, fmt }) {",
         "function draw({ S, C, step, p, params, lerp, during, fmt }) {\n  if (step === 2) undefinedHelper();")
    assert run(paper, "--no-run") == 0  # structure alone can't see it
    cl.RESULTS.clear()
    assert run(paper) == 1
    assert "draw() throws at step 3" in failed()["animation ba_model.html"]


@pytest.mark.skipif(not HAS_JS, reason="needs node or JavaScriptCore")
def test_a_slider_that_does_nothing_fails(paper):
    edit(paper / "animations" / "ba_model.html", "const PARAMS = [",
         'const PARAMS = [\n  { id: "unused", label: "Unused", min: 0, max: 9, step: 1, value: 3, paperValue: 3, help: "" },')
    assert run(paper) == 1
    assert "slider unused doesn't change the picture" in failed()["animation ba_model.html"]


@pytest.mark.skipif(not HAS_JS, reason="needs node or JavaScriptCore")
def test_nan_in_the_drawing_fails(paper):
    edit(paper / "animations" / "ba_model.html", "function draw({ S, C, step, p, params, lerp, during, fmt }) {",
         "function draw({ S, C, step, p, params, lerp, during, fmt }) {\n  S.circle(0 / 0, 10, 5);")
    assert run(paper) == 1
    assert "bad SVG attribute values" in failed()["animation ba_model.html"]
