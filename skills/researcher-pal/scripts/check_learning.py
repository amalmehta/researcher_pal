#!/usr/bin/env python3
"""Check a researcher-pal paper folder before the learner sees it.

    python3 check_learning.py papers/<slug>                  # everything
    python3 check_learning.py papers/<slug> --python python3.9
    python3 check_learning.py papers/<slug> --no-tests       # skip running the exercises' tests
    python3 check_learning.py papers/<slug> --no-run         # skip the tests and the animations

Checks, with no browser needed:
  concept graph  the Mermaid map follows the template's rules (quoted labels, no reserved IDs, defined classes
                 and nodes, balanced subgraphs); every node has an entry and every entry a node; every entry
                 cites the paper and has a valid kind; 🎬 nodes and animation links agree; every link and
                 anchor resolves; the coverage table exists
  animations     each page loads the shared player, loads no scripts but KaTeX, and, run headless with node
                 or macOS's JavaScriptCore, draws every step without an error, never writes NaN/undefined
                 into the drawing, changes between steps, and changes when each slider moves
  exercises      each has a README and either a coded stub + tests + reference solution or a worked problem
                 + reference solution; no solution text leaks into the learner's files; run one exercise at
                 a time, every stub fails its tests (not by crashing) and every solution passes, within the
                 time limits (1 minute; 5 for the final exercise)

Prints a Markdown report. Exit code 1 if any check FAILs. Standard library only.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []  # (status, check, detail)
CITATION = re.compile(r"§|¶|\bEqs?\.|\bEquations?\b|\bFig(ure|s?\.)|\bTables?\b|\bSec(tion|\.)|\bAppendix\b|\bApp\.|"
                      r"\bAlg(orithm|\.)|\bTheorem\b|\bLemma\b|\bProposition\b|\bDefinition\b|\bCorollary\b|"
                      r"\bp\.\s*\d|\bpages?\s+\d|\bE\d+\b|\(\d+\)")
KINDS = {"prerequisite", "core", "novel"}
CLASS_FOR_KIND = {"prerequisite": "prereq", "core": "core", "novel": "novel"}
RESERVED_IDS = {"end", "graph", "subgraph", "style", "class", "click", "flowchart", "classdef", "linkstyle"}


def record(status, check, detail=""):
    RESULTS.append((status, check, detail))


def summarize(items, limit=6):
    items = list(items)
    return "; ".join(items[:limit]) + (" (+%d more)" % (len(items) - limit) if len(items) > limit else "")


# ---------------------------------------------------------------- Markdown structure
def github_anchor(heading):
    """GitHub's heading anchor: lowercase, punctuation (and emoji) dropped, spaces become hyphens."""
    text = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return text.replace(" ", "-")


def anchors(markdown):
    seen, out = {}, set()
    for line in markdown.splitlines():
        match = re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", line)
        if match:
            base = github_anchor(match.group(1))
            count = seen.get(base, 0)
            out.add(base if count == 0 else "%s-%d" % (base, count))
            seen[base] = count + 1
    return out


def strip_code(markdown):
    """Fenced code blocks removed (their headings and links aren't real)."""
    return re.sub(r"^```.*?^```", "", markdown, flags=re.S | re.M)


