#!/usr/bin/env python3
"""Download a paper's PDF from whatever identifies it: an arXiv ID or link, a DOI, an OpenReview, PubMed Central,
ACL Anthology or Semantic Scholar link, a publisher's page, a direct PDF link, or just its title.

    python3 fetch_paper.py 1706.03762 --out papers/<slug>/paper.pdf
    python3 fetch_paper.py https://doi.org/10.1371/journal.pone.0000308 --out papers/<slug>/paper.pdf
    python3 fetch_paper.py "Emergence of scaling in random networks" --out papers/<slug>/paper.pdf

Only open-access copies are downloaded: arXiv, the open-access locations OpenAlex, Semantic Scholar and Europe PMC
list (and Unpaywall's, with --email or $UNPAYWALL_EMAIL), and the PDF a paper's own web page links to in its
citation_pdf_url tag. Nothing here gets around a paywall or a site's bot protection: if no open copy turns up, it
says so, lists what it tried, and the learner downloads the PDF through their own access and adds it by hand.

Writes the PDF and, next to it, source.json (title, DOI, arXiv ID, where the PDF came from). A downloaded file only
counts if it really is a PDF; publishers often answer a PDF link with an HTML login page.

Exit codes: 0 downloaded; 2 the input isn't something it can look up; 3 no open-access copy found;
4 a title matched several papers (the candidates are printed: pick one and pass its DOI or arXiv ID).
Standard library only.
"""
import argparse
import difflib
import html
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "researcher-pal-fetch/1.0 (downloads one open-access paper for a learner's local study)"
MIN_PDF_BYTES = 10_000
TITLE_MATCH = 0.92

ARXIV_NEW = r"\d{4}\.\d{4,5}"
ARXIV_OLD = r"[a-z][a-z\-]*(?:\.[A-Z]{2})?/\d{7}"
ARXIV_ID = r"(?:%s|%s)" % (ARXIV_NEW, ARXIV_OLD)
DOI = r"10\.\d{4,9}/[^\s\"'<>]+"


# ---------------------------------------------------------------- what was given
def classify(text):
    """(kind, value) for what the learner typed. Kinds: arxiv, doi, openreview, pmc, acl, s2, url, title."""
    text = text.strip().strip("<>")
    # An explicit version (v7) is kept: equation numbers can shift between versions.
    match = (re.search(r"arxiv\.org/(?:abs|pdf|html|format)/(%s(?:v\d+)?)" % ARXIV_ID, text, re.I)
             or re.match(r"arxiv:\s*(%s(?:v\d+)?)" % ARXIV_ID, text, re.I)
             or re.fullmatch(r"(%s(?:v\d+)?)" % ARXIV_ID, text))
    if match:
        return "arxiv", match.group(1)
    match = re.search(r"openreview\.net/(?:forum|pdf|attachment)\?id=([\w\-]+)", text)
    if match:
        return "openreview", match.group(1)
    match = re.search(r"\b(PMC\d{4,})\b", text, re.I)
    if match:
        return "pmc", match.group(1).upper()
    match = re.search(r"aclanthology\.org/([\w.\-]+?)(?:\.pdf)?/?$", text)
    if match:
        return "acl", match.group(1)
    match = re.search(r"semanticscholar\.org/paper/(?:[^/]+/)?([0-9a-f]{40})", text)
    if match:
        return "s2", match.group(1)
    match = re.search(r"(?:doi\.org/|doi:\s*|^)(%s)" % DOI, text, re.I)
    if match:
        doi = urllib.parse.unquote(match.group(1)).rstrip(".,;)")
        arxiv = re.fullmatch(r"10\.48550/arxiv\.(%s)" % ARXIV_ID, doi, re.I)
        return ("arxiv", arxiv.group(1)) if arxiv else ("doi", doi)
    if re.match(r"https?://", text):
        return "url", text
    if len(re.findall(r"[A-Za-z]{2,}", text)) >= 3:
        return "title", text
    return None, text


# ---------------------------------------------------------------- HTTP
_SSL = None


