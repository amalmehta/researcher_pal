"""Tests for researcher-pal's fetch_paper.py. The network is replaced by canned answers, so these run offline."""
import json
import sys
import urllib.error

import pytest

import fetch_paper as fp

PDF = b"%PDF-1.4\n" + b"0" * 20_000


@pytest.mark.parametrize("text, expected", [
    ("1706.03762", ("arxiv", "1706.03762")),
    ("1706.03762v7", ("arxiv", "1706.03762v7")),
    ("arXiv:1706.03762", ("arxiv", "1706.03762")),
    ("https://arxiv.org/abs/1706.03762v5", ("arxiv", "1706.03762v5")),
    ("https://arxiv.org/pdf/cond-mat/9910332v1", ("arxiv", "cond-mat/9910332v1")),
    ("cond-mat/9910332", ("arxiv", "cond-mat/9910332")),
    ("doi: 10.48550/arXiv.1706.03762", ("arxiv", "1706.03762")),
    ("10.1371/journal.pone.0000308", ("doi", "10.1371/journal.pone.0000308")),
    ("https://doi.org/10.1038/nature14539", ("doi", "10.1038/nature14539")),
    ("https://openreview.net/forum?id=rJ4km2R5t7", ("openreview", "rJ4km2R5t7")),
    ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159421/", ("pmc", "PMC3159421")),
    ("https://aclanthology.org/N19-1423/", ("acl", "N19-1423")),
    ("https://www.semanticscholar.org/paper/Attention-Vaswani/204e3073870fae3d05bcbc2f6a8e263d9b72e776",
     ("s2", "204e3073870fae3d05bcbc2f6a8e263d9b72e776")),
    ("https://example.com/paper.pdf", ("url", "https://example.com/paper.pdf")),
    ("Emergence of scaling in random networks", ("title", "Emergence of scaling in random networks")),
    ("deep learning", (None, "deep learning")),
])
def test_classify(text, expected):
    assert fp.classify(text) == expected


def test_page_meta_reads_quoted_and_unquoted_attributes():
    page = ('<meta content="BERT: Pre-training &amp; more" name=citation_title>'
            '<meta name="citation_pdf_url" content="https://x.org/a.pdf"><meta name=\'citation_doi\' content=\'10.1/abc\'>')
    assert fp.page_meta(page) == {"title": "BERT: Pre-training & more", "doi": "10.1/abc", "arxiv": None,
                                  "pdf": "https://x.org/a.pdf"}


class FakeWeb:
    """Canned answers by URL prefix; anything else is a 404."""
    def __init__(self, routes):
        self.routes = routes
        self.seen = []

    def __call__(self, url, accept=None, attempts=2):
        self.seen.append(url)
        for prefix, answer in self.routes.items():
            if url.startswith(prefix):
                if isinstance(answer, Exception):
                    raise answer
                body, ctype = answer
                return (json.dumps(body).encode() if isinstance(body, dict) else body), ctype, url
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)


def run(monkeypatch, tmp_path, web, *args):
    monkeypatch.setattr(fp, "http_get", web)
    monkeypatch.setattr(sys, "argv", ["fetch_paper.py", *args, "--out", str(tmp_path / "p" / "paper.pdf")])
    with pytest.raises(SystemExit) as exit_info:
        fp.main()
        raise SystemExit(0)  # main() returns normally on success
    return exit_info.value.code


def test_arxiv_id_downloads_and_records_the_source(monkeypatch, tmp_path):
    web = FakeWeb({"https://arxiv.org/pdf/1706.03762": (PDF, "application/pdf"),
                   "https://api.semanticscholar.org/": ({"title": "Attention Is All You Need", "externalIds": {"ArXiv": "1706.03762"}},
                                                        "application/json")})
    assert run(monkeypatch, tmp_path, web, "arXiv:1706.03762") == 0
    assert (tmp_path / "p" / "paper.pdf").read_bytes() == PDF
    source = json.loads((tmp_path / "p" / "source.json").read_text())
    assert source["title"] == "Attention Is All You Need"
    assert source["latex_source"] == "https://arxiv.org/e-print/1706.03762"


