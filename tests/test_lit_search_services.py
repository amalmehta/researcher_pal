"""Tests for lit_search's service parsers, cache and search loop. No network: parsers get fixture payloads."""
import json

import lit_search


def test_parse_openalex_rebuilds_the_inverted_abstract():
    data = {"results": [{
        "id": "https://openalex.org/W123", "doi": "https://doi.org/10.1038/s41467-019-08746-5",
        "display_name": "Scale-free networks are rare", "publication_year": 2019,
        "authorships": [{"author": {"display_name": "Anna D. Broido"}}, {"author": {"display_name": "Aaron Clauset"}}],
        "abstract_inverted_index": {"Real-world": [0], "networks": [1], "are": [2], "rare": [3]},
        "primary_location": {"source": {"display_name": "Nature Communications"}},
    }]}
    record, = lit_search.parse_openalex(data)
    assert record["title"] == "Scale-free networks are rare"
    assert record["ids"] == {"openalex": "W123", "doi": "10.1038/s41467-019-08746-5"}
    assert record["authors"][0] == "Anna D. Broido"
    assert record["abstract"] == "Real-world networks are rare"
    assert record["venue"] == "Nature Communications"
    assert record["url"] == "https://doi.org/10.1038/s41467-019-08746-5"


def test_parse_openalex_handles_missing_fields():
    record, = lit_search.parse_openalex({"results": [{"id": "https://openalex.org/W9", "display_name": "No DOI"}]})
    assert record["ids"] == {"openalex": "W9"} and record["abstract"] == "" and record["year"] is None



def test_parse_crossref_strips_abstract_markup():
    data = {"message": {"items": [{
        "DOI": "10.1137/070710111", "title": ["Power-Law Distributions in Empirical Data"],
        "author": [{"given": "Aaron", "family": "Clauset"}], "issued": {"date-parts": [[2009, 11]]},
        "container-title": ["SIAM Review"], "abstract": "<jats:p>Power-law distributions occur</jats:p>"}]}}
    record, = lit_search.parse_crossref(data)
    assert record["abstract"] == "Power-law distributions occur"
    assert record["authors"] == ["Aaron Clauset"] and record["year"] == 2009


def test_parse_semantic_scholar_collects_identifiers():
    data = {"data": [{"paperId": "abc", "title": "T", "year": 2020, "authors": [{"name": "A B"}],
                      "externalIds": {"ArXiv": "2002.04745", "DOI": "10.1/x"}, "url": "https://s2/abc",
                      "abstract": "a", "venue": "ICML"}]}
    record, = lit_search.parse_semantic_scholar(data)
    assert record["ids"] == {"s2": "abc", "arxiv": "2002.04745", "doi": "10.1/x"}


def test_parse_arxiv_reads_entries():
    xml = """<feed><entry><id>http://arxiv.org/abs/1706.03762v5</id><title>Attention Is
    All You Need</title><published>2017-06-12T00:00:00Z</published><summary>The dominant sequence</summary>
    <author><name>Ashish Vaswani</name></author></entry></feed>"""
    record, = lit_search.parse_arxiv(xml)
    assert record["title"] == "Attention Is All You Need"
    assert record["ids"] == {"arxiv": "1706.03762"} and record["year"] == 2017
    assert record["authors"] == ["Ashish Vaswani"]


# ---------------------------------------------------------------- cache and the search loop
def test_cache_roundtrip_and_expiry(tmp_path):
    records = [{"title": "Cached paper", "ids": {"doi": "10.1/c"}, "authors": [], "year": 2024, "url": "", "abstract": ""}]
    lit_search.cache_write("crossref", "warmup schedule", 5, records, directory=tmp_path)
    assert lit_search.cache_read("crossref", "warmup schedule", 5, directory=tmp_path) == records
    assert lit_search.cache_read("crossref", "Warmup   Schedule!", 5, directory=tmp_path) == records  # normalized key
    assert lit_search.cache_read("crossref", "other query", 5, directory=tmp_path) is None
    assert lit_search.cache_read("crossref", "warmup schedule", 5, ttl_days=0, directory=tmp_path) is None


def test_run_searches_caches_successes_and_retries_failures(tmp_path, monkeypatch):
    calls = {"good": 0, "flaky": 0}

    def good(query, limit):
        calls["good"] += 1
        return [{"title": "Found it", "ids": {"doi": "10.1/g"}, "authors": ["X Y"], "year": 2024, "url": "", "abstract": ""}]

    def flaky(query, limit):
        calls["flaky"] += 1
        raise RuntimeError("429")

    monkeypatch.setitem(lit_search.SERVICES, "good", good)
    monkeypatch.setitem(lit_search.SERVICES, "flaky", flaky)
    monkeypatch.setitem(lit_search.PAUSE, "good", 0)
    monkeypatch.setitem(lit_search.PAUSE, "flaky", 0)

    records, status = lit_search.run_searches(["one query"], ["good", "flaky"], 5, cache_dir=tmp_path)
    assert [r["title"] for r in records] == ["Found it"]
    assert status["good"] == {"ok": 1, "cached": 0, "errors": []}
    assert status["flaky"]["ok"] == 0 and status["flaky"]["errors"]

    records, status = lit_search.run_searches(["one query"], ["good", "flaky"], 5, cache_dir=tmp_path)
    assert calls == {"good": 1, "flaky": 2}, "the answered service is cached; the failed one is retried"
    assert status["good"]["cached"] == 1
    assert len(records) == 1


def test_run_searches_merges_a_record_found_by_two_services(tmp_path, monkeypatch):
    def a(query, limit):
        return [{"title": "Same Paper", "ids": {"doi": "10.1/s"}, "authors": ["A"], "year": 2021, "url": "u", "abstract": ""}]

    def b(query, limit):
        return [{"title": "same paper", "ids": {"arxiv": "2101.1"}, "authors": ["A"], "year": None, "url": "",
                 "abstract": "an abstract"}]

    monkeypatch.setitem(lit_search.SERVICES, "a", a)
    monkeypatch.setitem(lit_search.SERVICES, "b", b)
    monkeypatch.setitem(lit_search.PAUSE, "a", 0)
    monkeypatch.setitem(lit_search.PAUSE, "b", 0)
    records, _ = lit_search.run_searches(["q"], ["a", "b"], 5, use_cache=False, cache_dir=tmp_path)
    assert len(records) == 1
    assert records[0]["found_in"] == ["a", "b"]
    assert records[0]["ids"] == {"doi": "10.1/s", "arxiv": "2101.1"}
    assert records[0]["abstract"] == "an abstract"  # filled in from the second service


def test_report_markdown_shows_services_and_records():
    records = [{"title": "A Paper", "ids": {"doi": "10.1/a"}, "authors": ["First Author"], "year": 2025,
                "url": "https://doi.org/10.1/a", "found_in": ["openalex", "crossref"]}]
    status = {"openalex": {"ok": 1, "cached": 1, "errors": []}, "arxiv": {"ok": 0, "cached": 0, "errors": ["'q': 429"]}}
    markdown = lit_search.report_markdown(["q"], records, status)
    assert "| openalex | 1/1 | 1 | none |" in markdown
    assert "429" in markdown and "A Paper" in markdown and "doi:10.1/a" in markdown


def test_cache_file_is_readable_json(tmp_path):
    lit_search.cache_write("openalex", "q", 3, [], directory=tmp_path)
    saved = json.loads(lit_search.cache_path("openalex", "q", 3, tmp_path).read_text())
    assert saved["service"] == "openalex" and saved["records"] == [] and "fetched" in saved
