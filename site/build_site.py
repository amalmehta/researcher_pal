"""Build the Researcher Pal static site from the example outputs in examples/.

    python3.9 site/build_site.py

Writes site/dist/: index.html, anim/ (the animations, with KaTeX switched to cdnjs + MathML so they need no
external stylesheet), img/ and pages/. Needs python-markdown 3.3+.

Preview: run `python3 -m http.server 8765` from the project root and open http://localhost:8765/site/dist/index.html.
Paper page images come from site/assets/pages/ (JPEGs rendered from each venue's main.pdf); refresh them
after the example paper changes.
"""
import html
import re
import shutil
from pathlib import Path

import markdown

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
EX = ROOT / "examples"
DIST = SITE / "dist"
KATEX_JS = "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"
FONTS = ("https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500"
         "&family=Fira+Sans:ital,wght@0,400;0,500;0,600;1,400&family=STIX+Two+Text:ital,wght@0,400;0,600;1,400&display=swap")

PAPERS = {"attention": EX / "attention-is-all-you-need", "ba": EX / "barabasi-albert-scaling"}
TOY = EX / "paper-toy-transformer-ablation" / "paper"

# Documents the site renders, keyed by path, so links between them become in-page routes.
DOCS = {
    PAPERS["attention"] / "concept_graph.md": ("attention", "map"),
    PAPERS["ba"] / "concept_graph.md": ("ba", "map"),
    PAPERS["ba"] / "ideas/ideas.md": ("ba", "ideas"),
    PAPERS["ba"] / "ideas/experiments/01_nonlinear_attachment/findings.md": ("ba", "experiment"),
    TOY / "ideas/ideas.md": ("toy", "ideas"),
    TOY / "ideas/experiments/01_ramp_vs_peak_lr/findings.md": ("toy", "experiment"),
    EX / "knowledge_graph.md": ("graph", "map"),
}
DOCS = {path.resolve(): route for path, route in DOCS.items()}
IMAGES = {(PAPERS["ba"] / "ideas/experiments/01_nonlinear_attachment/results/degree_ccdf.png").resolve(): "img/ba-degree-ccdf.png"}

CASES = [
    {"id": "attention", "group": "learn", "title": "Attention Is All You Need", "ident": "arXiv:1706.03762",
     "byline": "Vaswani et al., 2017", "skills": ["researcher-pal"],
     "summary": "The full machine-learning test run. Every numbered equation and every Section 3.x is mapped to a concept, "
                "four animations cover the ideas that are easiest to misread, and twelve exercises build a Transformer "
                "from scaled dot-product attention up to a model that learns to reverse sequences."},
    {"id": "ba", "group": "learn", "title": "Emergence of Scaling in Random Networks", "ident": "arXiv:cond-mat/9910332",
     "byline": "Barabási & Albert, 1999", "skills": ["researcher-pal", "paper-ideas"],
     "summary": "A light run on a network-science paper, with a worked derivation where there is nothing to code. An "
                "improvement-ideas pass then tested the paper's one-sentence claim that scaling needs linear attachment."},
    {"id": "graph", "group": "learn", "title": "Knowledge graph", "ident": "2 papers",
     "byline": "Topics learned across both runs", "skills": ["researcher-pal"],
     "summary": "One map of what the learner knows, merged across papers. A topic both papers rely on appears once, "
                "with both papers listed."},
    {"id": "toy", "group": "write", "title": "In a Small Transformer, Warmup Matters but Attention Scaling Does Not",
     "short": "Warmup vs. attention scaling", "ident": "Example paper", "byline": "NeurIPS 2026 and ICLR 2027 formats",
     "skills": ["paper-writer", "paper-ideas"],
     "summary": "A 4-page workshop-style paper written from real training runs and simulated researcher notes, compiled "
                "for two venues. A follow-up experiment weakened its original claim that warmup is necessary, and "
                "the title changed with it."},
]

FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*$", re.M | re.S)
CODESPAN = re.compile(r"(``.+?``|`[^`\n]+`)")
DISPLAY_MATH = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE_MATH = re.compile(r"(?<![\\$\w])\$(?=\S)([^$\n]+?)(?<=\S)\$(?![\w$])")


def esc(text):
    return html.escape(text, quote=True)


def route(href, doc_path, case, tab, prefix):
    """Map a Markdown link to an in-page route. Returns (target, external); target None means no page for it."""
    if href.startswith(("http://", "https://", "mailto:")):
        return href, True
    path_part, _, anchor = href.partition("#")
    if not path_part:
        return "#%s/%s/%s--%s" % (case, tab, prefix, anchor), False
    target = (doc_path.parent / path_part).resolve()
    if target in DOCS:
        c, t = DOCS[target]
        return "#%s/%s" % (c, t) + ("/%s-%s--%s" % (c, t, anchor) if anchor else ""), False
    for c, base in PAPERS.items():
        if target.parent == (base / "animations").resolve() and target.suffix == ".html":
            return "#%s/animations/%s-anim-%s" % (c, c, target.stem), False
        exercises = (base / "exercises").resolve()
        if target == exercises:
            return "#%s/exercises" % c, False
        if exercises in target.parents:
            return "#%s/exercises/%s-ex-%s" % (c, c, target.relative_to(exercises).parts[0]), False
    return None, False


