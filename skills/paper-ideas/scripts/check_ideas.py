"""Check paper-ideas reports (ideas/ideas.md) before the I5 pause.

Checks, per report:
- every idea card has Type, Motivated by, Idea, Literature and Status;
- the ranked table and the cards list the same ideas;
- all four idea types are covered (writing, evidence, reviewer, direction);
- every Literature field starts with an allowed label;
- every cited doi:/arXiv: ID is a verified record, from ideas/literature/*.json or, for a draft, a
  refs.bib next to the ideas folder (the paper's own ID in the title line is ignored);
- every local link resolves.

Usage: python3 check_ideas.py path/to/ideas/ideas.md [more ideas.md ...]
Exit code 0 if every report passes, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

TYPES = {"writing", "evidence", "reviewer", "direction"}
FIELDS = ("**Type:**", "**Motivated by:**", "**Idea:**", "**Literature:**", "**Status:**")
LABELS = (
    "related work",
    "no close match in searched sources (not proof of novelty)",
    "unverified (search failed)",
    "not applicable (presentation)",
)


def verified_ids(base):
    """IDs of verified records: lit_search.py output, plus arXiv IDs and DOIs in the draft's refs.bib files."""
    known = set()
    for path in (base / "literature").glob("*.json"):
        for record in json.loads(path.read_text())["records"]:
            known.update(value.lower() for value in record["ids"].values())
    for bib in base.parent.glob("*/refs.bib"):
        text = bib.read_text()
        known.update(m.lower() for m in re.findall(r"\d{4}\.\d{4,5}", text))
        known.update(m.lower() for m in re.findall(r"doi\s*=\s*[{\"]([^}\"]+)", text, re.I))
    return known


def check(path):
    problems = []
    text = path.read_text()
    base = path.parent

    cards = re.split(r"\n### (?=I-\d\d)", text)[1:]
    if not cards:
        return ["no idea cards found (expected '### I-NN · title')"]
    types = set()
    for card in cards:
        card_id = card[:4]
        missing = [field for field in FIELDS if field not in card]
        if missing:
            problems.append("%s is missing %s" % (card_id, ", ".join(missing)))
            continue
        match = re.search(r"\*\*Type:\*\* (\w+)", card)
        if not match or match.group(1) not in TYPES:
            problems.append("%s has an unknown type" % card_id)
        else:
            types.add(match.group(1))
        literature = card.split("**Literature:**", 1)[1].strip()
        if not literature.startswith(LABELS):
            problems.append("%s literature label must start with one of: %s" % (card_id, "; ".join(LABELS)))

    rows = set(re.findall(r"^\| (I-\d\d) \|", text, re.M))
    card_ids = {card[:4] for card in cards}
    if rows != card_ids:
        problems.append("ranked table and cards differ: only in table %s, only in cards %s"
                        % (sorted(rows - card_ids), sorted(card_ids - rows)))
    if types != TYPES:
        problems.append("idea types not covered: %s" % sorted(TYPES - types))

    own = {m.lower() for m in re.findall(r"(?:doi:|arXiv:)([^\s\]\)]+)", text.splitlines()[0])}
    cited = {m.lower().rstrip(").,") for m in re.findall(r"(?:doi:|arXiv:)([^\s\]\)]+)", text)} - own
    unverified = sorted(cited - verified_ids(base))
    if unverified:
        problems.append("cited IDs that are not verified records: %s" % unverified)

    for link in re.findall(r"\]\(((?!https?:)[^)#\s]+)(?:#[^)]*)?\)", text):
        if not (base / link).exists():
            problems.append("broken link: %s" % link)

    summary = "%d ideas, types %s, %d cited IDs" % (len(cards), ", ".join(sorted(types)), len(cited))
    return problems, summary


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    failed = False
    for arg in sys.argv[1:]:
        result = check(Path(arg))
        problems, summary = result if isinstance(result, tuple) else (result, "")
        if problems:
            failed = True
            print("FAIL %s" % arg)
            for problem in problems:
                print("  - " + problem)
        else:
            print("PASS %s (%s)" % (arg, summary))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
