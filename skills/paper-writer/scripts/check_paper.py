#!/usr/bin/env python3
"""Venue-readiness checks for a paper compiled with Tectonic.

    python3 check_paper.py paper/<slug>/<venue> --main main.tex --page-limit 9 --anonymous \
        --author "Jane Doe" --author "Example University" [--verify-citations] [--report checks.md]

    # verify any .bib file on its own (e.g. the researcher's original one at P6):
    python3 check_paper.py paper/<slug>/<venue> --citations-only --bib inputs/refs.bib --citations-out p6_citations.md

Expects the paper folder layout from SKILL.md:
    main.tex, sections/*.tex, generated/values.tex, figures/*.pdf, refs.bib, sources.md
with the figure scripts in <venue>/figures/scripts/ or, shared by every venue, <paper>/figures_scripts/
and a compile with intermediates kept:
    tectonic main.tex --keep-logs --keep-intermediates
Put \\label{pw:mainend} at the end of the page-limited main text (before statements or references that
don't count), so the page count comes from where the main text really ends.

Citation checks use the arXiv API, doi.org content negotiation (Crossref and DataCite DOIs, including
arXiv's 10.48550 DOIs) and Crossref title search. An entry is "verified" only when a record's title matches
and its first author's surname is among the record's authors; lookups that fail are "not verified", never
guessed.

Prints a Markdown report. Exit code 1 if any check FAILs. Standard library only.
"""
import argparse
import difflib
import json
import os
import re
import ssl
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

RESULTS = []  # (status, check, detail)
USER_AGENT = "paper-writer-citation-check/1.2 (https://github.com/; citation verification for a local paper draft)"


def record(status, check, detail=""):
    RESULTS.append((status, check, detail))


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


# ---------------------------------------------------------------- compile log and page count
def check_log(paper, main):
    log = paper / (Path(main).stem + ".log")
    if not log.exists():
        record("FAIL", "compile log", "%s not found: compile with --keep-logs --keep-intermediates" % log.name)
        return
    text = log.read_text(errors="replace")
    errors = [line for line in text.splitlines() if line.startswith("! ")]
    record("FAIL" if errors else "PASS", "LaTeX errors", "; ".join(errors[:5]) or "none")
    undefined = sorted(set(re.findall(r"(?:Reference|Citation) `([^']+)' on page \d+ undefined", text)))
    record("FAIL" if undefined else "PASS", "undefined references/citations", ", ".join(undefined) or "none")
    missing = sorted(set(re.findall(r"File `([^']+)' not found", text)))
    record("FAIL" if missing else "PASS", "missing files", ", ".join(missing) or "none")
    substituted = sorted(set(re.findall(r"Font shape `([^']+)' undefined", text)))
    record("FAIL" if substituted else "PASS", "fonts",
           ("substituted: %s. Tectonic runs XeTeX; if the template loads times, add \\usepackage[T1]{fontenc} "
            "in main.tex" % ", ".join(substituted)) if substituted else "no font substitutions")
    overfull = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", text)]
    bad = [x for x in overfull if x > 5]
    record("WARN" if bad else "PASS", "overfull lines > 5pt", "%d (worst %.1fpt)" % (len(bad), max(bad)) if bad else "none")


def check_pages(paper, main, limit):
    aux = paper / (Path(main).stem + ".aux")
    if not aux.exists():
        record("FAIL", "page limit", "%s not found" % aux.name)
        return
    match = re.search(r"\\newlabel\{pw:mainend\}\{\{[^}]*\}\{(\d+)\}", aux.read_text(errors="replace"))
    if not match:
        record("FAIL", "page limit", "no \\label{pw:mainend} at the end of the main text")
        return
    pages = int(match.group(1))
    status = "PASS" if limit is None or pages <= limit else "FAIL"
    record(status, "page limit", "main text ends on page %d (limit %s)" % (pages, limit if limit else "not given"))