def ssl_context():
    """python.org's Python on macOS can ship an empty CA store; fall back to the system's (verification stays on)."""
    global _SSL
    if _SSL is None:
        _SSL = ssl.create_default_context()
        if not _SSL.cert_store_stats().get("x509_ca"):
            for candidate in (os.environ.get("SSL_CERT_FILE"), "/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
                if candidate and Path(candidate).exists():
                    _SSL = ssl.create_default_context(cafile=candidate)
                    break
    return _SSL


def http_get(url, accept=None, attempts=2):
    """(bytes, content-type, final URL). Retries once on throttling or a timeout."""
    for attempt in range(attempts):
        try:
            headers = {"User-Agent": USER_AGENT}
            if accept:
                headers["Accept"] = accept
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45,
                                        context=ssl_context()) as response:
                return response.read(), response.headers.get("Content-Type", ""), response.geturl()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == attempts - 1:
                raise
        time.sleep(4)


def get_json(url):
    return json.loads(http_get(url, accept="application/json")[0].decode("utf-8", "replace"))


def why(exc):
    return "HTTP %s" % exc.code if isinstance(exc, urllib.error.HTTPError) else type(exc).__name__


# ---------------------------------------------------------------- metadata services (each returns a dict)
def fold(text):
    text = unicodedata.normalize("NFKD", html.unescape(text or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text)).strip()


def title_ratio(a, b):
    return difflib.SequenceMatcher(None, fold(a), fold(b)).ratio() if a and b else 0.0


def openalex(path):
    """One OpenAlex work: {title, doi, arxiv, pmcid, pdfs}."""
    params = {"mailto": os.environ["OPENALEX_MAILTO"]} if os.environ.get("OPENALEX_MAILTO") else {}
    work = get_json("https://api.openalex.org/works/%s%s" % (path, ("?" + urllib.parse.urlencode(params)) if params else ""))
    return openalex_record(work)


def openalex_record(work):
    locations = [work.get("best_oa_location") or {}] + (work.get("locations") or [])
    pdfs = [loc.get("pdf_url") for loc in locations if loc and loc.get("is_oa") is not False and loc.get("pdf_url")]
    landing = [loc.get("landing_page_url") for loc in locations if loc and loc.get("landing_page_url")]
    ids = work.get("ids") or {}
    arxiv = next((re.search(ARXIV_ID, u).group(0) for u in landing + pdfs if "arxiv.org" in u and re.search(ARXIV_ID, u)), None)
    return {"title": work.get("display_name") or work.get("title"),
            "doi": (work.get("doi") or "").replace("https://doi.org/", "") or None,
            "arxiv": arxiv, "pmcid": (ids.get("pmcid") or "").rstrip("/").split("/")[-1] or None,
            "pdfs": pdfs, "via": "OpenAlex"}


def semantic_scholar(paper_id):
    data = get_json("https://api.semanticscholar.org/graph/v1/paper/%s?fields=title,externalIds,openAccessPdf"
                    % urllib.parse.quote(paper_id, safe=":/"))
    ext = data.get("externalIds") or {}
    pdf = (data.get("openAccessPdf") or {}).get("url")
    return {"title": data.get("title"), "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
            "pmcid": ("PMC" + str(ext["PubMedCentral"])) if ext.get("PubMedCentral") else None,
            "pdfs": [pdf] if pdf else [], "via": "Semantic Scholar"}


def arxiv_doi_record(ident):
    """Title from arXiv's own DataCite DOI (10.48550/arXiv.<id>), via doi.org; a fallback when other services are busy."""
    data = json.loads(http_get("https://doi.org/10.48550/arXiv." + re.sub(r"v\d+$", "", ident),
                               accept="application/vnd.citationstyles.csl+json")[0].decode("utf-8", "replace"))
    title = data.get("title")
    return {"title": title[0] if isinstance(title, list) else title, "doi": None, "arxiv": None, "pdfs": [], "via": "doi.org"}


def unpaywall(doi, email):
    data = get_json("https://api.unpaywall.org/v2/%s?email=%s" % (urllib.parse.quote(doi), urllib.parse.quote(email)))
    locations = [data.get("best_oa_location") or {}] + (data.get("oa_locations") or [])
    return {"title": data.get("title"), "doi": doi, "arxiv": None, "pmcid": None,
            "pdfs": [l["url_for_pdf"] for l in locations if l and l.get("url_for_pdf")], "via": "Unpaywall"}