def render_md(text, doc_path, case, tab, prefix, strip_h1=False, demote=0):
    stash = []

    def keep(snippet, block=False):
        stash.append(snippet)
        token = "QXSTASH%dQX" % (len(stash) - 1)
        return "\n\n%s\n\n" % token if block else token

    def protect_math(segment):
        parts = CODESPAN.split(segment)
        for i in range(0, len(parts), 2):
            part = DISPLAY_MATH.sub(lambda m: keep('<div class="tex tex-display">%s</div>' % esc(m.group(1).strip()), True), parts[i])
            parts[i] = INLINE_MATH.sub(lambda m: keep('<span class="tex">%s</span>' % esc(m.group(1))), part)
        return "".join(parts)

    if strip_h1:
        text = re.sub(r"\A\s*# [^\n]*\n", "", text)
    # The docs indent nested bullets, tables and images in list items by 2 spaces; python-markdown wants 4.
    text = re.sub(r"^  (?=- |\| |!\[)", "    ", text, flags=re.M)

    out, pos = [], 0
    for m in FENCE.finditer(text):
        out.append(protect_math(text[pos:m.start()]))
        if m.group(1).strip() == "mermaid":
            out.append(keep('<figure class="plate diagram"><pre class="mermaid">%s</pre></figure>'
                            % html.escape(m.group(2), quote=False), True))
        else:
            out.append(m.group(0))
        pos = m.end()
    out.append(protect_math(text[pos:]))

    body = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"]).convert("".join(out))
    body = re.sub(r"<p>\s*QXSTASH(\d+)QX\s*</p>", lambda m: stash[int(m.group(1))], body)
    body = re.sub(r"QXSTASH(\d+)QX", lambda m: stash[int(m.group(1))], body)
    body = re.sub(r'<h([1-6]) id="([^"]+)"', lambda m: '<h%s id="%s--%s"' % (m.group(1), prefix, m.group(2)), body)
    if demote:
        body = re.sub(r"<(/?)h([1-6])", lambda m: "<%sh%d" % (m.group(1), min(6, int(m.group(2)) + demote)), body)

    def fix_link(m):
        target, external = route(html.unescape(m.group(1)), doc_path, case, tab, prefix)
        if target is None:
            return '<span class="xref">%s</span>' % m.group(2)
        extra = ' target="_blank" rel="noopener"' if external else ""
        return '<a href="%s"%s>%s</a>' % (esc(target), extra, m.group(2))

    def fix_image(m):
        new = IMAGES.get((doc_path.parent / html.unescape(m.group(2))).resolve())
        if not new:
            return ""
        return '<img class="plot" alt="%s" src="%s" loading="lazy">' % (m.group(1), new)

    body = re.sub(r'<a href="([^"]*)">(.*?)</a>', fix_link, body, flags=re.S)
    body = re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', fix_image, body)
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return body


def katex_for_artifact(text):
    """The artifact host allows scripts from cdnjs but blocks external stylesheets, so drop KaTeX's CSS and
    render to MathML, which browsers style themselves."""
    text = re.sub(r'\s*<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/katex[^>]*>', "", text)
    text = re.sub(r'<script defer src="https://cdn\.jsdelivr\.net/npm/katex[^"]*"[^>]*></script>',
                  '<script defer src="%s"></script>' % KATEX_JS, text)
    return text.replace("throwOnError: false", 'throwOnError: false, output: "mathml"')


def copy_animation(case, src):
    """One page per animation; the shared player (_player.js/_player.css) is copied once alongside them."""
    for shared in ("_player.js", "_player.css"):
        target = DIST / "anim" / shared
        if not target.exists():
            target.write_text(katex_for_artifact((src.parent / shared).read_text()))
    text = katex_for_artifact(src.read_text())
    assert "jsdelivr" not in text, src
    name = "%s-%s.html" % (case, src.stem)
    (DIST / "anim" / name).write_text(text)
    title = re.search(r"<title>([^<]*)</title>", text).group(1).replace(" · researcher-pal", "")
    return {"id": "%s-anim-%s" % (case, src.stem), "file": "anim/" + name, "title": title,
            "src": str(src.relative_to(ROOT))}