# ---------------------------------------------------------------- anonymity
def tex_sources(paper, main):
    files = [paper / main] + sorted((paper / "sections").glob("*.tex"))
    return {f: strip_comments(f.read_text(errors="replace")) for f in files if f.exists()}


def check_anonymity(paper, main, authors):
    sources = tex_sources(paper, main)
    everything = "\n".join(sources.values())
    problems = []
    for name in authors:
        if name.lower() in everything.lower():
            problems.append("'%s' appears in the source" % name)
    for pattern, why in [
        (r"^\s*\\iclrfinalcopy", "\\iclrfinalcopy is active"),
        (r"\\usepackage\[[^\]]*(final|accepted)[^\]]*\]\{(neurips|icml)", "camera-ready package option"),
        (r"\\section\*?\{Acknowledg", "acknowledgements section"),
        (r"\b(our|we)\s+(previous|prior|earlier)\s+(work|paper)", "first-person reference to prior work"),
        (r"github\.com/(?!anonymous)[\w-]+", "non-anonymous GitHub link"),
        (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    ]:
        if re.search(pattern, everything, flags=re.IGNORECASE | re.MULTILINE):
            problems.append(why)
    record("FAIL" if problems else "PASS", "anonymity", "; ".join(problems) or "no identifying text found")


# ---------------------------------------------------------------- numbers must be sourced
NUMBER = re.compile(r"(?<![\w\\{.])(\d{1,3}(?:,\d{3})+|\d+\.\d+|\d{2,})(\s*\\?%)?(?![\w}])")


def prose_only(tex):
    tex = re.sub(r"\\(cite[tp]?|citeauthor|citeyear|ref|cref|Cref|eqref|label|input|include|includegraphics|"
                 r"bibliography|bibliographystyle|url|href|usepackage|documentclass|begin|end|vspace|hspace)"
                 r"\*?(\[[^\]]*\])*\{[^}]*\}", " ", tex)
    tex = re.sub(r"\[[^\]]*(width|height|scale)[^\]]*\]", " ", tex)
    tex = re.sub(r"\{[\d.]+\\(line|text|column)width\}", " ", tex)
    return tex


def check_numbers(paper, main):
    sources_md = paper / "sources.md"
    listed = sources_md.read_text(errors="replace") if sources_md.exists() else ""
    unsourced = []
    for f, tex in tex_sources(paper, main).items():
        if f.name == main:  # preamble/settings; prose lives in sections/
            continue
        for match in NUMBER.finditer(prose_only(tex)):
            literal = match.group(1)
            if re.fullmatch(r"(19|20)\d\d", literal):
                continue  # years
            if literal not in listed:
                unsourced.append("%s: %s" % (f.name, literal + (match.group(2) or "")))
    macros_used = set(re.findall(r"\\(val[A-Za-z]+)", "\n".join(tex_sources(paper, main).values())))
    values = paper / "generated" / "values.tex"
    defined = set(re.findall(r"\\newcommand\{\\(val[A-Za-z]+)\}", values.read_text())) if values.exists() else set()
    undefined = sorted(m for m in macros_used if m not in defined)
    unlisted = sorted(m for m in macros_used if m not in listed)
    record("FAIL" if unsourced else "PASS", "numbers in prose are sourced", "; ".join(unsourced[:15]) or "all listed in sources.md")
    record("FAIL" if undefined or unlisted else "PASS", "value macros",
           ("undefined: %s " % ", ".join(undefined) if undefined else "") +
           ("missing from sources.md: %s" % ", ".join(unlisted) if unlisted else "") or "%d macros, all defined and listed" % len(macros_used))


def check_todos(paper, main):
    files = {paper / main} | set((paper / "sections").glob("*.tex")) | set(paper.glob("*.tex"))
    todos = []
    for f in sorted(files):
        if not f.exists():
            continue
        text = strip_comments(f.read_text(errors="replace"))
        todos += ["%s: %s" % (f.name, t[:70]) for t in re.findall(r"\\TODO\{([^}]*)\}", text)]
        todos += ["%s: unanswered checklist item" % f.name for _ in re.findall(r"\\answerTODO\{\}", text)]
    record("WARN" if todos else "PASS", "open TODOs", "; ".join(todos) or "none")


# ---------------------------------------------------------------- figures regenerate from scripts
def script_dirs(paper):
    """Per-venue scripts, then scripts shared by every venue of the same paper."""
    return [paper / "figures" / "scripts", paper.parent / "figures_scripts"]


def find_script(paper, stem):
    for directory in script_dirs(paper):
        candidate = directory / (stem + ".py")
        if candidate.exists():
            return candidate
    return None


def check_figures(paper, main):
    everything = "\n".join(tex_sources(paper, main).values())
    problems = []
    for target in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", everything):
        path = paper / target
        if path.suffix == "":
            path = path.with_suffix(".pdf")
        if not path.exists():
            problems.append("%s missing" % target)
        if not find_script(paper, path.stem):
            problems.append("no script %s.py for %s (looked in %s)"
                            % (path.stem, target, " and ".join(str(d.name) for d in script_dirs(paper))))
    record("FAIL" if problems else "PASS", "figures have scripts", "; ".join(problems) or "all figures have a generating script")


# ---------------------------------------------------------------- figures and values match the data
PDF_VOLATILE = [re.compile(rb"/(?:CreationDate|ModDate)\s*\(D:[^)]*\)"), re.compile(rb"/ID\s*\[[^\]]*\]"),
                re.compile(rb"/(?:Producer|Creator)\s*\([^)]*\)"), re.compile(rb"<xmp:(CreateDate|ModifyDate)>[^<]*</xmp:\1>")]


def strip_volatile(data):
    for pattern in PDF_VOLATILE:
        data = pattern.sub(b"", data)
    return data


def stable_bytes(data):
    """File contents with per-run timestamps removed, so two runs of the same script compare equal.
    PDF streams are decompressed first: Cairo (Graphviz, rsvg-convert) hides its /CreationDate inside one."""
    if not data.startswith(b"%PDF"):
        return strip_volatile(data)
    parts, pos = [], 0
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        parts.append(strip_volatile(data[pos:match.start()]))
        try:
            body = zlib.decompress(match.group(1))
        except zlib.error:
            body = match.group(1)
        parts.append(strip_volatile(body))
        pos = match.end()
    parts.append(strip_volatile(data[pos:]))
    return b"".join(parts)


def output_tree(paper):
    """{path: (bytes, stat)} for every file the figure and value scripts may write."""
    files = sorted((paper / "generated").rglob("*")) + sorted((paper / "figures").rglob("*"))
    return {f: (f.read_bytes(), f.stat()) for f in files if f.is_file()}


def compared(tree, paper, figures=True):
    """The outputs the check compares: values and tables, plus the figure PDFs/PNGs unless figures=False."""
    def wanted(f):
        return f.is_relative_to(paper / "generated") or (
            figures and f.parent == paper / "figures" and f.suffix in (".pdf", ".png"))
    return {f: stable_bytes(data) for f, (data, _) in tree.items() if wanted(f)}


def restore_tree(paper, snapshot):
    """Put generated/ and figures/ back exactly as they were, timestamps included, so the check never leaves
    rewritten files behind (or makes a build tool think the paper needs recompiling)."""
    for f in output_tree(paper):
        if f not in snapshot:
            f.unlink()
    for f, (data, st) in snapshot.items():
        if not f.is_file() or f.read_bytes() != data:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns))
    for root in (paper / "generated", paper / "figures"):
        for d in sorted((d for d in root.rglob("*") if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
            if not any(d.iterdir()) and not any(f.is_relative_to(d) for f in snapshot):
                d.rmdir()


def check_regenerated(paper, python=None, compare_figures=True):
    """Re-run the figure and value scripts and compare: the paper's numbers and figures must match the data
    they claim to come from, not merely exist. With compare_figures=False the figures must still rebuild,
    but only the values and tables are compared: figures depend on the machine's fonts, Graphviz and Cairo,
    so a figure built on macOS never matches one built on Linux byte for byte."""
    make_all = find_script(paper, "make_all")
    if make_all is None:
        record("WARN", "figures and values match the data", "no make_all.py found; skipped")
        return
    snapshot = output_tree(paper)
    before = compared(snapshot, paper, compare_figures)
    if not before:
        record("WARN", "figures and values match the data", "nothing generated yet; skipped")
        return
    env = dict(os.environ, SOURCE_DATE_EPOCH="0", VENUE_DIR=str(paper.resolve()), MPLBACKEND="Agg", PYTHONWARNINGS="ignore")
    make_all = make_all.resolve()
    # The scripts write into the paper folder itself (they may find their data relative to where they live, so
    # they can't be pointed at a copy); whatever happens, the folder is restored afterwards.
    try:
        try:
            done = subprocess.run([python or sys.executable, "-W", "ignore", str(make_all), str(paper.resolve())],
                                  cwd=str(make_all.parent), env=env, capture_output=True, text=True, timeout=900)
        except (OSError, subprocess.SubprocessError) as exc:
            record("FAIL", "figures and values match the data", "could not run %s: %s" % (make_all.name, exc))
            return
        if done.returncode != 0:
            tail = (done.stderr or done.stdout or "").strip().splitlines()[-3:]
            record("FAIL", "figures and values match the data", "%s failed: %s" % (make_all.name, " / ".join(tail)))
            return
        after = compared(output_tree(paper), paper, compare_figures)
    finally:
        restore_tree(paper, snapshot)
    changed = sorted(str(f.relative_to(paper)) for f in set(before) | set(after) if before.get(f) != after.get(f))
    record("FAIL" if changed else "PASS", "figures and values match the data",
           ("regenerating changed %d file(s): %s. Either the paper was built from stale data (run %s, then "
            "recompile), or the figures were built by a different Python/matplotlib than %s (pass --python). "
            "The paper's files were left as they were."
            % (len(changed), ", ".join(changed[:6]), make_all.name, Path(python or sys.executable).name)) if changed
           else "%d generated files reproduce exactly from the data%s"
           % (len(after), "" if compare_figures else " (figures rebuilt, not compared: --no-figure-compare)"))


# ---------------------------------------------------------------- citations
def parse_bib(text):
    entries = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        start, depth, i = match.end(), 1, match.end()
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[start:i - 1]
        fields = {}
        for field in re.finditer(r"(\w+)\s*=\s*", body):
            j, value = field.end(), ""
            if j < len(body) and body[j] == "{":
                depth, k = 1, j + 1
                while k < len(body) and depth:
                    depth += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                value = body[j + 1:k - 1]
            elif j < len(body) and body[j] == '"':
                k = body.find('"', j + 1)
                value = body[j + 1:k]
            else:
                value = re.match(r"[^,\n]*", body[j:]).group(0)
            fields.setdefault(field.group(1).lower(), value.strip())
        entries.append((match.group(1).lower(), match.group(2), fields))
    return entries


def ascii_fold(text):
    text = re.sub(r"\\[a-zA-Z]+\s*|[{}\\]", "", text or "")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def norm_title(title):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", ascii_fold(title).lower())).strip()


def title_ratio(a, b):
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio() if a and b else 0.0


def first_author_surname(fields):
    first = ascii_fold(fields.get("author", "")).split(" and ")[0].strip()
    if not first:
        return ""
    return (first.split(",")[0] if "," in first else first.split()[-1]).strip().lower()


_SSL_CONTEXT = None


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


def fetch(url, headers=None, attempts=4):
    """GET with backoff on rate limits and timeouts."""
    delay = 3.0
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=dict({"User-Agent": USER_AGENT}, **(headers or {})))
            with urllib.request.urlopen(request, timeout=30, context=ssl_context()) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == attempts - 1:
                raise
        time.sleep(delay)
        delay *= 2


def arxiv_id(fields):
    eprint = fields.get("eprint", "")
    if not eprint:
        match = re.search(r"arxiv\.org/(?:abs|pdf)/([\w./-]+?)(?:v\d+)?(?:\.pdf)?$", fields.get("url", ""))
        eprint = match.group(1) if match else ""
    return re.sub(r"v\d+$", "", eprint.strip())


def arxiv_records(ids):
    """One batched arXiv API request. Returns {id: (title, [author surnames])}."""
    if not ids:
        return {}
    xml = fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"id_list": ",".join(ids), "max_results": len(ids)}))
    records = {}
    for entry in xml.split("<entry>")[1:]:
        found_id = re.search(r"<id>https?://arxiv\.org/abs/([^<]+?)(?:v\d+)?</id>", entry)
        found_title = re.search(r"<title>(.*?)</title>", entry, flags=re.S)
        names = re.findall(r"<name>(.*?)</name>", entry)
        if found_id and found_title:
            records[found_id.group(1)] = (re.sub(r"\s+", " ", found_title.group(1)).strip(),
                                          [ascii_fold(n).split()[-1].lower() for n in names if n.split()])
    return records