def sections(markdown):
    """{'## heading text': body} for the level-2 sections."""
    parts = re.split(r"^(## .*)$", markdown, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def entries(concepts_section):
    """[(id, name, body)] for each '### id: Name' entry."""
    found = []
    parts = re.split(r"^### (.*)$", concepts_section, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        heading, body = parts[i].strip(), parts[i + 1]
        match = re.match(r"([A-Za-z_][\w]*)\s*:\s*(.+)", heading)
        found.append((match.group(1), match.group(2), body) if match else (None, heading, body))
    return found


# ---------------------------------------------------------------- Mermaid
ARROW = re.compile(r"\s*(?:-{2,}>|-{3,}|={2,}>|-\.+->|-\.+-|--\s*\|[^|]*\|\s*>?|-->\s*\|[^|]*\|)\s*")


def lint_mermaid(source):
    """Problems with a flowchart, judged by the template's rules. Returns (problems, nodes, edges).
    nodes: {id: (label, class)}; edges: [(from, to)]."""
    problems, nodes, edges = [], {}, []
    class_defs = set()
    depth = 0
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("%%")]
    if not lines or not re.match(r"\s*flowchart\s+TD\b", lines[0]):
        problems.append("the first line should be `flowchart TD`")
    for number, raw in enumerate(lines[1:], 2):
        line = raw.strip()
        where = "line %d" % number
        if line.count('"') % 2:
            problems.append('%s: unbalanced `"` (a quote inside a label? use #quot;)' % where)
        if line.startswith("classDef "):
            class_defs.add(line.split()[1])
            continue
        if re.match(r"(class|style|linkStyle|click)\s", line):
            continue
        if line == "end":
            depth -= 1
            if depth < 0:
                problems.append("%s: `end` without a subgraph" % where)
                depth = 0
            continue
        if line.startswith("subgraph"):
            depth += 1
            line = re.sub(r'^subgraph\s+\w+\s*(\["[^"]*"\])?', "", line).strip()
            if not line:
                continue
        if re.search(r"-{2,}[ox]\w", line):
            problems.append("%s: `--o`/`--x` followed by a name parses as a circle/cross edge; add a space or `>`" % where)
        for label in re.findall(r'"([^"]*)"', line):
            if re.search(r"[<>]", label):
                problems.append("%s: `<` or `>` in a label (write #lt;/#gt; or words): %s" % (where, label))
            if "$" in label or "\\" in label:
                problems.append("%s: LaTeX in a label (write plain text, e.g. sqrt(d_k)): %s" % (where, label))
        # Split an edge line into its node references, then read each one. Labels are set aside first, so an
        # arrow or `&` written inside a label isn't mistaken for syntax.
        labels = re.findall(r'"[^"]*"', line)
        masked = re.sub(r'"[^"]*"', '"@"', line)
        for chunk in re.split(ARROW.pattern + r"|\s*&\s*", masked):
            chunk = chunk.strip()
            while '"@"' in chunk and labels:
                chunk = chunk.replace('"@"', labels.pop(0), 1)
            if not chunk:
                continue
            match = re.match(r'([A-Za-z_]\w*)\s*(?:(\[\[|\[\(|\(\(|\[|\(|\{\{|\{|>)\s*(")?(.*))?$', chunk)
            if not match:
                problems.append("%s: can't read `%s`" % (where, chunk))
                continue
            node_id, opener, quote, rest = match.groups()
            if node_id.lower() in RESERVED_IDS:
                problems.append("%s: `%s` is a reserved word and can't be a node ID" % (where, node_id))
            label, klass = None, None
            if opener:
                if not quote:
                    problems.append('%s: label of `%s` isn\'t in double quotes' % (where, node_id))
                    label = re.sub(r"[\]\)\}]+.*$", "", rest or "")
                else:
                    label = (rest or "").split('"')[0]
            class_match = re.search(r":::(\w+)\s*$", chunk)
            if class_match:
                klass = class_match.group(1)
            if node_id in nodes:
                old_label, old_class = nodes[node_id]
                nodes[node_id] = (old_label if label is None else label, old_class or klass)
            else:
                nodes[node_id] = (label, klass)
        refs = [re.match(r"\s*([A-Za-z_]\w*)", c).group(1) for c in ARROW.split(masked) if re.match(r"\s*[A-Za-z_]\w*", c)]
        edges += list(zip(refs, refs[1:]))
    if depth:
        problems.append("%d subgraph(s) never closed with `end`" % depth)
    for node_id, (label, klass) in nodes.items():
        if klass and klass not in class_defs:
            problems.append("`%s` uses class `%s`, which has no classDef" % (node_id, klass))
        if label is None:
            problems.append("`%s` appears only in an edge, never defined with a label (a typo?)" % node_id)
    return problems, nodes, edges


# ---------------------------------------------------------------- concept graph
def check_concept_graph(paper):
    path = paper / "concept_graph.md"
    if not path.exists():
        record("FAIL", "concept graph", "concept_graph.md not found")
        return None
    text = path.read_text()
    blocks = re.findall(r"^```mermaid\s*\n(.*?)^```", text, flags=re.S | re.M)
    prose = strip_code(text)
    secs = sections(prose)
    missing = [name for name in ("Map", "Coverage", "Concepts") if not any(name in k for k in secs)]
    record("FAIL" if missing else "PASS", "concept graph sections",
           "missing: " + ", ".join("## " + m for m in missing) if missing else "Map, Coverage and Concepts present")

    if len(blocks) != 1:
        record("FAIL", "Mermaid map", "expected one ```mermaid block, found %d" % len(blocks))
        return {"animated_nodes": set(), "text": text}
    problems, nodes, _ = lint_mermaid(blocks[0])
    record("FAIL" if problems else "PASS", "Mermaid map follows the template's rules",
           summarize(problems) or "%d nodes, all labels quoted, classes defined, subgraphs balanced" % len(nodes))

    concepts = next((body for k, body in secs.items() if "Concepts" in k), "")
    items = entries(concepts)
    unreadable = [name for cid, name, _ in items if cid is None]
    ids = [cid for cid, _, _ in items if cid]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    no_node = sorted(set(ids) - set(nodes))
    no_entry = sorted(set(nodes) - set(ids))
    problems = (["headings not in `### id: Name` form: " + summarize(unreadable, 3)] if unreadable else []) + \
               (["duplicate entries: " + ", ".join(duplicates)] if duplicates else []) + \
               (["entries missing from the map: " + ", ".join(no_node)] if no_node else []) + \
               (["map nodes with no entry: " + ", ".join(no_entry)] if no_entry else [])
    record("FAIL" if problems else "PASS", "map and entries match", "; ".join(problems) or "%d concepts, one entry each" % len(ids))

    uncited, bad_kind, mismatched, anim_mismatch = [], [], [], []
    for cid, _, body in items:
        if not cid:
            continue
        source = re.search(r"\*\*Source:\*\*(.*)", body)
        if not source or not CITATION.search(source.group(1)):
            uncited.append(cid)
        kind = re.search(r"\*\*Kind:\*\*\s*([a-z]+)", body)
        if not kind or kind.group(1) not in KINDS:
            bad_kind.append(cid)
        elif cid in nodes:
            klass = nodes[cid][1]
            if klass not in (CLASS_FOR_KIND[kind.group(1)], "known"):
                mismatched.append("%s (%s, drawn as %s)" % (cid, kind.group(1), klass))
        # An entry may point at a neighbour's animation; the concept an animation is named after owns its 🎬.
        links = re.findall(r"\*\*Animation:\*\*.*?\]\(animations/([^)#]+)\.html\)", body)
        has_clapper = cid in nodes and "🎬" in (nodes[cid][0] or "")
        if has_clapper and not links:
            anim_mismatch.append(cid + " has 🎬 in the map but no **Animation:** link")
        if cid in links and not has_clapper:
            anim_mismatch.append(cid + " owns animations/%s.html but its node has no 🎬" % cid)
    record("FAIL" if uncited else "PASS", "every entry cites the paper",
           ("no §/Eq./Fig./Table/¶ citation on the **Source:** line of: " + summarize(uncited)) if uncited
           else "all %d entries cite a section, equation, figure or table" % len(ids))
    record("FAIL" if bad_kind else "PASS", "every entry has a kind",
           ("**Kind:** missing or not prerequisite/core/novel: " + summarize(bad_kind)) if bad_kind else "ok")
    if mismatched:
        record("WARN", "kinds match the map's colors", summarize(mismatched))
    record("FAIL" if anim_mismatch else "PASS", "🎬 marks match animation links", summarize(anim_mismatch) or "ok")

    targets = anchors(prose)
    broken = []
    for target in re.findall(r"\]\(([^)\s]+)\)", prose):
        if re.match(r"[a-z]+://|mailto:", target):
            continue
        file_part, _, fragment = target.partition("#")
        if file_part:
            if not (paper / file_part).exists():
                broken.append(target)
        elif fragment and fragment not in targets:
            broken.append(target)
    for ref in re.findall(r"`(exercises/[^`\s]+?)/?`", prose):
        if not (paper / ref).exists():
            broken.append(ref)
    record("FAIL" if broken else "PASS", "links and anchors resolve", summarize(sorted(set(broken))) or "ok")

    coverage = next((body for k, body in secs.items() if "Coverage" in k), "")
    rows = [l for l in coverage.splitlines() if l.startswith("|") and not re.match(r"\|\s*-", l)][1:]
    record("FAIL" if not rows else "PASS", "coverage table", "%d paper items mapped to concepts" % len(rows) if rows
           else "no coverage table: list every section, equation, figure and table with its concept(s)")
    return {"text": text, "linked_animations": set(re.findall(r"\(animations/([^)#]+\.html)\)", prose))}


# ---------------------------------------------------------------- animations
def js_engine():
    if shutil.which("node"):
        return [shutil.which("node")]
    jsc = Path("/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc")
    return [str(jsc)] if jsc.exists() else None


def run_animation(page, player, engine):
    """Runs animation_check.js over one page. Returns (errors, warnings, info) or raises RuntimeError."""
    html = page.read_text()
    inline = [s for attrs, s in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S) if "src=" not in attrs]
    head, tail = (HERE / "animation_check.js").read_text().split("// @@SPLIT@@")
    program = head + "\n;\n" + "\n;\n".join(inline) + "\n;\n" + player.read_text() + "\n;\n" + tail
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "check.js"
        script.write_text(program)
        done = subprocess.run(engine + [str(script)], capture_output=True, text=True, timeout=120)
    result = re.search(r"^RESULT (.*)$", done.stdout, flags=re.M)
    if not result:
        message = (done.stderr or done.stdout).strip().splitlines()
        raise RuntimeError("the page's script didn't run: " + (message[-1] if message else "no output"))
    data = json.loads(result.group(1))
    return data["errors"], data["warnings"], data