def exercises_html(case, intro):
    items = []
    for readme in sorted((PAPERS[case] / "exercises").glob("*/README.md")):
        name = readme.parent.name
        text = readme.read_text()
        num, title = re.match(r"# (\d+) · ([^\n]+)", text).groups()
        body = render_md(text, readme, case, "exercises", "%s-ex-%s" % (case, name), strip_h1=True, demote=2)
        items.append('<details class="exercise" id="%s-ex-%s"><summary><span class="ex-num">%s</span>'
                     '<span class="ex-title">%s</span></summary><div class="ex-body prose">%s'
                     '<p class="src-path">%s</p></div></details>'
                     % (case, name, num, esc(title), body, esc(str(readme.parent.relative_to(ROOT)) + "/")))
    return len(items), '<div class="prose intro"><p>%s</p></div><div class="exercises">%s</div>' % (intro, "".join(items))


def animations_html(anims):
    intro = ("Interactive pages generated for the ideas that are easiest to misread on paper. Each one has play, "
             "step and scrub controls, keyboard shortcuts, and sliders for its parameters.")
    blocks = ['<div class="prose intro"><p>%s</p></div>' % intro]
    for a in anims:
        blocks.append('<section class="anim-block" id="%s"><h2 class="block-title">%s</h2>'
                      '<iframe class="anim" data-src="%s" title="%s"></iframe><p class="src-path">%s</p></section>'
                      % (a["id"], esc(a["title"]), a["file"], esc(a["title"]), esc(a["src"])))
    return "".join(blocks)


def doc_html(path, strip_h1=True, demote=0):
    case, tab = DOCS[path.resolve()]
    return '<div class="prose">%s</div>' % render_md(path.read_text(), path.resolve(), case, tab, "%s-%s" % (case, tab),
                                                     strip_h1=strip_h1, demote=demote)


def paper_html(pages):
    venues = [
        ("neurips", "NeurIPS 2026", "neurips2026", ["Anonymized submission", "Main text ends on page 4 of 4",
                                                    "6/6 citations verified", "Checklist pages 5–11 not shown"]),
        ("iclr", "ICLR 2027", "iclr2027", ["Anonymized submission", "Main text ends on page 4",
                                           "6/6 citations verified", "AI-use and reproducibility statements included"]),
    ]
    intro = ("Pages of the two compiled PDFs. The researcher's notes, rough draft and .bib are simulated; the results "
             "are real runs of the Attention example's code. Every number in the text comes from a generated macro "
             "traced in <code>sources.md</code>, and every figure is regenerated by its script.")
    blocks = ['<div class="prose intro"><p>%s</p></div>' % intro]
    for key, name, folder, facts in venues:
        figures = "".join('<figure class="page"><img src="pages/%s" alt="%s, page %s" width="918" height="1188" loading="lazy">'
                          '<figcaption>p. %s</figcaption></figure>' % (p.name, name, n, n)
                          for p, n in pages if p.name.startswith(key + "-"))
        blocks.append('<section class="venue"><h2 class="block-title">%s</h2><ul class="facts">%s</ul>'
                      '<div class="pages">%s</div><p class="src-path">%s</p></section>'
                      % (name, "".join("<li>%s</li>" % esc(f) for f in facts), figures,
                         esc(str((TOY / folder / "main.pdf").relative_to(ROOT)))))
    return "".join(blocks)


def case_section(case, tabs):
    links = "".join('<a role="tab" href="#%s/%s" data-tab="%s" aria-selected="false">%s%s</a>'
                    % (case["id"], tab, tab, esc(label), '<span class="count">%d</span>' % n if n else "")
                    for tab, label, n, _ in tabs)
    panels = "".join('<div class="panel" role="tabpanel" data-tab="%s">%s</div>' % (tab, inner) for tab, _, _, inner in tabs)
    skills = "".join('<span class="skill">%s</span>' % s for s in case["skills"])
    return ('<section class="case" id="case-%s" data-case="%s"><header class="case-head"><p class="ident">%s</p>'
            '<h1>%s</h1><p class="byline"><span>%s</span>%s</p><p class="summary">%s</p></header>'
            '<nav class="tabs" role="tablist" aria-label="%s">%s</nav><div class="panels">%s</div></section>'
            % (case["id"], case["id"], esc(case["ident"]), esc(case["title"]), esc(case["byline"]), skills,
               esc(case["summary"]), esc(case["title"]), links, panels))