def doi_record(doi):
    """(title, [author surnames]) via doi.org content negotiation; works for Crossref and DataCite DOIs."""
    data = json.loads(fetch("https://doi.org/" + urllib.parse.quote(doi, safe="/"),
                            headers={"Accept": "application/vnd.citationstyles.csl+json"}))
    title = data.get("title")
    if isinstance(title, list):
        title = title[0] if title else None
    return title, [ascii_fold(a.get("family", "")).lower() for a in data.get("author", []) if isinstance(a, dict)]


def crossref_search(fields):
    """Best of the top 5 Crossref title matches: (title, [author surnames])."""
    query = urllib.parse.urlencode({"query.bibliographic": fields["title"], "rows": 5})
    items = json.loads(fetch("https://api.crossref.org/works?" + query))["message"]["items"]
    best = max(items, key=lambda item: title_ratio(fields["title"], (item.get("title") or [""])[0]), default=None)
    if best is None:
        return None, []
    return (best.get("title") or [None])[0], [ascii_fold(a.get("family", "")).lower() for a in best.get("author", [])]


def verify_bib(bib_path, out_path):
    entries = parse_bib(bib_path.read_text(errors="replace"))
    ids = sorted({arxiv_id(f) for _, _, f in entries if arxiv_id(f)})
    try:
        by_id, arxiv_note = arxiv_records(ids), ""
    except Exception as exc:  # fall back per entry below; never hidden
        by_id, arxiv_note = {}, "arXiv API unavailable (%s)" % getattr(exc, "code", type(exc).__name__)
    lines, flagged = [], []
    for _, key, fields in entries:
        ident, doi, notes, candidates = arxiv_id(fields), fields.get("doi"), [], []
        if ident:
            if ident in by_id:
                candidates.append(("arXiv:" + ident,) + by_id[ident])
            else:
                if arxiv_note:
                    notes.append(arxiv_note)
                try:
                    candidates.append(("doi.org 10.48550/arXiv." + ident,) + doi_record("10.48550/arXiv." + ident))
                except Exception as exc:
                    notes.append("arXiv DOI lookup failed (%s)" % getattr(exc, "code", type(exc).__name__))
        if doi:
            try:
                candidates.append(("doi.org " + doi,) + doi_record(doi))
            except Exception as exc:
                notes.append("DOI lookup failed (%s)" % getattr(exc, "code", type(exc).__name__))
        if not ident and not doi and fields.get("title"):
            try:
                candidates.append(("Crossref title search",) + crossref_search(fields))
            except Exception as exc:
                notes.append("Crossref search failed (%s)" % getattr(exc, "code", type(exc).__name__))
        time.sleep(0.5)

        surname = first_author_surname(fields)
        best = max(candidates, key=lambda c: title_ratio(fields.get("title"), c[1]), default=None)
        if best is None or not best[1]:
            status, source, found, ratio = "**NOT VERIFIED**", "; ".join(notes) or "no identifier or title", "—", 0.0
        else:
            source, found, surnames = best
            ratio = title_ratio(fields.get("title"), found)
            author_ok = not surnames or not surname or surname in surnames
            if ratio >= 0.9 and author_ok:
                status = "verified"
            elif ratio >= 0.9:
                status = "**MISMATCH** (first author %r not in record)" % surname
            else:
                status = "**MISMATCH** (title)"
            if notes:
                source += " (%s)" % "; ".join(notes)
        if status != "verified":
            flagged.append(key)
        lines.append("| `%s` | %s | %s | %s | %.2f | %s |" % (
            key, fields.get("title", "")[:60], source, (found or "—")[:60], ratio, status))
    out_path.write_text(
        "# Citation verification: `%s`\n\n| Key | Title in .bib | Checked against | Title found | Match | Status |\n"
        "|---|---|---|---|---|---|\n%s\n" % (bib_path.name, "\n".join(lines)))
    return entries, flagged


