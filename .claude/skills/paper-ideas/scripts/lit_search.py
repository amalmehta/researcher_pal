#!/usr/bin/env python3
"""Keyword literature search over arXiv, Semantic Scholar and Crossref, returning verified records.

    python3 lit_search.py "learning rate warmup transformer" "attention logit scaling" \
        --guard-text paper/<slug>/<venue>/sections --limit 5 --out ideas/literature/warmup

Every record comes straight from a service's API with its identifier (arXiv ID, DOI or Semantic
Scholar paper ID); nothing is summarized or guessed. Records found by several services are merged.

Privacy guard: --guard-text points at the unpublished draft (files or folders of .tex/.md). A query
that shares 6 or more consecutive words with it, or is longer than 12 words, is refused, so draft
text never leaves the machine. Writes <out>.json and <out>.md; prints the Markdown. Standard library only.
"""
import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "paper-ideas-lit-search/1.0 (keyword literature check for a local draft)"
MAX_QUERY_WORDS = 12
SHINGLE = 6


def fold(text):
    text = re.sub(r"\\[a-zA-Z]+\*?|[{}$\\%~^_]", " ", text or "")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def words(text):
    return re.findall(r"[a-z0-9]+", fold(text))


def guard_shingles(paths):
    shingles = set()
    for raw in paths:
        path = Path(raw)
        files = [f for f in path.rglob("*") if f.suffix in (".tex", ".md", ".txt")] if path.is_dir() else [path]
        for f in files:
            text = re.sub(r"(?<!\\)%.*", "", f.read_text(errors="replace"))
            w = words(text)
            shingles.update(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))
    return shingles


def check_query(query, shingles):
    w = words(query)
    if len(w) > MAX_QUERY_WORDS:
        return "query has %d words; keyword queries are limited to %d" % (len(w), MAX_QUERY_WORDS)
    for i in range(len(w) - SHINGLE + 1):
        if tuple(w[i:i + SHINGLE]) in shingles:
            return "query shares %d consecutive words with the draft: %r" % (SHINGLE, " ".join(w[i:i + SHINGLE]))
    return None


def fetch(url, attempts=3):
    """GET with backoff: rate limits (HTTP 429) wait 10 s then 30 s; other transient errors 3 s then 6 s.
    Public APIs without keys throttle bursts, so a failed service is reported rather than retried forever."""
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
            time.sleep((10, 30)[attempt] if exc.code == 429 else (3, 6)[attempt])
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == attempts - 1:
                raise
            time.sleep((3, 6)[attempt])


def search_arxiv(query, limit):
    terms = " AND ".join("all:%s" % t for t in words(query))
    xml = fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": terms, "max_results": limit, "sortBy": "relevance"}))
    out = []
    for entry in xml.split("<entry>")[1:]:
        ident = re.search(r"<id>https?://arxiv\.org/abs/([^<]+?)(?:v\d+)?</id>", entry)
        title = re.search(r"<title>(.*?)</title>", entry, flags=re.S)
        year = re.search(r"<published>(\d{4})", entry)
        abstract = re.search(r"<summary>(.*?)</summary>", entry, flags=re.S)
        if ident and title:
            out.append({
                "title": re.sub(r"\s+", " ", title.group(1)).strip(),
                "authors": re.findall(r"<name>(.*?)</name>", entry),
                "year": int(year.group(1)) if year else None,
                "ids": {"arxiv": ident.group(1)},
                "url": "https://arxiv.org/abs/" + ident.group(1),
                "abstract": re.sub(r"\s+", " ", abstract.group(1)).strip() if abstract else "",
            })
    return out


def search_semantic_scholar(query, limit):
    data = json.loads(fetch("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode({
        "query": " ".join(words(query)), "limit": limit,
        "fields": "title,year,authors,externalIds,url,abstract,venue"})))
    out = []
    for item in data.get("data", []):
        ids = {"s2": item.get("paperId")}
        ext = item.get("externalIds") or {}
        if ext.get("ArXiv"):
            ids["arxiv"] = ext["ArXiv"]
        if ext.get("DOI"):
            ids["doi"] = ext["DOI"]
        out.append({
            "title": item.get("title") or "", "authors": [a.get("name", "") for a in item.get("authors") or []],
            "year": item.get("year"), "ids": ids, "url": item.get("url") or "", "abstract": item.get("abstract") or "",
            "venue": item.get("venue") or "",
        })
    return out