def test_a_doi_prefers_its_arxiv_copy(monkeypatch, tmp_path):
    web = FakeWeb({"https://api.semanticscholar.org/": ({"title": "T", "externalIds": {"ArXiv": "2001.00001"}}, "application/json"),
                   "https://api.openalex.org/": ({"display_name": "T", "best_oa_location": {"pdf_url": "https://pub.org/t.pdf"}},
                                                 "application/json"),
                   "https://arxiv.org/pdf/2001.00001": (PDF, "application/pdf")})
    assert run(monkeypatch, tmp_path, web, "10.1000/t") == 0
    assert json.loads((tmp_path / "p" / "source.json").read_text())["via"].startswith("arXiv")


def test_an_html_login_page_is_not_a_pdf(monkeypatch, tmp_path, capsys):
    web = FakeWeb({"https://api.openalex.org/": ({"display_name": "Paywalled", "best_oa_location": {"pdf_url": "https://pub.org/p.pdf"}},
                                                 "application/json"),
                   "https://pub.org/p.pdf": (b"<html>Please log in</html>" * 1000, "text/html"),
                   "https://doi.org/": (b"<html><meta name=citation_title content=Paywalled></html>", "text/html")})
    assert run(monkeypatch, tmp_path, web, "10.1000/paywalled") == 3
    out = capsys.readouterr().out
    assert "not a PDF" in out and "No open-access copy found for: Paywalled" in out
    assert not (tmp_path / "p" / "paper.pdf").exists()


def test_a_service_being_down_is_reported_not_fatal(monkeypatch, tmp_path, capsys):
    web = FakeWeb({"https://api.semanticscholar.org/": urllib.error.HTTPError("x", 429, "busy", {}, None),
                   "https://api.openalex.org/": ({"display_name": "T", "best_oa_location": {"pdf_url": "https://repo.org/t.pdf"}},
                                                 "application/json"),
                   "https://repo.org/t.pdf": (PDF, "application/pdf")})
    assert run(monkeypatch, tmp_path, web, "10.1000/t") == 0
    assert "unavailable (HTTP 429)" in capsys.readouterr().out


def search(results):
    return {"https://api.openalex.org/works?": ({"results": results}, "application/json"),
            "https://api.semanticscholar.org/graph/v1/paper/search": ({"data": []}, "application/json")}


def test_one_paper_under_two_records_is_treated_as_one(monkeypatch, tmp_path):
    routes = search([{"display_name": "Emergence of Scaling in Random Networks", "doi": "https://doi.org/10.1515/x",
                      "locations": [{"landing_page_url": "https://arxiv.org/abs/cond-mat/9910332"}]},
                     {"display_name": "Emergence of scaling in random networks", "doi": "https://doi.org/10.1126/science.286.5439.509"}])
    routes["https://arxiv.org/pdf/cond-mat/9910332"] = (PDF, "application/pdf")
    assert run(monkeypatch, tmp_path, FakeWeb(routes), "Emergence of scaling in random networks") == 0


def test_two_different_papers_with_close_titles_ask_which(monkeypatch, tmp_path, capsys):
    routes = search([{"display_name": "Deep residual learning for image recognition", "doi": "https://doi.org/10.1/a"},
                     {"display_name": "Deep residual learning for image recognitions", "doi": "https://doi.org/10.1/b"}])
    assert run(monkeypatch, tmp_path, FakeWeb(routes), "Deep residual learning for image recognition") == 4
    out = capsys.readouterr().out
    assert "doi:10.1/a" in out and "doi:10.1/b" in out


def test_vague_input_is_refused(monkeypatch, tmp_path):
    assert run(monkeypatch, tmp_path, FakeWeb({}), "deep learning") == 2


def test_an_explicit_arxiv_version_is_kept_and_titled_via_doi_org(monkeypatch, tmp_path):
    web = FakeWeb({"https://arxiv.org/pdf/1706.03762v1": (PDF, "application/pdf"),
                   "https://api.semanticscholar.org/": urllib.error.HTTPError("x", 429, "busy", {}, None),
                   "https://doi.org/10.48550/arXiv.1706.03762": ({"title": "Attention Is All You Need"}, "application/json")})
    assert run(monkeypatch, tmp_path, web, "https://arxiv.org/abs/1706.03762v1") == 0
    source = json.loads((tmp_path / "p" / "source.json").read_text())
    assert source["arxiv"] == "1706.03762v1" and source["pdf_url"].endswith("1706.03762v1")
    assert source["title"] == "Attention Is All You Need"