HOME = """
<section class="case is-active" id="case-home" data-case="home">
  <header class="hero">
    <div class="hero-text">
      <p class="eyebrow">Claude Code skills · example outputs</p>
      <h1>Researcher Pal</h1>
      <p class="lede">Learn a paper by rebuilding it, write your own to a venue's rules, and turn a reviewer's
      doubts into experiments. Everything on this site was produced by the example runs in <code>examples/</code>.</p>
    </div>
    <figure class="fig">
      <iframe class="anim" src="anim/attention-sdpa.html" title="Scaled dot-product attention, step by step"></iframe>
      <figcaption><span class="fig-label">Figure 1.</span> Scaled dot-product attention, step by step: one of the six
      animations researcher-pal generated. Press play, step through it, or drag the sliders.
      <a href="#attention/animations">All animations</a></figcaption>
    </figure>
  </header>

  <section class="home-section" aria-labelledby="skills-title">
    <h2 class="section-title" id="skills-title">Three skills</h2>
    <dl class="skill-list">
      <dt><span class="skill-name">researcher-pal</span><span class="skill-role">Learn a paper</span></dt>
      <dd><p>Maps the paper's concepts and their prerequisites, animates the hardest ideas, and sets exercises that
      rebuild the method: coded where the field allows, worked problems where it doesn't. What you learn joins one
      knowledge graph across papers.</p>
      <p class="say">Say <q>help me learn arXiv 1706.03762</q> · Examples: <a href="#attention">Attention</a>,
      <a href="#ba">Barabási–Albert</a>, <a href="#graph">knowledge graph</a></p></dd>
      <dt><span class="skill-name">paper-writer</span><span class="skill-role">Write a paper</span></dt>
      <dd><p>Turns your results, notes, code and draft into a paper for a specific venue: its template, page limit and
      checklist, figures and tables generated from your data, every number traced to its source, and citations
      checked against arXiv and Crossref.</p>
      <p class="say">Say <q>help me write my paper for NeurIPS</q> · Example: <a href="#toy/paper">the warmup paper</a></p></dd>
      <dt><span class="skill-name">paper-ideas</span><span class="skill-role">Improve a paper</span></dt>
      <dd><p>Ranks ideas of four kinds (writing, missing evidence, reviewer objections, new directions), checks each
      against the literature with keyword-only searches, and with your approval applies edits or runs experiments
      within a compute budget.</p>
      <p class="say">Say <q>suggest improvements for my paper</q> · Examples: <a href="#toy/ideas">own draft</a>,
      <a href="#ba/ideas">learned paper</a></p></dd>
    </dl>
  </section>

  <section class="home-section" aria-labelledby="checks-title">
    <h2 class="section-title" id="checks-title">What was checked</h2>
    <div class="table-wrap">
      <table class="ledger">
        <thead><tr><th scope="col">Output</th><th scope="col">Check</th><th scope="col">Status</th></tr></thead>
        <tbody>
          <tr><td><a href="#attention/exercises">Attention exercises</a></td><td>pytest fails on every stub; 66 tests pass on the reference solutions</td><td><span class="pill pass">Pass</span></td></tr>
          <tr><td><a href="#ba/exercises">Barabási–Albert exercises</a></td><td>coded exercises fail on stubs and pass on solutions; one worked problem</td><td><span class="pill pass">Pass</span></td></tr>
          <tr><td><a href="#toy/paper">NeurIPS 2026 PDF</a></td><td>compiles; main text ends on page 4 of 4; anonymized; 6/6 citations verified</td><td><span class="pill pass">Pass</span></td></tr>
          <tr><td><a href="#toy/paper">ICLR 2027 PDF</a></td><td>compiles; main text ends on page 4; anonymized; 6/6 citations verified</td><td><span class="pill pass">Pass</span></td></tr>
          <tr><td><a href="#toy/ideas">Ideas reports</a></td><td>12 and 11 ideas; all four types; every cited ID a verified record</td><td><span class="pill pass">Pass</span></td></tr>
          <tr><td><a href="#toy/experiment">Warmup experiment</a></td><td>6 runs in 1,479 s (budget 1,800 s); weakened a claim, and the revision was kept</td><td><span class="pill pass">Done</span></td></tr>
          <tr><td><a href="#ba/experiment">Attachment experiment</a></td><td>9 runs in 69 s; consistent with the paper</td><td><span class="pill pass">Done</span></td></tr>
          <tr><td>Skill triggers</td><td>needs a fresh Claude Code session to test the three phrases above</td><td><span class="pill wait">Awaiting you</span></td></tr>
        </tbody>
      </table>
    </div>
  </section>
</section>
"""