def europe_pmc(pmcid):
    data = get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": "PMCID:%s" % pmcid, "resultType": "core", "format": "json"}))
    results = (data.get("resultList") or {}).get("result") or []
    if not results:
        return {"title": None, "doi": None, "arxiv": None, "pmcid": pmcid, "pdfs": [], "via": "Europe PMC"}
    hit = results[0]
    links = ((hit.get("fullTextUrlList") or {}).get("fullTextUrl")) or []
    pdfs = [l["url"] for l in links if l.get("documentStyle") == "pdf" and l.get("availabilityCode") in ("OA", "F")]
    return {"title": hit.get("title"), "doi": hit.get("doi"), "arxiv": None, "pmcid": pmcid, "pdfs": pdfs,
            "via": "Europe PMC"}


def page_meta(page_html):
    """The Highwire citation tags most publishers and repositories put on a paper's page."""
    found = {}
    def attribute(tag, key):  # quoted or unquoted, as HTML allows (aclanthology.org writes name=citation_title)
        match = re.search(r"\b%s\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))" % key, tag, re.I)
        return None if not match else next(g for g in match.groups() if g is not None)
    for tag in re.findall(r"<meta\b[^>]*>", page_html, re.I):
        name, content = attribute(tag, "name"), attribute(tag, "content")
        if name and content is not None:
            found.setdefault(name.lower(), html.unescape(content).strip())
    return {"title": found.get("citation_title"), "doi": found.get("citation_doi"),
            "arxiv": found.get("citation_arxiv_id"), "pdf": found.get("citation_pdf_url")}