def search_crossref(query, limit):
    data = json.loads(fetch("https://api.crossref.org/works?" + urllib.parse.urlencode({
        "query.bibliographic": " ".join(words(query)), "rows": limit,
        "select": "DOI,title,author,issued,container-title,abstract"})))
    out = []
    for item in data["message"]["items"]:
        issued = (item.get("issued") or {}).get("date-parts") or [[None]]
        out.append({
            "title": (item.get("title") or [""])[0],
            "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author") or []],
            "year": issued[0][0], "ids": {"doi": item.get("DOI")}, "url": "https://doi.org/" + item.get("DOI", ""),
            "abstract": re.sub(r"<[^>]+>", "", item.get("abstract") or ""),
            "venue": (item.get("container-title") or [""])[0],
        })
    return out


SERVICES = {"arxiv": search_arxiv, "semanticscholar": search_semantic_scholar, "crossref": search_crossref}


def merge(records):
    merged = {}
    for rec in records:
        key = " ".join(words(rec["title"]))
        if not key:
            continue
        if key in merged:
            merged[key]["found_in"] = sorted(set(merged[key]["found_in"]) | set(rec["found_in"]))
            merged[key]["ids"].update({k: v for k, v in rec["ids"].items() if v})
            for field in ("abstract", "venue", "year", "url"):
                if not merged[key].get(field) and rec.get(field):
                    merged[key][field] = rec[field]
        else:
            merged[key] = rec
    return list(merged.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("queries", nargs="+")
    parser.add_argument("--guard-text", nargs="*", default=[], help="unpublished draft files/folders queries must not quote")
    parser.add_argument("--services", default="arxiv,semanticscholar,crossref")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", type=Path, help="write <out>.json and <out>.md")
    args = parser.parse_args()

    shingles = guard_shingles(args.guard_text)
    for query in args.queries:
        problem = check_query(query, shingles)
        if problem:
            print("REFUSED %r: %s" % (query, problem), file=sys.stderr)
            sys.exit(2)

    report = {"queries": args.queries, "services": {}, "records": []}
    raw = []
    for query in args.queries:
        for name in args.services.split(","):
            status = report["services"].setdefault(name, {"ok": 0, "errors": []})
            try:
                found = SERVICES[name](query, args.limit)
                status["ok"] += 1
                for rec in found:
                    rec["found_in"] = [name]
                    rec["query"] = query
                raw += found
            except Exception as exc:  # failures are reported, never hidden
                status["errors"].append("%r: %s" % (query, getattr(exc, "code", type(exc).__name__)))
            time.sleep(1.0 if name != "arxiv" else 3.0)
    report["records"] = sorted(merge(raw), key=lambda r: (-len(r["found_in"]), -(r.get("year") or 0)))

    lines = ["# Literature search", "", "**Queries (keywords only):** " + "; ".join("`%s`" % q for q in args.queries), "",
             "| Service | Queries answered | Errors |", "|---|---|---|"]
    lines += ["| %s | %d/%d | %s |" % (n, s["ok"], len(args.queries), "; ".join(s["errors"]) or "none") for n, s in report["services"].items()]
    lines += ["", "| Title | Year | First author | IDs | Found in |", "|---|---|---|---|---|"]
    for r in report["records"]:
        ids = ", ".join("%s:%s" % (k, v) for k, v in r["ids"].items() if v and k != "s2") or "s2:" + str(r["ids"].get("s2"))
        lines.append("| [%s](%s) | %s | %s | %s | %s |" % (r["title"].replace("|", "/")[:90], r["url"], r.get("year") or "",
                                                          (r["authors"] or [""])[0], ids, ", ".join(r["found_in"])))
    markdown = "\n".join(lines) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".json").write_text(json.dumps(report, indent=2))
        args.out.with_suffix(".md").write_text(markdown)
    print(markdown)


if __name__ == "__main__":
    main()
