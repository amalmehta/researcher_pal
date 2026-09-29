#!/usr/bin/env python3
"""Keyword literature search over OpenAlex, Crossref, arXiv and Semantic Scholar.

    python3 lit_search.py "learning rate warmup transformer" "attention logit scaling" \
        --guard-text paper/<slug>/<venue>/sections --limit 5 --out ideas/literature/warmup

Every record comes straight from a service's API with its identifier (DOI, arXiv ID, OpenAlex or
Semantic Scholar ID); nothing is summarized or guessed. Records found by several services are merged.

Privacy guard: --guard-text points at the unpublished draft (files or folders of .tex/.md/.txt). A query
that shares 6 or more consecutive words with it, or is longer than 12 words, is refused, so draft text
never leaves the machine. Only the queries you pass are ever sent.

Caching: successful (service, query) results are cached on disk, failures are not. So re-running the same
command costs nothing for the services that answered and retries only the ones that failed --- which is the
normal case, because these free APIs throttle bursts. --no-cache ignores it, --cache-ttl sets the age limit.

Optional environment variables (all unset by default, nothing is sent without them):
    SEMANTIC_SCHOLAR_API_KEY   raises Semantic Scholar's rate limit
    OPENALEX_MAILTO            an email address for OpenAlex's polite pool (faster, more reliable)
    CROSSREF_MAILTO            the same for Crossref
    PAPER_IDEAS_CACHE          cache directory (default ~/.cache/paper-ideas/lit_search)

Writes <out>.json and <out>.md; prints the Markdown. Standard library only.
"""
import argparse
import hashlib
import json
import os
import random
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "paper-ideas-lit-search/2.0 (keyword literature check for a local draft)"
MAX_QUERY_WORDS = 12
SHINGLE = 6
DEFAULT_SERVICES = "openalex,crossref,arxiv,semanticscholar"
CACHE_DIR = Path(os.environ.get("PAPER_IDEAS_CACHE", Path.home() / ".cache" / "paper-ideas" / "lit_search"))
CACHE_TTL_DAYS = 14


# ---------------------------------------------------------------- privacy guard
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


# ---------------------------------------------------------------- cache
def cache_path(service, query, limit, directory=None):
    key = hashlib.sha1(("%s|%s|%d" % (service, " ".join(words(query)), limit)).encode()).hexdigest()[:16]
    return Path(directory or CACHE_DIR) / service / (key + ".json")


def cache_read(service, query, limit, ttl_days=CACHE_TTL_DAYS, directory=None):
    path = cache_path(service, query, limit, directory)
    if not path.exists():
        return None
    if ttl_days is not None and time.time() - path.stat().st_mtime > ttl_days * 86400:
        return None
    try:
        return json.loads(path.read_text())["records"]
    except (ValueError, KeyError):
        return None


def cache_write(service, query, limit, records, directory=None):
    path = cache_path(service, query, limit, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"service": service, "query": query, "limit": limit,
                                "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"), "records": records}, indent=1))


