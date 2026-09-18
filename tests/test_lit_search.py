"""Unit tests for paper-ideas' lit_search.py. The privacy guard is the part that must never regress:
an unpublished draft's wording must not leave the machine."""
import lit_search


def draft(tmp_path, text):
    (tmp_path / "results.tex").write_text(text)
    return [str(tmp_path)]


def test_guard_refuses_a_query_that_quotes_the_draft(tmp_path):
    paths = draft(tmp_path, "We train a small encoder decoder transformer trained to reverse digit sequences.")
    shingles = lit_search.guard_shingles(paths)
    assert lit_search.check_query("encoder decoder transformer trained to reverse", shingles)
    assert not lit_search.check_query("learning rate warmup transformer", shingles)


def test_guard_ignores_short_overlaps(tmp_path):
    paths = draft(tmp_path, "The learning rate warmup schedule matters for small transformers.")
    shingles = lit_search.guard_shingles(paths)
    assert not lit_search.check_query("learning rate warmup", shingles)


def test_guard_refuses_overlong_queries():
    assert lit_search.check_query(" ".join(["topic"] * 13), set())
    assert not lit_search.check_query(" ".join(["topic"] * 12), set())


def test_guard_reads_markdown_and_text_too(tmp_path):
    (tmp_path / "notes.md").write_text("our alignment metric counts the strongest attention position per target")
    shingles = lit_search.guard_shingles([str(tmp_path)])
    # six consecutive words from the notes: refused. Five ("strongest … target token"): allowed.
    assert lit_search.check_query("counts the strongest attention position per target", shingles)
    assert not lit_search.check_query("strongest attention position per target token", shingles)


def test_guard_is_case_and_punctuation_insensitive(tmp_path):
    paths = draft(tmp_path, "Warmup is necessary for post-LayerNorm transformers in this setting.")
    shingles = lit_search.guard_shingles(paths)
    assert lit_search.check_query("Warmup, is necessary for post LayerNorm transformers!", shingles)