def check_citations(paper, verify, bib=None, out=None):
    bib = bib or paper / "refs.bib"
    if not bib.exists():
        record("WARN", "citations", "%s not found" % bib)
        return
    if not verify:
        record("PASS", "citations", "%d entries (run with --verify-citations to check them online)" % len(parse_bib(bib.read_text())))
        return
    out = out or paper / "citations_verification.md"
    entries, flagged = verify_bib(bib, out)
    record("FAIL" if flagged else "PASS", "citations verified",
           ("flagged: %s (see %s)" % (", ".join(flagged), out.name)) if flagged else "%d/%d verified" % (len(entries), len(entries)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paper", type=Path)
    parser.add_argument("--main", default="main.tex")
    parser.add_argument("--page-limit", type=int)
    parser.add_argument("--anonymous", action="store_true")
    parser.add_argument("--author", action="append", default=[], help="name, affiliation or email that must not appear")
    parser.add_argument("--verify-citations", action="store_true")
    parser.add_argument("--regenerate", action="store_true",
                        help="re-run the figure and value scripts and fail if anything changes (the real check "
                             "that the paper matches its data; needs the scripts' dependencies installed)")
    parser.add_argument("--python", help="interpreter that builds the figures (default: the one running this "
                                         "script). Use the project's, or matplotlib versions will differ.")
    parser.add_argument("--no-figure-compare", action="store_true",
                        help="with --regenerate: rebuild the figures but compare only values and tables, for a "
                             "machine other than the one that built the figures (e.g. CI on Linux)")
    parser.add_argument("--citations-only", action="store_true", help="only verify the .bib file")
    parser.add_argument("--bib", type=Path, help="bib file to verify (default: <paper>/refs.bib)")
    parser.add_argument("--citations-out", type=Path, help="where to write the verification table")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.citations_only:
        check_citations(args.paper, True, args.bib, args.citations_out)
    else:
        check_log(args.paper, args.main)
        check_pages(args.paper, args.main, args.page_limit)
        if args.anonymous:
            check_anonymity(args.paper, args.main, args.author)
        check_numbers(args.paper, args.main)
        check_figures(args.paper, args.main)
        if args.regenerate:
            check_regenerated(args.paper, args.python, not args.no_figure_compare)
        check_citations(args.paper, args.verify_citations, args.bib, args.citations_out)
        check_todos(args.paper, args.main)

    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
    report = "| | Check | Detail |\n|---|---|---|\n" + "\n".join(
        "| %s %s | %s | %s |" % (icon[s], s, c, d.replace("|", "\\|")) for s, c, d in RESULTS)
    print(report)
    if args.report:
        args.report.write_text(report + "\n")
    sys.exit(1 if any(s == "FAIL" for s, _, _ in RESULTS) else 0)


if __name__ == "__main__":
    main()