# ---------------------------------------------------------------- HTTP
def ssl_context():
    """Some Python builds (python.org on macOS) ship with an empty CA store, so every HTTPS call fails.
    Fall back to the system store, then certifi. Verification always stays on."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is None:
        _SSL_CONTEXT = ssl.create_default_context()
        if not _SSL_CONTEXT.cert_store_stats().get("x509_ca"):
            for candidate in (os.environ.get("SSL_CERT_FILE"), "/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
                if candidate and Path(candidate).exists():
                    _SSL_CONTEXT = ssl.create_default_context(cafile=candidate)
                    break
            else:
                try:
                    import certifi
                    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
                except ImportError:
                    pass
    return _SSL_CONTEXT


_SSL_CONTEXT = None


def fetch(url, headers=None, attempts=3):
    """GET with backoff. Honors Retry-After; otherwise waits 5 s, then 15 s, with jitter.
    These APIs are free and throttle bursts, so a service that keeps failing is reported, not retried forever."""
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=dict({"User-Agent": USER_AGENT}, **(headers or {})))
            with urllib.request.urlopen(request, timeout=30, context=ssl_context()) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
            retry_after = (exc.headers or {}).get("Retry-After")
            wait = float(retry_after) if (retry_after or "").strip().isdigit() else (5, 15)[attempt]
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == attempts - 1:
                raise
            wait = (3, 9)[attempt]
        time.sleep(wait + random.uniform(0, 1.5))


def fetch_json(url, headers=None):
    return json.loads(fetch(url, headers))


# ---------------------------------------------------------------- services: fetch + parse (parsers are pure)
def parse_arxiv(xml):
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
                "venue": "arXiv preprint",
            })
    return out


def search_arxiv(query, limit):
    terms = " AND ".join("all:%s" % t for t in words(query))
    return parse_arxiv(fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": terms, "max_results": limit, "sortBy": "relevance"})))


def parse_semantic_scholar(data):
    out = []
    for item in data.get("data") or []:
        ext = item.get("externalIds") or {}
        ids = {"s2": item.get("paperId")}
        if ext.get("ArXiv"):
            ids["arxiv"] = ext["ArXiv"]
        if ext.get("DOI"):
            ids["doi"] = ext["DOI"]
        out.append({
            "title": item.get("title") or "", "authors": [a.get("name", "") for a in item.get("authors") or []],
            "year": item.get("year"), "ids": ids, "url": item.get("url") or "",
            "abstract": item.get("abstract") or "", "venue": item.get("venue") or "",
        })
    return out


def search_semantic_scholar(query, limit):
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    return parse_semantic_scholar(fetch_json(
        "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode({
            "query": " ".join(words(query)), "limit": limit,
            "fields": "title,year,authors,externalIds,url,abstract,venue"}),
        headers={"x-api-key": key} if key else None))


def parse_crossref(data):
    out = []
    for item in data["message"]["items"]:
        issued = (item.get("issued") or {}).get("date-parts") or [[None]]
        out.append({
            "title": (item.get("title") or [""])[0],
            "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author") or []],
            "year": issued[0][0], "ids": {"doi": item.get("DOI")}, "url": "https://doi.org/" + (item.get("DOI") or ""),
            "abstract": re.sub(r"<[^>]+>", "", item.get("abstract") or ""),
            "venue": (item.get("container-title") or [""])[0],
        })
    return out


def search_crossref(query, limit):
    params = {"query.bibliographic": " ".join(words(query)), "rows": limit,
              "select": "DOI,title,author,issued,container-title,abstract"}
    if os.environ.get("CROSSREF_MAILTO"):
        params["mailto"] = os.environ["CROSSREF_MAILTO"]
    return parse_crossref(fetch_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params)))


def openalex_abstract(inverted):
    """OpenAlex ships abstracts as {word: [positions]}; put the words back in order."""
    if not inverted:
        return ""
    positions = [(p, word) for word, spots in inverted.items() for p in spots]
    return " ".join(word for _, word in sorted(positions))


def parse_openalex(data):
    out = []
    for item in data.get("results") or []:
        doi = (item.get("doi") or "").replace("https://doi.org/", "")
        ids = {"openalex": (item.get("id") or "").rsplit("/", 1)[-1]}
        if doi:
            ids["doi"] = doi
        location = (item.get("primary_location") or {}).get("source") or {}
        out.append({
            "title": item.get("display_name") or item.get("title") or "",
            "authors": [(a.get("author") or {}).get("display_name", "") for a in item.get("authorships") or []],
            "year": item.get("publication_year"), "ids": ids,
            "url": "https://doi.org/" + doi if doi else (item.get("id") or ""),
            "abstract": openalex_abstract(item.get("abstract_inverted_index")),
            "venue": location.get("display_name") or "",
        })
    return out


def search_openalex(query, limit):
    params = {"search": " ".join(words(query)), "per-page": limit}
    if os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = os.environ["OPENALEX_MAILTO"]
    return parse_openalex(fetch_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))



SERVICES = {"openalex": search_openalex, "crossref": search_crossref, "arxiv": search_arxiv,
            "semanticscholar": search_semantic_scholar}
PAUSE = {"arxiv": 3.0}  # seconds to wait after a call; arXiv throttles hardest
# DBLP is not included: its search API sits behind an anti-bot page that returns HTML, not JSON.


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


def run_searches(queries, services, limit, use_cache=True, ttl_days=CACHE_TTL_DAYS, cache_dir=None):
    """Returns (records, per-service status). Cached results cost nothing; only failures are retried."""
    status = {name: {"ok": 0, "cached": 0, "errors": []} for name in services}
    raw = []
    for query in queries:
        for name in services:
            found = cache_read(name, query, limit, ttl_days, cache_dir) if use_cache else None
            if found is not None:
                status[name]["ok"] += 1
                status[name]["cached"] += 1
            else:
                try:
                    found = SERVICES[name](query, limit)
                    status[name]["ok"] += 1
                    if use_cache:
                        cache_write(name, query, limit, found, cache_dir)
                except Exception as exc:  # failures are reported, never hidden, and never cached
                    status[name]["errors"].append("%r: %s" % (query, getattr(exc, "code", type(exc).__name__)))
                    continue
                time.sleep(PAUSE.get(name, 1.0))
            for rec in found:
                rec = dict(rec, found_in=[name], query=query)
                raw.append(rec)
    return sorted(merge(raw), key=lambda r: (-len(r["found_in"]), -(r.get("year") or 0))), status


def report_markdown(queries, records, status):
    lines = ["# Literature search", "", "**Queries (keywords only):** " + "; ".join("`%s`" % q for q in queries), "",
             "| Service | Queries answered | From cache | Errors |", "|---|---|---|---|"]
    lines += ["| %s | %d/%d | %d | %s |" % (name, s["ok"], len(queries), s["cached"], "; ".join(s["errors"]) or "none")
              for name, s in status.items()]
    lines += ["", "| Title | Year | First author | IDs | Found in |", "|---|---|---|---|---|"]
    for r in records:
        ids = ", ".join("%s:%s" % (k, v) for k, v in r["ids"].items() if v and k not in ("s2", "openalex", "dblp")) \
            or ", ".join("%s:%s" % (k, v) for k, v in r["ids"].items() if v)
        lines.append("| [%s](%s) | %s | %s | %s | %s |" % (
            r["title"].replace("|", "/")[:90], r["url"], r.get("year") or "",
            (r["authors"] or [""])[0], ids, ", ".join(r["found_in"])))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("queries", nargs="+")
    parser.add_argument("--guard-text", nargs="*", default=[], help="unpublished draft files/folders queries must not quote")
    parser.add_argument("--services", default=DEFAULT_SERVICES, help="comma-separated: " + ", ".join(SERVICES))
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--no-cache", action="store_true", help="ignore and do not write the cache")
    parser.add_argument("--cache-ttl", type=float, default=CACHE_TTL_DAYS, help="days a cached result stays usable")
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, help="write <out>.json and <out>.md")
    args = parser.parse_args()

    services = [s.strip() for s in args.services.split(",") if s.strip()]
    unknown = [s for s in services if s not in SERVICES]
    if unknown:
        sys.exit("unknown service(s): %s; available: %s" % (", ".join(unknown), ", ".join(SERVICES)))

    shingles = guard_shingles(args.guard_text)
    for query in args.queries:
        problem = check_query(query, shingles)
        if problem:
            print("REFUSED %r: %s" % (query, problem), file=sys.stderr)
            sys.exit(2)

    records, status = run_searches(args.queries, services, args.limit,
                                   use_cache=not args.no_cache, ttl_days=args.cache_ttl, cache_dir=args.cache_dir)
    markdown = report_markdown(args.queries, records, status)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".json").write_text(json.dumps(
            {"queries": args.queries, "services": status, "records": records}, indent=2))
        args.out.with_suffix(".md").write_text(markdown)
    print(markdown)
    if all(s["ok"] == 0 for s in status.values()):
        sys.exit(3)  # every service failed: the caller must label the group "unverified (search failed)"


if __name__ == "__main__":
    main()
