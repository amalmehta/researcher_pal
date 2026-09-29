"""Unit tests for paper-writer's check_paper.py (offline parts only; citation lookups need the network)."""
import os

import check_paper as cp
import pytest


@pytest.fixture(autouse=True)
def clear_results():
    cp.RESULTS.clear()
    yield
    cp.RESULTS.clear()


def statuses():
    return {check: (status, detail) for status, check, detail in cp.RESULTS}


# ---------------------------------------------------------------- .bib parsing
def test_parse_bib_keeps_nested_braces_and_authors():
    entries = cp.parse_bib("""
@inproceedings{vaswani2017attention,
  title     = {Attention is {All} you Need},
  author    = {Vaswani, Ashish and Shazeer, Noam},
  booktitle = {NeurIPS},
  year      = {2017},
}
@article{clauset2009, title = "Power-Law Distributions in Empirical Data", doi = {10.1137/070710111}}
""")
    assert [key for _, key, _ in entries] == ["vaswani2017attention", "clauset2009"]
    kind, _, fields = entries[0]
    assert kind == "inproceedings"
    assert fields["title"] == "Attention is {All} you Need"
    assert fields["year"] == "2017"
    assert cp.first_author_surname(fields) == "vaswani"
    assert entries[1][2]["doi"] == "10.1137/070710111"


def test_first_author_surname_without_comma():
    assert cp.first_author_surname({"author": "Albert-László Barabási and Réka Albert"}) == "barabasi"


def test_ascii_fold_and_title_matching():
    assert cp.ascii_fold("Erdős") == "Erdos"
    assert cp.norm_title("Attention Is All You Need!") == "attention is all you need"
    assert cp.title_ratio("Attention is all you need", "Attention Is All You Need") > 0.95
    assert cp.title_ratio("Attention is all you need", "Deep residual learning for image recognition") < 0.6


def test_arxiv_id_from_url_and_eprint():
    assert cp.arxiv_id({"eprint": "1706.03762v5"}) == "1706.03762"
    assert cp.arxiv_id({"url": "https://arxiv.org/abs/cond-mat/9910332v1"}) == "cond-mat/9910332"
    assert cp.arxiv_id({"title": "no identifier"}) == ""


# ---------------------------------------------------------------- numbers in prose
def write_paper(tmp_path, prose, sources="", values="\\newcommand{\\valSteps}{1500}\n"):
    (tmp_path / "sections").mkdir(exist_ok=True)
    (tmp_path / "generated").mkdir(exist_ok=True)
    (tmp_path / "main.tex").write_text("\\documentclass{article}\n\\input{generated/values}\n"
                                       "\\begin{document}\\input{sections/body}\\end{document}\n")
    (tmp_path / "sections" / "body.tex").write_text(prose)
    (tmp_path / "generated" / "values.tex").write_text(values)
    (tmp_path / "sources.md").write_text(sources)
    return tmp_path


def test_prose_only_drops_markup_but_keeps_real_numbers():
    tex = ("We train for \\valSteps{} steps and reach 99.8\\% accuracy \\citep{kingma2015adam}.\n"
           "\\includegraphics[width=0.48\\linewidth]{figures/loss.pdf}\n"
           "See Figure~\\ref{fig:loss}; 1,500 steps, published in 2017.")
    numbers = {m.group(1) for m in cp.NUMBER.finditer(cp.prose_only(tex))}
    assert {"99.8", "1,500", "2017"} <= numbers
    assert "0.48" not in numbers


def test_check_numbers_flags_a_number_missing_from_sources(tmp_path):
    paper = write_paper(tmp_path, "Accuracy was 99.8\\% and the final loss 0.53.\n", sources="| 99.8 | accuracy |\n")
    cp.check_numbers(paper, "main.tex")
    status, detail = statuses()["numbers in prose are sourced"]
    assert status == "FAIL" and "0.53" in detail


def test_check_numbers_passes_when_everything_is_listed(tmp_path):
    paper = write_paper(tmp_path, "We ran \\valSteps{} steps in 2017 and reached 99.8\\%.\n",
                        sources="| 99.8 | accuracy |\n| valSteps | training steps |\n")
    cp.check_numbers(paper, "main.tex")
    assert statuses()["numbers in prose are sourced"][0] == "PASS"
    assert statuses()["value macros"][0] == "PASS"


def test_check_numbers_flags_an_undefined_macro(tmp_path):
    paper = write_paper(tmp_path, "We ran \\valMissing{} steps.\n", sources="valMissing\n")
    cp.check_numbers(paper, "main.tex")
    status, detail = statuses()["value macros"]
    assert status == "FAIL" and "valMissing" in detail


# ---------------------------------------------------------------- page limit and anonymity
def test_check_pages_uses_the_main_end_label(tmp_path):
    (tmp_path / "main.aux").write_text("\\newlabel{pw:mainend}{{6}{4}{}{}{}}\n")
    cp.check_pages(tmp_path, "main.tex", 4)
    assert cp.RESULTS[-1][0] == "PASS"
    cp.RESULTS.clear()
    cp.check_pages(tmp_path, "main.tex", 3)
    assert cp.RESULTS[-1][0] == "FAIL"


