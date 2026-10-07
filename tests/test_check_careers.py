"""Tests for career-fit's check_careers.py: a valid report passes, and each kind of gap is caught."""
import pytest

import check_careers as cc

GOOD = """# Career fit

> **As of 2026-10-06.** Based on profile.md, 4 papers and 1 case study in your library, and 0 learned topics.

## Ikigai

| Circle | What we found | Evidence |
|---|---|---|
| What you love | efficient model architectures, AI safety | [library: deepseek-v3-technical-report], [profile] |
| What you're good at | Python, PyTorch | [profile] |
| What the world needs | safer evaluation sandboxes | [S1] |
| What you can be paid for | research engineering | [S2] |

## Best fit

### 1. Research engineer (R1) at Example Lab (C1)
- **Love:** architectures [library: deepseek-v3-technical-report] · **Good at:** PyTorch [profile]
- **World needs:** [S1] · **Paid for:** an open posting [S2]
- **Weakest circle:** good at: no learned topics yet
- **Next step:** add "Mixtral of Experts" (arXiv 2401.04088) to the library

## Companies you'd love to work at

### C1: Example Lab
- **What they work on that matches you:** efficient training [S1]
- **Why you:** [library: deepseek-v3-technical-report] [profile]
- **Openings:** Research Engineer, remote, read on 2026-10-06 [S2]
- **Fit notes:** remote OK

### C2: Other Org
- **What they work on that matches you:** evaluations [S1]
- **Why you:** [profile]
- **Openings:** no current posting found (checked 2026-10-06)

## Roles you'd love

### R1: Research engineer
- **What it involves:** training and evaluating models [S2]
- **Gaps:** distributed training

## Dropped

| Candidate | Why it was dropped |
|---|---|
| Far Away Inc | on-site only, outside your locations |

## Sources

| ID | Title | Publisher | Date read | URL |
|---|---|---|---|---|
| S1 | Research | Example Lab | 2026-10-06 | https://example.org/research |
| S2 | Careers | Example Lab | 2026-10-06 | https://example.org/careers |
"""


@pytest.fixture(autouse=True)
def clear():
    cc.RESULTS.clear()
    yield
    cc.RESULTS.clear()


def failures(text):
    cc.check(text)
    return {check: detail for status, check, detail in cc.RESULTS if status == "FAIL"}


def test_a_complete_report_passes():
    assert failures(GOOD) == {}


@pytest.mark.parametrize("old, new, check, words", [
    ("**As of 2026-10-06.**", "**Recently.**", "dated", "As of"),
    ("- **What they work on that matches you:** evaluations [S1]", "- **What they work on that matches you:** evaluations",
     "companies and roles are sourced", "C2 Other Org cites no source"),
    ("Research Engineer, remote, read on 2026-10-06 [S2]", "Research Engineer, remote",
     "companies and roles are sourced", "without a cited posting"),
    ("at Example Lab (C1)", "at Example Lab (C9)", "best-fit picks", "no listed company"),
    ("- **Next step:** add", "- **Later:** add", "best-fit picks", "no next step"),
    ("| What you're good at | Python, PyTorch | [profile] |", "| What you're good at | Python, PyTorch | |",
     "ikigai circles cite evidence", "no evidence"),
    ("efficient training [S1]", "efficient training [S7]", "sources listed with URL and date", "S7"),
    ("| 2026-10-06 | https://example.org/careers |", "| 2026-10-06 | (see site) |", "sources listed with URL and date",
     "S2 has no URL"),
])
def test_each_gap_is_caught(old, new, check, words):
    assert old in GOOD
    found = failures(GOOD.replace(old, new, 1))
    assert check in found and words in found[check], found


def test_a_pick_that_cites_nothing_about_the_person_fails():
    text = GOOD.replace("[library: deepseek-v3-technical-report] · **Good at:** PyTorch [profile]", "· **Good at:** PyTorch", 1)
    assert "cites nothing about you" in failures(text)["best-fit picks"]