def check_animations(paper, run, linked):
    folder = paper / "animations"
    pages = sorted(p for p in folder.glob("*.html") if not p.name.startswith("_")) if folder.is_dir() else []
    if not pages:
        record("WARN", "animations", "none in animations/ (the skill makes 3-6, or 1-2 for a short paper)")
        return
    orphans = [p.name for p in pages if linked is not None and p.name not in linked]
    record("FAIL" if orphans else "PASS", "every animation is linked from its concept", summarize(orphans) or "%d linked" % len(pages))
    player = folder / "_player.js"
    structure = []
    for page in pages:
        html = page.read_text()
        for shared in ("_player.js", "_player.css"):
            if shared not in html:
                structure.append("%s doesn't load %s" % (page.name, shared))
        for src in re.findall(r'<script[^>]*\bsrc="([^"]+)"', html):
            if src != "_player.js" and not re.match(r"https://cdn\.jsdelivr\.net/npm/katex@", src):
                structure.append("%s loads %s (only KaTeX is allowed)" % (page.name, src))
    for shared in ("_player.js", "_player.css"):
        if not (folder / shared).exists():
            structure.append("animations/%s is missing (copy it from the skill's assets/animation_player.*)" % shared)
    record("FAIL" if structure else "PASS", "animations load the shared player", summarize(structure) or "ok")
    if not run or not player.exists():
        return
    engine = js_engine()
    if engine is None:
        record("WARN", "animations run", "no JavaScript engine (node, or JavaScriptCore on macOS); open each page in a browser instead")
        return
    for page in pages:
        try:
            errors, warnings, info = run_animation(page, player, engine)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            record("FAIL", "animation " + page.name, str(exc))
            continue
        status = "FAIL" if errors else "WARN" if warnings else "PASS"
        note = (" (no paper value, so no reset button: %s)" % ", ".join(info["unpinned"])) if info.get("unpinned") else ""
        record(status, "animation " + page.name, summarize(errors + warnings, 4) or
               "%d steps and %d sliders: every frame draws, steps differ, every slider changes the picture%s"
               % (info["steps"], info["sliders"], note))