def test_check_pages_fails_without_the_label(tmp_path):
    (tmp_path / "main.aux").write_text("\\newlabel{fig:loss}{{1}{2}{}{}{}}\n")
    cp.check_pages(tmp_path, "main.tex", 4)
    assert cp.RESULTS[-1][0] == "FAIL"


def test_check_anonymity_finds_identifying_text(tmp_path):
    paper = write_paper(tmp_path, "Contact jane@example.edu about our previous work.\n")
    cp.check_anonymity(paper, "main.tex", ["Jane Doe"])
    status, detail = statuses()["anonymity"]
    assert status == "FAIL" and "email" in detail


def test_check_anonymity_passes_on_clean_text(tmp_path):
    paper = write_paper(tmp_path, "We ablate warmup and attention scaling.\n")
    cp.check_anonymity(paper, "main.tex", ["Jane Doe"])
    assert statuses()["anonymity"][0] == "PASS"


def test_strip_comments_keeps_escaped_percent():
    assert cp.strip_comments("accuracy 99.8\\% % a comment\n").strip() == "accuracy 99.8\\%"


# ---------------------------------------------------------------- regenerate check
def regen_paper(tmp_path, script):
    """A venue folder with committed outputs and a make_all.py that does whatever `script` says."""
    paper = tmp_path / "venue"
    (paper / "generated" / "tables").mkdir(parents=True)
    (paper / "figures" / "src").mkdir(parents=True)
    (paper / "main.tex").write_text("\\documentclass{article}")
    (paper / "generated" / "values.tex").write_text("\\newcommand{\\valSteps}{1500}\n")
    (paper / "generated" / "tables" / "results.tex").write_text("0.42\n")
    (paper / "figures" / "loss.pdf").write_bytes(b"%PDF-1.4 figure\n")
    (paper / "figures" / "src" / "loss.svg").write_text("<svg/>")
    scripts = paper / "figures" / "scripts"
    scripts.mkdir()
    (scripts / "make_all.py").write_text("import sys\nfrom pathlib import Path\nv = Path(sys.argv[1])\n" + script)
    return paper


def tree(paper):
    return {str(f.relative_to(paper)): (f.read_bytes(), f.stat().st_mtime_ns)
            for f in sorted(paper.rglob("*")) if f.is_file()}


def rewrite(paper):
    # Push every existing file's mtime into the past, so a rewrite by the scripts would show up.
    for f in paper.rglob("*"):
        if f.is_file():
            os.utime(f, ns=(10**18, 10**18))


REWRITES_SAME = """
(v / "generated" / "values.tex").write_text("\\\\newcommand{\\\\valSteps}{1500}\\n")
(v / "generated" / "tables" / "results.tex").write_text("0.42\\n")
(v / "figures" / "loss.pdf").write_bytes(b"%PDF-1.4 figure\\n")
(v / "figures" / "src" / "loss.svg").write_text("<svg/>")
"""

STALE = """
(v / "generated" / "tables" / "results.tex").write_text("0.99\\n")
(v / "figures" / "src" / "extra").mkdir()
(v / "figures" / "src" / "extra" / "new.dot").write_text("digraph {}")
"""


def test_regenerate_passes_and_leaves_the_folder_untouched(tmp_path):
    paper = regen_paper(tmp_path, REWRITES_SAME)
    rewrite(paper)
    original = tree(paper)
    cp.check_regenerated(paper)
    assert statuses()["figures and values match the data"][0] == "PASS"
    assert tree(paper) == original


def test_regenerate_fails_on_stale_table_and_restores_everything(tmp_path):
    paper = regen_paper(tmp_path, STALE)
    rewrite(paper)
    original = tree(paper)
    cp.check_regenerated(paper)
    status, detail = statuses()["figures and values match the data"]
    assert status == "FAIL" and "generated/tables/results.tex" in detail
    assert tree(paper) == original
    assert not (paper / "figures" / "src" / "extra").exists()


def test_regenerate_restores_after_the_scripts_crash(tmp_path):
    paper = regen_paper(tmp_path, STALE + "raise SystemExit('boom')\n")
    rewrite(paper)
    original = tree(paper)
    cp.check_regenerated(paper)
    status, detail = statuses()["figures and values match the data"]
    assert status == "FAIL" and "boom" in detail
    assert tree(paper) == original


def test_regenerate_can_skip_comparing_figures(tmp_path):
    paper = regen_paper(tmp_path, REWRITES_SAME + '(v / "figures" / "loss.pdf").write_bytes(b"%PDF-1.4 other\\n")\n')
    cp.check_regenerated(paper, compare_figures=False)
    assert statuses()["figures and values match the data"][0] == "PASS"
    cp.RESULTS.clear()
    cp.check_regenerated(paper)
    status, detail = statuses()["figures and values match the data"]
    assert status == "FAIL" and "figures/loss.pdf" in detail