# ---------------------------------------------------------------- resolving
class Resolver:
    def __init__(self, email=None, log=print):
        self.email = email
        self.log = log
        self.tried = []          # (where, what happened)
        self.meta = {"title": None, "doi": None, "arxiv": None}
        self.candidates = []     # (pdf url, where it came from), in order of preference
        self.asked = {}          # (service, identifier) -> record, so nothing is looked up twice

    def note(self, where, what):
        self.tried.append((where, what))

    def add(self, url, where):
        if url and url not in [u for u, _ in self.candidates]:
            self.candidates.append((url, where))

    def learn(self, record):
        for key in ("title", "doi", "arxiv"):
            if record.get(key) and not self.meta.get(key):
                self.meta[key] = record[key]

    def ask(self, where, call, key=None):
        if key is not None and (where, key) in self.asked:
            return self.asked[(where, key)]
        try:
            record = call()
        except Exception as exc:  # a service being down is reported, never fatal
            self.note(where, "unavailable (%s)" % why(exc))
            return None
        self.learn(record)
        self.note(where, "%d open-access PDF link(s)" % len(record.get("pdfs") or []) +
                  (", arXiv copy %s" % record["arxiv"] if record.get("arxiv") else ""))
        for pdf in record.get("pdfs") or []:
            self.add(pdf, where)
        if key is not None:
            self.asked[(where, key)] = record
        return record

    def arxiv(self, ident):
        self.meta["arxiv"] = ident  # what the learner asked for wins, version included
        self.add("https://arxiv.org/pdf/%s" % ident, "arXiv")

    def doi(self, doi):
        self.meta["doi"] = self.meta.get("doi") or doi
        s2 = self.ask("Semantic Scholar", lambda: semantic_scholar("DOI:" + doi), key=doi.lower())
        oa = self.ask("OpenAlex", lambda: openalex("doi:" + doi), key=doi.lower())
        # An arXiv copy is the most dependable download, so it goes first.
        arxiv = self.meta.get("arxiv") or (s2 or {}).get("arxiv") or (oa or {}).get("arxiv")
        if arxiv:
            self.candidates.insert(0, ("https://arxiv.org/pdf/%s" % arxiv, "arXiv (copy of the DOI)"))
        if self.email:
            self.ask("Unpaywall", lambda: unpaywall(doi, self.email))
        pmcid = (s2 or {}).get("pmcid") or (oa or {}).get("pmcid")
        if pmcid:
            self.ask("Europe PMC", lambda: europe_pmc(pmcid), key=pmcid)
        self.landing("https://doi.org/" + urllib.parse.quote(doi, safe="/"), "the DOI's landing page")

    def landing(self, url, where):
        """A paper's own web page: a PDF link in its citation tags, or a DOI/arXiv ID to look up."""
        try:
            body, ctype, final = http_get(url)
        except Exception as exc:
            self.note(where, "unavailable (%s)" % why(exc))
            return
        if body[:5] == b"%PDF-":
            self.add(final, where)
            self.note(where, "is itself a PDF")
            return
        meta = page_meta(body.decode("utf-8", "replace"))
        self.learn(meta)
        if meta["pdf"]:
            self.add(urllib.parse.urljoin(final, meta["pdf"]), where + " (citation_pdf_url)")
        self.note(where, "PDF link in its citation tags" if meta["pdf"] else "no PDF link in its citation tags")
        return meta

    def resolve(self, kind, value):
        if kind == "arxiv":
            self.arxiv(value)
            self.ask("Semantic Scholar", lambda: semantic_scholar("arXiv:" + re.sub(r"v\d+$", "", value)))
            if not self.meta.get("title"):
                self.ask("arXiv DOI (doi.org)", lambda: arxiv_doi_record(value))
        elif kind == "doi":
            self.doi(value)
        elif kind == "acl":
            self.landing("https://aclanthology.org/%s/" % value, "ACL Anthology")
            self.add("https://aclanthology.org/%s.pdf" % value, "ACL Anthology")
        elif kind == "pmc":
            record = self.ask("Europe PMC", lambda: europe_pmc(value), key=value)
            if record and record.get("doi"):
                self.doi(record["doi"])
        elif kind == "s2":
            record = self.ask("Semantic Scholar", lambda: semantic_scholar(value))
            if record and record.get("arxiv"):
                self.arxiv(record["arxiv"])
            if record and record.get("doi"):
                self.doi(record["doi"])
        elif kind == "openreview":
            # openreview.net blocks scripted downloads, so look for the same paper elsewhere by its title.
            self.add("https://openreview.net/pdf?id=%s" % value, "OpenReview")
            try:
                notes = get_json("https://api2.openreview.net/notes?id=%s" % value).get("notes") or []
                content = notes[0].get("content", {}) if notes else {}
                title = content.get("title", {})
                title = title.get("value") if isinstance(title, dict) else title
            except Exception as exc:
                self.note("OpenReview API", "unavailable (%s)" % why(exc))
                title = None
            if title:
                self.note("OpenReview API", "title: %s" % title)
                self.meta["title"] = title
                return self.by_title(title)
        elif kind == "url":
            meta = self.landing(value, "the page you gave")
            if meta:
                if meta.get("arxiv"):
                    self.arxiv(re.search(ARXIV_ID, meta["arxiv"]).group(0) if re.search(ARXIV_ID, meta["arxiv"]) else meta["arxiv"])
                if meta.get("doi"):
                    self.doi(meta["doi"])
        elif kind == "title":
            return self.by_title(value)
        return None

    def by_title(self, title):
        """Best title match across OpenAlex and Semantic Scholar. Returns candidates when it isn't clear-cut."""
        found = []
        try:
            params = {"search": title, "per-page": 5}
            for work in get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params)).get("results") or []:
                found.append(openalex_record(work))
            self.note("OpenAlex title search", "%d results" % len(found))
        except Exception as exc:
            self.note("OpenAlex title search", "unavailable (%s)" % why(exc))
        try:
            data = get_json("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
                {"query": title, "limit": 5, "fields": "title,externalIds,openAccessPdf,year"}))
            for item in data.get("data") or []:
                ext = item.get("externalIds") or {}
                pdf = (item.get("openAccessPdf") or {}).get("url")
                found.append({"title": item.get("title"), "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
                              "pdfs": [pdf] if pdf else [], "via": "Semantic Scholar"})
            self.note("Semantic Scholar title search", "%d results" % len(data.get("data") or []))
        except Exception as exc:
            self.note("Semantic Scholar title search", "unavailable (%s)" % why(exc))
        close = [r for r in found if title_ratio(title, r.get("title")) >= TITLE_MATCH]
        papers = {}
        for record in close:  # the same paper from two services counts once
            key = (record.get("doi") or "").lower() or record.get("arxiv") or fold(record.get("title"))
            papers.setdefault(key, []).append(record)
        # Records that all carry the very same title are versions of one paper (the arXiv preprint and the
        # journal or book version): treat them as one, so the open copy can be used.
        if len(papers) > 1 and len({fold(r.get("title")) for r in close}) == 1:
            self.note("title match", "%d records share this exact title; treated as versions of one paper" % len(papers))
            papers = {"one": close}
        if len(papers) != 1:
            ranked = sorted(found, key=lambda r: -title_ratio(title, r.get("title")))
            return [r for r in ranked if r.get("title")][:6]
        group = next(iter(papers.values()))
        for record in group:
            self.learn(record)
            for pdf in record.get("pdfs") or []:
                self.add(pdf, record["via"] + " (title match)")
        if self.meta.get("arxiv"):
            self.candidates.insert(0, ("https://arxiv.org/pdf/%s" % self.meta["arxiv"], "arXiv (title match)"))
        if self.meta.get("doi") and not self.candidates:
            self.doi(self.meta["doi"])
        return None

    def download(self, out):
        for url, where in self.candidates:
            try:
                body, ctype, final = http_get(url)
            except Exception as exc:
                self.note(where, "download failed (%s): %s" % (why(exc), url))
                continue
            if body[:5] != b"%PDF-" or len(body) < MIN_PDF_BYTES:
                self.note(where, "not a PDF (%s, %d bytes; often a login or bot-check page): %s"
                          % (ctype.split(";")[0] or "unknown type", len(body), url))
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(body)
            return url, where
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paper", nargs="+", help="arXiv ID, DOI, link, or the paper's title")
    parser.add_argument("--out", type=Path, default=Path("paper.pdf"), help="where to save the PDF (default ./paper.pdf)")
    parser.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL"),
                        help="your email, to also ask Unpaywall (its terms require one); default $UNPAYWALL_EMAIL")
    args = parser.parse_args()
    text = " ".join(args.paper)

    kind, value = classify(text)
    if kind is None:
        print("Can't tell what %r is. Give an arXiv ID, a DOI, a link to the paper, or its full title." % text)
        sys.exit(2)
    print("Looking up %s: %s" % ({"arxiv": "arXiv paper", "doi": "DOI", "openreview": "OpenReview paper",
                                  "pmc": "PubMed Central paper", "acl": "ACL Anthology paper",
                                  "s2": "Semantic Scholar paper", "url": "the page", "title": "the title"}[kind], value))
    resolver = Resolver(email=args.email)
    ambiguous = resolver.resolve(kind, value)
    if ambiguous is not None:
        print("\nThe title doesn't pick out one paper. Closest matches:")
        for record in ambiguous:
            ident = ("arXiv:%s" % record["arxiv"]) if record.get("arxiv") else ("doi:%s" % record["doi"]) if record.get("doi") else "-"
            print("  - %s  [%s]  (match %.2f)" % (record.get("title"), ident, title_ratio(value, record.get("title"))))
        print("Run again with the right one's DOI or arXiv ID.")
        sys.exit(4)

    got = resolver.download(args.out)
    print()
    for where, what in resolver.tried:
        print("  %-34s %s" % (where, what))
    if not got:
        title = (resolver.meta.get("title") or "").strip().rstrip(".")
        print("\nNo open-access copy found%s." % (" for: " + title if title else ""))
        if kind == "openreview":
            print("openreview.net doesn't allow scripted downloads. Open %s in your browser, download the PDF, and add "
                  "it as a file; or give the paper's title, in case it is also on arXiv." % text)
        else:
            print("If you have access (a library, a subscription), download the PDF yourself and add it as a file.")
        sys.exit(3)
    url, where = got
    source = dict(resolver.meta, input=text, pdf_url=url, via=where, fetched=time.strftime("%Y-%m-%d"))
    if resolver.meta.get("arxiv"):
        source["latex_source"] = "https://arxiv.org/e-print/%s" % resolver.meta["arxiv"]
    (args.out.parent / "source.json").write_text(json.dumps(source, indent=2) + "\n")
    print("\nSaved %s (%d KB) from %s" % (args.out, args.out.stat().st_size // 1024, where))
    print("  title: %s" % (resolver.meta.get("title") or "unknown"))
    if source.get("latex_source"):
        print("  LaTeX source (exact equations): %s" % source["latex_source"])


if __name__ == "__main__":
    main()