PAGE = r"""<meta charset="utf-8">
<title>Researcher Pal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="@@FONTS@@">
<style>
:root {
  --ground: #0E1013; --panel: #171A1F; --panel-2: #1F242B; --rule: #2A2F37; --ink: #ECE8DF; --dim: #9AA1A9;
  --link: #58C4DD; --mark: #F4D35E; --mark-ink: #16181B; --good: #83C167; --bad: #FC6255;
  --plate: #F5F4F0; --plate-ink: #16181B; --plate-rule: #D9D7CF; --code: #1C2026;
  --serif: "STIX Two Text", "STIX Two", "Times New Roman", Georgia, serif;
  --sans: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --mono: "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color-scheme: dark;
}
@media (prefers-color-scheme: light) {
  :root:not([data-theme="dark"]) {
    --ground: #F2F4F5; --panel: #FFFFFF; --panel-2: #E4E9EC; --rule: #D2D8DC; --ink: #15181C; --dim: #56606A;
    --link: #0F7490; --mark: #F4D35E; --mark-ink: #16181B; --good: #3A7A28; --bad: #B5382A;
    --plate: #FFFFFF; --plate-ink: #16181B; --plate-rule: #D2D8DC; --code: #E4E9EC;
    color-scheme: light;
  }
}
:root[data-theme="light"] {
  --ground: #F2F4F5; --panel: #FFFFFF; --panel-2: #E4E9EC; --rule: #D2D8DC; --ink: #15181C; --dim: #56606A;
  --link: #0F7490; --mark: #F4D35E; --mark-ink: #16181B; --good: #3A7A28; --bad: #B5382A;
  --plate: #FFFFFF; --plate-ink: #16181B; --plate-rule: #D2D8DC; --code: #E4E9EC;
  color-scheme: light;
}

*, *::before, *::after { box-sizing: border-box; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
body { margin: 0; background: var(--ground); color: var(--ink); font: 16px/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
a { color: var(--link); text-decoration-thickness: 1px; text-underline-offset: .18em; }
a:hover { text-decoration-thickness: 2px; }
:focus-visible { outline: 2px solid var(--mark); outline-offset: 2px; border-radius: 2px; }
code, pre { font-family: var(--mono); font-size: .86em; }

.shell { display: grid; grid-template-columns: 16.5rem minmax(0, 1fr); gap: clamp(28px, 4vw, 60px); max-width: 90rem; margin: 0 auto; padding-inline: 24px; }

/* Contents rail */
.rail { position: sticky; top: 0; align-self: start; max-height: 100vh; overflow-y: auto; padding-block: 32px; display: flex; flex-direction: column; gap: 26px; }
.brand { font: 600 1.5rem/1.1 var(--serif); color: var(--ink); text-decoration: none; }
.rail-note { margin: 6px 0 0; color: var(--dim); font-size: .8125rem; }
.rail nav { display: flex; flex-direction: column; gap: 22px; }
.rail-group { display: flex; flex-direction: column; gap: 6px; }
.rail-label { margin: 0; font-size: .6875rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--dim); }
.rail ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
.rail li a { display: flex; flex-direction: column; gap: 1px; padding: 8px 10px; margin-inline: -10px; border-radius: 6px; color: var(--ink); text-decoration: none; }
.rail li a:hover { background: var(--panel); }
.rail li a[aria-current="page"] { background: var(--panel-2); }
.rail-title { font-size: .9375rem; line-height: 1.3; font-weight: 500; }
.rail-id { font: .75rem/1.45 var(--mono); color: var(--dim); }
.rail li a[aria-current="page"] .rail-id { color: var(--link); }
.rail-foot { margin: 0; color: var(--dim); font-size: .75rem; line-height: 1.5; }

main { min-width: 0; position: relative; padding-block: 32px 96px; }
.case:not(.is-active), .panel:not(.is-active) { position: absolute; inset-inline-start: -300vw; top: 0; width: 100%; height: 0; overflow: hidden; visibility: hidden; }
.panels { position: relative; }

/* Home */
.hero { display: flex; flex-direction: column; gap: 28px; padding-bottom: 44px; border-bottom: 1px solid var(--rule); }
.eyebrow { margin: 0; font: 500 .75rem/1.4 var(--mono); letter-spacing: .04em; color: var(--dim); }
.hero h1 { margin: .25em 0 0; font: 600 clamp(2.5rem, 5.5vw, 4rem)/1 var(--serif); letter-spacing: -.015em; }
.lede { margin: 18px 0 0; max-width: 58ch; font-size: 1.1875rem; line-height: 1.55; text-wrap: pretty; }
.fig { margin: 0; display: flex; flex-direction: column; gap: 10px; }
iframe.anim { display: block; width: 100%; height: 820px; border: 1px solid var(--rule); border-radius: 10px; background: #0E1013; }
figcaption { font-size: .875rem; color: var(--dim); max-width: 78ch; }
.fig-label { font: 600 1rem var(--serif); color: var(--ink); }
.home-section { padding-block: 44px 4px; }
.section-title, .block-title { margin: 0 0 18px; font: 600 1.75rem/1.2 var(--serif); text-wrap: balance; }
.block-title { font-size: 1.5rem; }
.skill-list { margin: 0; display: grid; grid-template-columns: minmax(0, 13rem) minmax(0, 1fr); column-gap: 32px; }
.skill-list dt, .skill-list dd { margin: 0; padding-block: 18px; border-top: 1px solid var(--rule); }
.skill-name { display: block; font: 500 .875rem/1.4 var(--mono); color: var(--link); }
.skill-role { display: block; margin-top: 2px; font: 400 1.3125rem/1.3 var(--serif); }
.skill-list dd p { margin: 0 0 8px; max-width: 70ch; }
.skill-list dd p:last-child { margin-bottom: 0; }
.say { font-size: .875rem; color: var(--dim); }
.say q { color: var(--ink); font-style: italic; }

/* Tables and status */
.table-wrap { overflow-x: auto; margin-block: 16px; }
table { border-collapse: collapse; width: 100%; font-size: .9375rem; line-height: 1.45; font-variant-numeric: tabular-nums; }
th, td { text-align: left; vertical-align: top; padding: 9px 16px 9px 0; border-bottom: 1px solid var(--rule); }
th { font-size: .75rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--dim); }
td:last-child, th:last-child { padding-right: 0; }
.ledger td:first-child { white-space: nowrap; }
.prose table { min-width: 44rem; }
.prose td:first-child { min-width: 3.6em; }
.pill { display: inline-block; padding: 0 9px; border: 1px solid currentColor; border-radius: 999px; font: 500 .75rem/1.7 var(--mono); white-space: nowrap; }
.pill.pass { color: var(--good); }
.pill.wait { background: var(--mark); border-color: var(--mark); color: var(--mark-ink); }

/* Output pages */
.case-head { display: flex; flex-direction: column; gap: 8px; padding-bottom: 22px; }
.ident { margin: 0; font: 500 .8125rem/1.4 var(--mono); color: var(--link); }
.case-head h1 { margin: 0; max-width: 30ch; font: 600 clamp(1.875rem, 3.6vw, 2.625rem)/1.12 var(--serif); letter-spacing: -.01em; text-wrap: balance; }
.byline { margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; color: var(--dim); font-size: .9375rem; }
.skill { font: .75rem/1.6 var(--mono); color: var(--ink); background: var(--panel-2); padding: 1px 8px; border-radius: 4px; }
.summary { margin: 6px 0 0; max-width: 68ch; font-size: 1.0625rem; text-wrap: pretty; }
.tabs { position: sticky; top: 0; z-index: 2; display: flex; gap: 4px 24px; overflow-x: auto; margin-bottom: 30px; background: var(--ground); border-bottom: 1px solid var(--rule); }
.tabs a { padding: 11px 0 9px; margin-bottom: -1px; border-bottom: 2px solid transparent; color: var(--dim); font-weight: 500; text-decoration: none; white-space: nowrap; }
.tabs a:hover { color: var(--ink); }
.tabs a[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--mark); }
.count { margin-left: 6px; font: .75rem var(--mono); color: var(--dim); }

.prose > :first-child { margin-top: 0; }
.prose p, .prose li, .prose blockquote, .prose h2, .prose h3, .prose h4 { max-width: 72ch; }
.prose [id] { scroll-margin-top: 64px; }
.prose h2 { margin: 2.2em 0 .6em; padding-top: .7em; border-top: 1px solid var(--rule); font: 600 1.625rem/1.25 var(--serif); text-wrap: balance; }
.prose h3 { margin: 2em 0 .5em; font: 600 1.1875rem/1.35 var(--sans); text-wrap: balance; }
.prose h4 { margin: 1.6em 0 .4em; font: 600 1rem/1.4 var(--sans); }
.prose h5, .prose h6 { margin: 1.4em 0 .3em; font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: var(--dim); }
.prose blockquote { margin: 1.2em 0; padding: 2px 0 2px 16px; border-left: 2px solid var(--rule); color: var(--dim); font-size: .9375rem; }
.prose blockquote p { margin: .3em 0; }
.prose code { padding: .1em .35em; border-radius: 4px; background: var(--code); }
.prose pre { padding: 14px 16px; border-radius: 8px; background: var(--code); overflow-x: auto; line-height: 1.5; }
.prose pre code { padding: 0; background: none; }
.prose ul, .prose ol { padding-left: 1.3em; }
.prose li { margin-block: .3em; }
.prose img.plot { display: block; max-width: min(100%, 560px); height: auto; margin-block: 14px; padding: 8px; border-radius: 6px; background: #FFFFFF; }
.intro p { color: var(--dim); }
.plate { margin: 22px 0; padding: 18px; overflow-x: auto; background: var(--plate); color: var(--plate-ink); border: 1px solid var(--plate-rule); border-radius: 8px; }
.plate pre.mermaid { margin: 0; padding: 0; background: none; color: var(--plate-ink); font-size: .75rem; }
.tex { font-family: var(--mono); font-size: .9em; }
.tex.tex-done { font-family: inherit; font-size: inherit; }
.tex-display { margin: 1.1em 0; overflow-x: auto; text-align: center; }
math { font-family: "STIX Two Math", "Cambria Math", math; font-size: 1.08em; }
.src-path { margin: 8px 0 0; font: .75rem/1.5 var(--mono); color: var(--dim); overflow-wrap: anywhere; }

.anim-block + .anim-block, .venue + .venue { margin-top: 52px; }
.exercises { border-bottom: 1px solid var(--rule); }
.exercise { border-top: 1px solid var(--rule); }
.exercise summary { display: flex; align-items: baseline; gap: 14px; padding: 14px 0; cursor: pointer; list-style: none; }
.exercise summary::-webkit-details-marker { display: none; }
.exercise summary::after { content: "+"; margin-left: auto; font-family: var(--mono); color: var(--dim); }
.exercise[open] summary::after { content: "\2212"; }
.ex-num { min-width: 2ch; font: 500 .875rem var(--mono); color: var(--dim); }
.ex-title { font-size: 1.0625rem; font-weight: 500; }
.ex-body { padding: 0 0 24px calc(2ch + 14px); }

.facts { list-style: none; margin: -6px 0 18px; padding: 0; display: flex; flex-wrap: wrap; gap: 4px 20px; color: var(--dim); font-size: .875rem; }
.pages { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 16rem), 1fr)); gap: 22px; }
.page { margin: 0; display: flex; flex-direction: column; gap: 6px; }
.page img { display: block; width: 100%; max-width: 100%; height: auto; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 3px; }
.page figcaption { font: .75rem var(--mono); }

@media (max-width: 960px) {
  .shell { grid-template-columns: minmax(0, 1fr); gap: 0; padding-inline: 16px; }
  .rail { position: static; max-height: none; padding-block: 18px 12px; gap: 12px; border-bottom: 1px solid var(--rule); }
  .rail nav { flex-direction: row; gap: 20px; overflow-x: auto; padding-bottom: 6px; }
  .rail-group { flex: none; }
  .rail ul { flex-direction: row; gap: 4px; }
  .rail li a { margin-inline: 0; width: max-content; max-width: 14rem; }
  .rail-foot { display: none; }
  iframe.anim { height: 1100px; }
}
@media (max-width: 640px) {
  .skill-list { grid-template-columns: minmax(0, 1fr); }
  .skill-list dd { padding-top: 0; border-top: 0; }
  .ex-body { padding-left: 0; }
  .ledger td:first-child { white-space: normal; }
}
</style>

<div class="shell">
  <aside class="rail">
    <div>
      <a class="brand" href="#home">Researcher Pal</a>
      <p class="rail-note">Example outputs · 15 Sep 2026</p>
    </div>
    <nav aria-label="Example outputs">@@RAIL@@</nav>
    <p class="rail-foot">Built from <code>examples/</code> by <code>site/build_site.py</code>.</p>
  </aside>
  <main>
@@HOME@@
@@CASES@@
  </main>
</div>

<script defer src="@@KATEX@@"></script>
<script>
(function () {
  var cases = Array.prototype.slice.call(document.querySelectorAll(".case"));

  function norm(s) { return s.toLowerCase().replace(/[^a-z0-9]/g, ""); }
  function findTarget(id) {
    var el = document.getElementById(id);
    if (el) return el;
    var n = norm(id), all = document.querySelectorAll("[id]");
    for (var i = 0; i < all.length; i++) if (norm(all[i].id) === n) return all[i];
    return null;
  }
  function fit(frame) {
    try {
      var doc = frame.contentDocument;
      if (!doc || !doc.body || !doc.body.children.length) return;
      frame.style.height = "300px";
      frame.style.height = doc.documentElement.scrollHeight + "px";
    } catch (e) { /* cross-origin: keep the CSS height */ }
  }

  function activate() {
    var parts = decodeURIComponent(location.hash.replace(/^#/, "")).split("/");
    var section = document.getElementById("case-" + parts[0]) || document.getElementById("case-home");
    var caseChanged = !section.classList.contains("is-active");
    cases.forEach(function (s) { s.classList.toggle("is-active", s === section); });
    document.querySelectorAll("[data-case-link]").forEach(function (a) {
      if (a.getAttribute("data-case-link") === section.getAttribute("data-case")) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    var panels = Array.prototype.slice.call(section.querySelectorAll(".panel"));
    var panel = panels.filter(function (p) { return p.getAttribute("data-tab") === parts[1]; })[0] || panels[0];
    var tabChanged = !!panel && !panel.classList.contains("is-active");
    panels.forEach(function (p) { p.classList.toggle("is-active", p === panel); });
    section.querySelectorAll(".tabs a").forEach(function (a) {
      a.setAttribute("aria-selected", String(!!panel && a.getAttribute("data-tab") === panel.getAttribute("data-tab")));
    });
    if (panel) panel.querySelectorAll("iframe[data-src]").forEach(function (f) {
      f.src = f.getAttribute("data-src");
      f.removeAttribute("data-src");
    });
    var target = parts[2] ? findTarget(parts[2]) : null;
    if (target) {
      var details = target.closest("details");
      if (details) details.open = true;
      requestAnimationFrame(function () { target.scrollIntoView({ block: "start" }); });
    } else if (caseChanged || tabChanged) {
      window.scrollTo(0, 0);
    }
  }

  document.querySelectorAll("iframe.anim").forEach(function (f) {
    f.addEventListener("load", function () { fit(f); setTimeout(function () { fit(f); }, 600); });
    fit(f);
  });
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { document.querySelectorAll("iframe.anim").forEach(fit); }, 150);
  });
  window.addEventListener("hashchange", activate);
  document.addEventListener("DOMContentLoaded", function () {
    if (!window.katex) return;  /* TeX stays readable as source */
    document.querySelectorAll(".tex").forEach(function (el) {
      try {
        katex.render(el.textContent, el, { displayMode: el.classList.contains("tex-display"), throwOnError: false, output: "mathml" });
        el.classList.add("tex-done");
      } catch (e) { /* leave the source */ }
    });
  });
  activate();
})();
</script>
"""


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    for folder in ("anim", "img", "pages"):
        (DIST / folder).mkdir(parents=True)

    anims = {c: [copy_animation(c, p) for p in sorted((base / "animations").glob("*.html"))] for c, base in PAPERS.items()}
    for src, dst in IMAGES.items():
        shutil.copy(src, DIST / dst)
    pages = []
    for p in sorted((SITE / "assets" / "pages").glob("*.jpg"), key=lambda p: (p.name.split("-p")[0], int(re.search(r"-p(\d+)", p.name).group(1)))):
        shutil.copy(p, DIST / "pages" / p.name)
        pages.append((p, re.search(r"-p(\d+)", p.name).group(1)))
    assert (DIST / "anim" / "attention-sdpa.html").exists()

    def ideas_count(path):
        return len(re.findall(r"^### I-\d\d", path.read_text(), re.M))

    coded = ("Each coded exercise has a README, a stub <code>impl.py</code> and tests: pytest fails on the untouched stub "
             "and passes on the reference solution. The descriptions are below; the code is in <code>%s</code>.")
    n_att, ex_att = exercises_html("attention", coded % "examples/attention-is-all-you-need/exercises/")
    n_ba, ex_ba = exercises_html("ba", (coded % "examples/barabasi-albert-scaling/exercises/")
                                 + " Exercise 02 is a worked derivation, so there is nothing to code.")
    tabs = {
        "attention": [("map", "Concept map", 0, doc_html(PAPERS["attention"] / "concept_graph.md")),
                      ("animations", "Animations", len(anims["attention"]), animations_html(anims["attention"])),
                      ("exercises", "Exercises", n_att, ex_att)],
        "ba": [("map", "Concept map", 0, doc_html(PAPERS["ba"] / "concept_graph.md")),
               ("animations", "Animations", len(anims["ba"]), animations_html(anims["ba"])),
               ("exercises", "Exercises", n_ba, ex_ba),
               ("ideas", "Improvement ideas", ideas_count(PAPERS["ba"] / "ideas/ideas.md"), doc_html(PAPERS["ba"] / "ideas/ideas.md")),
               ("experiment", "Experiment", 0, doc_html(PAPERS["ba"] / "ideas/experiments/01_nonlinear_attachment/findings.md", strip_h1=False, demote=1))],
        "graph": [("map", "Map", 0, doc_html(EX / "knowledge_graph.md"))],
        "toy": [("paper", "Paper", 0, paper_html(pages)),
                ("ideas", "Improvement ideas", ideas_count(TOY / "ideas/ideas.md"), doc_html(TOY / "ideas/ideas.md")),
                ("experiment", "Experiment", 0, doc_html(TOY / "ideas/experiments/01_ramp_vs_peak_lr/findings.md", strip_h1=False, demote=1))],
    }

    groups = [("learn", "Learn a paper"), ("write", "Write a paper")]
    rail = "".join(
        '<div class="rail-group"><p class="rail-label">%s</p><ul>%s</ul></div>'
        % (label, "".join('<li><a href="#%s" data-case-link="%s"><span class="rail-title">%s</span><span class="rail-id">%s</span></a></li>'
                          % (c["id"], c["id"], esc(c.get("short", c["title"])), esc(c["ident"]))
                          for c in CASES if c["group"] == group))
        for group, label in groups)
    sections = "\n".join(case_section(c, tabs[c["id"]]) for c in CASES)
    page = (PAGE.replace("@@FONTS@@", esc(FONTS)).replace("@@KATEX@@", KATEX_JS)
            .replace("@@RAIL@@", rail).replace("@@HOME@@", HOME).replace("@@CASES@@", sections))
    (DIST / "index.html").write_text(page)

    unresolved = len(re.findall(r'class="xref"', page))
    print("wrote %s (%d kB), %d animations, %d page images, %d links kept as plain text"
          % (DIST.relative_to(ROOT) / "index.html", len(page) // 1024, sum(map(len, anims.values())), len(pages), unresolved))


if __name__ == "__main__":
    main()