# ---------------------------------------------------------------- exercises
def code_lines(text):
    """Lines worth comparing for leaks: long enough to be specific, not comments or docstring boilerplate."""
    out = set()
    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) >= 25 and not stripped.startswith(("#", '"""', "'''", "raise NotImplementedError")):
            out.add(stripped)
    return out


def pytest_status(code):
    return {0: "passed", 1: "failed", 2: "was interrupted", 3: "crashed (internal error)", 4: "was misused (usage error)",
            5: "collected no tests"}.get(code, "exited with %s" % code)


def run_exercise(python, root, name, timeout):
    started = time.time()
    try:
        done = subprocess.run([python, "-m", "pytest", "-q", "-x", name], cwd=str(root), capture_output=True, text=True,
                              timeout=timeout)
        code = done.returncode
    except subprocess.TimeoutExpired:
        code = "timeout"
    return code, time.time() - started


def check_exercises(paper, run, python, graph_text):
    folder = paper / "exercises"
    if not folder.is_dir():
        record("WARN", "exercises", "no exercises/ yet (written at step 6)")
        return
    dirs = sorted(d for d in folder.iterdir() if d.is_dir() and re.match(r"\d\d_", d.name))
    if not dirs:
        record("WARN", "exercises", "exercises/ has no NN_<concept> folders")
        return
    numbers = [int(d.name[:2]) for d in dirs]
    if numbers != list(range(1, len(dirs) + 1)):
        record("WARN", "exercise numbering", "expected 01..%02d in order, found %s" % (len(dirs), ", ".join(d.name[:2] for d in dirs)))
    problems, leaks, coded = [], [], []
    for d in dirs:
        solution_dir = paper / ".solutions" / d.name
        if not (d / "README.md").exists():
            problems.append("%s has no README.md" % d.name)
        if (d / "impl.py").exists():
            coded.append(d.name)
            if not (d / "test_impl.py").exists():
                problems.append("%s has impl.py but no test_impl.py" % d.name)
            solution = solution_dir / "impl.py"
            if not solution.exists():
                problems.append("%s has no reference solution at .solutions/%s/impl.py" % (d.name, d.name))
                continue
            stub_text, solution_text = (d / "impl.py").read_text(), solution.read_text()
            if stub_text == solution_text:
                leaks.append("%s/impl.py is the solution itself" % d.name)
                continue
            readme = (d / "README.md").read_text() if (d / "README.md").exists() else ""
            only_solution = code_lines(solution_text) - code_lines(stub_text)
            in_stub = sorted(l for l in only_solution if l in stub_text)
            # A README may state the names the tests rely on (`self.lut = nn.Embedding(...)`): attribute
            # declarations are the interface, not the answer. Two or more other solution lines are.
            in_readme = sorted(l for l in only_solution if l in readme
                               and not re.fullmatch(r"self\.\w+\s*=\s*[\w.]+\([^()]*\)", l))
            if in_stub:
                leaks.append("%s/impl.py contains solution code: %s" % (d.name, in_stub[0][:70]))
            elif len(in_readme) >= 2:
                leaks.append("%s/README.md contains %d lines of the solution, e.g. %s" % (d.name, len(in_readme), in_readme[0][:60]))
        elif (d / "answer.md").exists():
            solution = solution_dir / "solution.md"
            if not solution.exists():
                problems.append("%s has no reference solution at .solutions/%s/solution.md" % (d.name, d.name))
                continue
            learner = (d / "answer.md").read_text() + ((d / "README.md").read_text() if (d / "README.md").exists() else "")
            leaked = sorted(l for l in code_lines(solution.read_text()) if l in learner)
            if len(leaked) >= 2:
                leaks.append("%s: %d lines of the worked solution in the learner's files, e.g. %s" % (d.name, len(leaked), leaked[0][:60]))
        else:
            problems.append("%s is neither a coded exercise (impl.py) nor a worked problem (answer.md)" % d.name)
        if graph_text is not None and d.name not in graph_text:
            problems.append("%s isn't referenced from any concept's **Exercise:** line" % d.name)
    record("FAIL" if problems else "PASS", "exercise files", summarize(problems) or
           "%d exercises (%d coded), each with a README and a reference solution" % (len(dirs), len(coded)))
    record("FAIL" if leaks else "PASS", "solutions stay hidden", summarize(leaks) or "no solution text in the learner's files")
    if not run or not coded:
        return

    # One exercise at a time: a stub that passes is caught even when the others fail.
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        stubs, solved = Path(tmp) / "stubs", Path(tmp) / "solved"
        ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache")
        shutil.copytree(folder, stubs, ignore=ignore)
        shutil.copytree(folder, solved, ignore=ignore)
        for name in coded:
            solution = paper / ".solutions" / name / "impl.py"
            if solution.exists():
                shutil.copy(solution, solved / name / "impl.py")
        for name in coded:
            limit = 300 if "final" in name else 60
            stub_code, _ = run_exercise(python, stubs, name, timeout=max(120, 2 * limit))
            solved_code, seconds = run_exercise(python, solved, name, timeout=max(600, 2 * limit))
            results.append((name, stub_code, solved_code, seconds, limit))
    bad, slow = [], []
    for name, stub_code, solved_code, seconds, limit in results:
        if stub_code == 0:
            bad.append("%s: the untouched stub passes its tests" % name)
        elif stub_code != 1:
            bad.append("%s: on the stub, pytest %s (a collection error?), so the tests never really ran"
                       % (name, "timed out" if stub_code == "timeout" else pytest_status(stub_code)))
        if solved_code != 0:
            bad.append("%s: %s" % (name, "the reference solution timed out" if solved_code == "timeout"
                                       else "the reference solution fails its tests" if solved_code == 1
                                       else "with the reference solution, pytest " + pytest_status(solved_code)))
        elif seconds > limit:
            slow.append("%s takes %.0fs (limit %ds)" % (name, seconds, limit))
    record("FAIL" if bad else "PASS", "stubs fail, solutions pass", summarize(bad) or
           "%d coded exercises, checked one at a time" % len(results))
    if slow:
        record("WARN", "exercise run time", summarize(slow) + " (on a busy machine, re-run before trusting this)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paper", type=Path, help="papers/<slug>")
    parser.add_argument("--python", default=sys.executable, help="interpreter for the exercises' tests")
    parser.add_argument("--no-tests", action="store_true", help="don't run the exercises' tests")
    parser.add_argument("--no-run", action="store_true", help="don't run the tests or the animations")
    parser.add_argument("--report", type=Path, help="also write the report here")
    args = parser.parse_args()
    if not args.paper.is_dir():
        sys.exit("no such folder: %s" % args.paper)

    graph = check_concept_graph(args.paper)
    check_animations(args.paper, not args.no_run, graph["linked_animations"] if graph and "linked_animations" in graph else None)
    check_exercises(args.paper, not (args.no_run or args.no_tests), args.python, graph["text"] if graph else None)

    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
    report = "| | Check | Detail |\n|---|---|---|\n" + "\n".join(
        "| %s %s | %s | %s |" % (icon[s], s, c, d.replace("|", "\\|")) for s, c, d in RESULTS)
    print(report)
    if args.report:
        args.report.write_text(report + "\n")
    sys.exit(1 if any(s == "FAIL" for s, _, _ in RESULTS) else 0)


if __name__ == "__main__":
    main()
