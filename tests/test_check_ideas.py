"""Tests for paper-ideas' check_ideas.py, run as the CLI does, plus the two reports in examples/."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/paper-ideas/scripts/check_ideas.py"

CARD = """
### I-0{n} · {title}
- **Type:** {type} · **Impact:** Medium · **Effort:** 1 h · **Compute:** none
- **Motivated by:** `sections/results.tex`: the claim in question
- **Idea:** {title}
- **Literature:** {label}
- **Status:** proposed
"""

REPORT = """# Improvement ideas: Example paper (arXiv:2101.00001)

## Ranked ideas
| # | Idea | Type | Impact | Effort | Compute | Literature | Status |
|---|---|---|---|---|---|---|---|
| I-01 | Name the metric | writing | Medium | 1 h | none | n/a | proposed |
| I-02 | Add a control | evidence | Medium | 1 h | none | related work | proposed |
| I-03 | Pre-empt a reviewer | reviewer | Medium | 1 h | none | related work | proposed |
| I-04 | A follow-up study | direction | Medium | 1 h | none | related work | proposed |

## Details
{cards}
## Log
- nothing yet
"""


def build(tmp_path, labels=None, extra_card="", cited="10.1137/070710111"):
    labels = labels or ["not applicable (presentation)", "related work: [doi:%s](https://doi.org/%s)" % (cited, cited),
                        "related work", "related work"]
    cards = "".join(CARD.format(n=i + 1, title=t, type=k, label=labels[i]) for i, (t, k) in enumerate(
        [("Name the metric", "writing"), ("Add a control", "evidence"),
         ("Pre-empt a reviewer", "reviewer"), ("A follow-up study", "direction")]))
    ideas = tmp_path / "ideas"
    (ideas / "literature").mkdir(parents=True)
    (ideas / "literature" / "group.json").write_text(json.dumps(
        {"queries": ["example query"], "services": {}, "records": [
            {"title": "Power-Law Distributions in Empirical Data", "ids": {"doi": "10.1137/070710111"},
             "authors": ["Aaron Clauset"], "year": 2009, "found_in": ["crossref"]}]}))
    (ideas / "ideas.md").write_text(REPORT.format(cards=cards + extra_card))
    return ideas / "ideas.md"


def run(path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def test_a_complete_report_passes(tmp_path):
    result = run(build(tmp_path))
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


def test_missing_field_fails(tmp_path):
    path = build(tmp_path)
    path.write_text(path.read_text().replace("- **Motivated by:** `sections/results.tex`: the claim in question\n", "", 1))
    result = run(path)
    assert result.returncode == 1 and "Motivated by" in result.stdout


def test_invented_citation_fails(tmp_path):
    path = build(tmp_path, cited="10.9999/not-a-real-record")
    result = run(path)
    assert result.returncode == 1 and "not verified records" in result.stdout


def test_unknown_literature_label_fails(tmp_path):
    path = build(tmp_path, labels=["probably novel", "related work", "related work", "related work"])
    result = run(path)
    assert result.returncode == 1 and "literature label" in result.stdout


def test_missing_idea_type_fails(tmp_path):
    path = build(tmp_path)
    path.write_text(path.read_text().replace("**Type:** direction", "**Type:** writing"))
    result = run(path)
    assert result.returncode == 1 and "types not covered" in result.stdout


def test_card_without_a_table_row_fails(tmp_path):
    path = build(tmp_path, extra_card=CARD.format(n=5, title="Stray card", type="writing", label="related work"))
    result = run(path)
    assert result.returncode == 1 and "cards differ" in result.stdout


def test_broken_local_link_fails(tmp_path):
    path = build(tmp_path)
    path.write_text(path.read_text().replace("- **Idea:** Add a control",
                                             "- **Idea:** see [the plan](experiments/01/plan.md)"))
    result = run(path)
    assert result.returncode == 1 and "broken link" in result.stdout


@pytest.mark.parametrize("report", [
    "examples/paper-toy-transformer-ablation/paper/ideas/ideas.md",
    "examples/barabasi-albert-scaling/ideas/ideas.md",
])
def test_the_example_reports_pass(report):
    result = run(ROOT / report)
    assert result.returncode == 0, result.stdout
