#!/usr/bin/env python3
"""Check a career-fit report (careers.md) before the person sees it.

    python3 check_careers.py ~/researcher-pal/career/careers.md

Checks: the report is dated; every section is there; each ikigai circle cites evidence; every company and role cites
at least one source; every company's openings line cites a posting or says none was found; every best-fit pick names a
real company and role, cites evidence about the person and gives a next step; every cited source is listed with a URL
and the date it was read. Prints a Markdown report. Exit code 1 if any check FAILs. Standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

RESULTS = []
SECTIONS = ["Ikigai", "Best fit", "Companies you'd love to work at", "Roles you'd love", "Sources"]
CIRCLES = ["What you love", "What you're good at", "What the world needs", "What you can be paid for"]
PERSON = re.compile(r"\[(profile|library: [^\]]+|kg: [^\]]+)\]")
SOURCE = re.compile(r"\[(S\d+)\]")


def record(status, check, detail=""):
    RESULTS.append((status, check, detail))


def summarize(items, limit=6):
    items = list(items)
    return "; ".join(items[:limit]) + (" (+%d more)" % (len(items) - limit) if len(items) > limit else "")


def sections(text):
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def entries(body, prefix):
    """{id: (name, text)} for '### C1: Name' style entries."""
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    found = {}
    for i in range(1, len(parts) - 1, 2):
        match = re.match(r"(%s\d+)\s*:\s*(.+)" % prefix, parts[i].strip())
        if match:
            found[match.group(1)] = (match.group(2), parts[i + 1])
    return found


def check(text):
    dated = re.search(r"As of (\d{4}-\d{2}-\d{2})", text)
    record("PASS" if dated else "FAIL", "dated", "as of %s" % dated.group(1) if dated else
           "no 'As of YYYY-MM-DD' line: openings change weekly, so the report must say when it was made")
    secs = sections(text)
    missing = [s for s in SECTIONS if s not in secs]
    record("FAIL" if missing else "PASS", "sections", ("missing: " + ", ".join("## " + m for m in missing)) if missing
           else "all present")

    # Sources: every ID listed once, with a URL and a read date.
    listed, bad_rows = {}, []
    for row in re.findall(r"^\|\s*(S\d+)\s*\|(.*)$", secs.get("Sources", ""), flags=re.M):
        ident, rest = row
        if ident in listed:
            bad_rows.append("%s listed twice" % ident)
        listed[ident] = rest
        if not re.search(r"https?://\S+", rest):
            bad_rows.append("%s has no URL" % ident)
        if not re.search(r"\d{4}-\d{2}-\d{2}", rest):
            bad_rows.append("%s has no date read" % ident)
    cited = set(SOURCE.findall(text.split("## Sources")[0]))
    undefined = sorted(cited - set(listed), key=lambda s: int(s[1:]))
    unused = sorted(set(listed) - cited, key=lambda s: int(s[1:]))
    record("FAIL" if bad_rows or undefined else "PASS", "sources listed with URL and date",
           summarize(bad_rows + (["cited but not listed: " + ", ".join(undefined)] if undefined else []))
           or "%d sources" % len(listed))
    if unused:
        record("WARN", "unused sources", ", ".join(unused))

    ikigai = secs.get("Ikigai", "")
    weak = []
    for circle in CIRCLES:
        row = re.search(r"^\|\s*%s\s*\|(.*)$" % re.escape(circle), ikigai, flags=re.M)
        if not row:
            weak.append("%s: missing" % circle)
        elif not (PERSON.search(row.group(1)) or SOURCE.search(row.group(1))):
            weak.append("%s: no evidence" % circle)
    record("FAIL" if weak else "PASS", "ikigai circles cite evidence", summarize(weak) or "all four")

    companies = entries(secs.get("Companies you'd love to work at", ""), "C")
    roles = entries(secs.get("Roles you'd love", ""), "R")
    problems = []
    for ident, (name, body) in companies.items():
        if not SOURCE.search(body):
            problems.append("%s %s cites no source" % (ident, name))
        openings = re.search(r"\*\*Openings:\*\*(.*)", body)
        if not openings:
            problems.append("%s %s has no **Openings:** line" % (ident, name))
        elif not (SOURCE.search(openings.group(1)) or re.search(r"no current posting found", openings.group(1), re.I)):
            problems.append("%s %s lists openings without a cited posting" % (ident, name))
    for ident, (name, body) in roles.items():
        if not SOURCE.search(body):
            problems.append("%s %s cites no source" % (ident, name))
    record("FAIL" if problems or not companies or not roles else "PASS", "companies and roles are sourced",
           summarize(problems) or ("no companies or no roles" if not (companies and roles) else
                                   "%d companies, %d roles" % (len(companies), len(roles))))

    picks = re.split(r"^### \d+\.", secs.get("Best fit", ""), flags=re.M)[1:]
    issues = []
    for n, pick in enumerate(picks, 1):
        refs = set(re.findall(r"\b([CR]\d+)\b", pick))
        if not any(r.startswith("C") and r in companies for r in refs):
            issues.append("pick %d names no listed company (C#)" % n)
        if not any(r.startswith("R") and r in roles for r in refs):
            issues.append("pick %d names no listed role (R#)" % n)
        if not PERSON.search(pick):
            issues.append("pick %d cites nothing about you ([profile], [library: …] or [kg: …])" % n)
        if "**Next step:**" not in pick:
            issues.append("pick %d has no next step" % n)
    if not 1 <= len(picks) <= 5:
        issues.append("expected 1-5 best-fit picks, found %d" % len(picks))
    record("FAIL" if issues else "PASS", "best-fit picks", summarize(issues) or "%d picks" % len(picks))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    if not args.report.exists():
        sys.exit("no such report: %s" % args.report)
    check(args.report.read_text())
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
    print("| | Check | Detail |\n|---|---|---|\n" + "\n".join(
        "| %s %s | %s | %s |" % (icon[s], s, c, d.replace("|", "\\|")) for s, c, d in RESULTS))
    sys.exit(1 if any(s == "FAIL" for s, _, _ in RESULTS) else 0)


if __name__ == "__main__":
    main()
