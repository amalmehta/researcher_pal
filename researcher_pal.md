PROJECT NAME: researcher_pal

META-INSTRUCTIONS:

<Read everything below before acting. If anything is unclear, contradictory,
 or underspecified, ask before starting — batch your questions into one message.>

<If you see a way to make the instructions simpler or more effective, propose
 the change first. Only edit this file after I approve. Keep a short changelog
 at the bottom.>

<Do not expand scope. If something seems necessary but isn't listed, flag it
 as a proposal — don't just do it.>

<Prefer doing over describing. Run code, produce files, test things.>

<At the end of the build, list every deliverable component with its path and a
 one-line description of what it is and how to verify it works.>

CONTEXT:

Helps one learner understand any research paper from scratch, in any field (not
just ML), inside Claude Code. It builds a concept graph of how the paper works,
explains the fine details and nuances (including what the paper leaves out), shows
the key ideas as interactive 3Blue1Brown-style animations, walks the learner through
implementing or working through the paper with guided exercises, and keeps one
knowledge graph of every topic the learner has learned across all papers.

It also helps a researcher write their own paper for a chosen venue: drafting text
from their results, notes, code and existing drafts, generating figures and tables
from their data, and formatting to the venue's official template and rules. The
researcher owns every claim; the skill never invents results or citations.

It also generates ideas for improving a paper, both the researcher's own draft and papers
being learned: writing and presentation fixes, stronger evidence and experiments, likely
reviewer objections, and new research directions. Each idea is tied to evidence in the
paper and checked against existing literature. Approved ideas can be applied to the draft
or run as new experiments.

INPUTS:

- A paper, given as a local PDF path or an arXiv ID/URL. The paper is the
  authoritative source; anything the notes say that the paper doesn't must be
  labeled "not in paper".
- The learner's knowledge graph at ~/researcher-pal/knowledge_graph.md (created on
  first use).
- For paper writing: any of results data (CSV/JSON/logs), notes or an outline, a
  code repository, an existing draft and .bib file; plus the target venue, as a
  built-in profile name or a CFP link / template zip. The researcher's data and the
  venue's current CFP are authoritative; profiles are a starting point.
- For paper ideas: the draft (or the learned paper), its results and code, and the
  compute budget (default: CPU, 30 minutes per experiment, 2 hours per round).

INSTRUCTIONS:

1. Get the paper: copy the PDF, or download it from arXiv, to papers/<slug>/paper.pdf.
2. Read the whole paper, appendix included. List every section, numbered equation,
   algorithm, figure and hyperparameter table.
3. Read the knowledge graph, then write papers/<slug>/concept_graph.md:
   a. A Mermaid diagram of concepts, with arrows going from prerequisite to concept.
      Reuse the knowledge graph's topic IDs for concepts it already has, and mark
      topics the learner already knows.
   b. One entry per concept with: intuition; the equation with every symbol (and
      shape or units) explained; nuances and gotchas; the paper section/equation
      it comes from; prerequisites from outside the paper.
4. Pick the 3–6 concepts where seeing things move builds intuition most. For each,
   write papers/<slug>/animations/<concept>.html from the skill's template:
   play/step/scrub controls, at least one slider tied to a real quantity from the
   paper, and the equations shown alongside. Link each from its concept entry.
5. PAUSE: show the graph and animations, list the topics the knowledge graph says
   the learner already knows, and ask which other concepts they know and where they
   want to start. Record known topics in the knowledge graph.
6. Turn the concepts into exercises in dependency order under
   papers/<slug>/exercises/NN_<concept>/. Choose the form per concept:
   a. Coded exercise: README.md (goal plus the equations it covers), impl.py
      (signatures and TODOs only), test_impl.py (pytest checks), and a reference
      solution in papers/<slug>/.solutions/. Stack by field: PyTorch for ML,
      NumPy/SciPy for numerical and scientific models, the standard library for
      algorithms and CS theory.
   b. Worked problem, when there is nothing meaningful to code (proofs, pure
      theory, qualitative arguments): README.md (the problem and what a complete
      answer shows), answer.md for the learner, and a reference solution.md in
      papers/<slug>/.solutions/.
7. Tutor loop, repeated per exercise and waiting on the learner each time: the
   learner writes code or an answer (and runs the tests for code). Hints escalate
   from the idea, to the relevant equation, to specific code or steps. Review the
   work against the paper. Only reveal the solution if asked. When an exercise
   passes or a worked problem is accepted, mark its topic learned in the
   knowledge graph.
8. Final exercise: combine the parts into the paper's core method or central
   result. For coded papers, run it on toy data and reproduce one of the paper's
   qualitative results. For theory papers, set a capstone worked problem that
   rebuilds the main argument.

INSTRUCTIONS — paper-writer (a separate skill):

P1. Intake: read everything provided. List the paper's claims, the result file(s)
    behind each, and what's missing. PAUSE: the researcher confirms the claims.
P2. Venue: load the profile, then fetch the current CFP and official template (or use
    the ones provided). Record the page limits, anonymity rules, required sections and
    checklists, formatting rules and LLM-use policy. Flag anything in the profile that
    no longer matches the CFP.
P3. Outline: a section-by-section plan sized to the page budget, plus a figure/table
    plan (what each shows, which data file it uses). PAUSE: the researcher approves it.
P4. Figures and tables: one script per figure or table under the paper's
    figures/scripts/. Each reads the data and writes a PDF or .tex file at the venue's
    column width and fonts, in colorblind-safe colors. Method diagrams in TikZ or
    Graphviz; concept illustrations as editable SVG drafts.
P5. Draft one section at a time in the venue's style. Every number is logged in
    sources.md with its file; anything unknown becomes a visible \TODO{}, never a guess.
P6. Citations: check every .bib entry against arXiv or DOI records and flag failures.
    Suggest related work from the knowledge graph and provided references, but only
    add what the researcher approves.
P7. Compile with Tectonic, then write venue_report.md: page count against the limit,
    overfull boxes, missing references and figures, anonymity leaks, checklist status,
    and a draft LLM-use disclosure.
P8. Revision loop: apply the researcher's edits and re-run P7 after each change.
P9. Retarget: switching venue re-runs P2, P3 (resizing and restructuring) and P7.

INSTRUCTIONS — paper-ideas (a separate skill, called by paper-writer and researcher-pal):

I1. Gather context. Own draft: sections, compiled PDF, results, code, venue profile,
    venue report. Learned paper: the paper, concept graph, the learner's implementation,
    knowledge graph.
I2. Generate candidate ideas of four types: (a) writing and presentation; (b) evidence and
    experiments (missing baselines, ablations, seeds, statistics, thin claims); (c) a
    simulated reviewer critique (the target venue's reviewers for a draft; a critical
    reviewer for a published paper); (d) new research directions.
I3. Ground each idea in the exact passage, figure or number that motivates it. For
    experiment ideas: the claim it tests, what result would change the conclusion, and a
    compute estimate.
I4. Literature check: keyword-only queries (never unpublished text) on arXiv, Semantic
    Scholar and Crossref. Attach related work found (verified records only). Label each
    idea "related work: …", "no close match in searched sources (not proof of novelty)"
    or "unverified (search failed)". List the queries used in the report.
I5. Rank by impact × feasibility and write ideas.md (ranked table + details).
    PAUSE: the researcher or learner picks which ideas to act on.
I6. Apply approved non-experiment ideas. Own draft: edit sections, scripts or figures, then
    regenerate, recompile and re-run the checks. Learned paper: add the idea to the concept
    graph as an "open question" note.
I7. Run approved experiments: write a plan (hypothesis, design, metrics, compute estimate)
    and confirm it fits the budget; put new code and results in a new folder; run it; then
    update from the results. Own draft: values, tables, figures and claims, including
    negative results, followed by recompile and checks. Learned paper: findings and figures
    in ideas.md.
Triggers: automatically after the first successful paper-writer P7 and after researcher-pal
step 8; on request at any time.

CONSTRAINTS:

- Python 3.9+ and pytest for coded exercises. Libraries by field: PyTorch 2.2+ (ML),
  NumPy/SciPy (numerical and scientific), standard library only (algorithms, CS
  theory). Ask before adding any other library.
- Every exercise runs on CPU in under 1 minute; the final one in under 5 minutes.
- Animations are single self-contained HTML files using plain JS with SVG or
  Canvas. The only external script is KaTeX from a CDN. No build step.
- Allowed external calls: downloading the paper (and its LaTeX source) from arXiv,
  and loading KaTeX or mermaid.js from a CDN in the browser. No API keys.
- Never put solution code or answers into the learner's files, or show solutions,
  unless the learner asks.
- Every concept entry names its section or equation in the paper.
- All written output is Markdown, except the animation HTML files.
- The knowledge graph is one Markdown + Mermaid file shared by all papers. Topics are
  merged by ID, and no topic or other paper's history is ever deleted.

CONSTRAINTS — paper-writer:

- Never invent results, numbers, experiments, quotes or citations.
- Every number in text or tables is traced in sources.md, and every figure
  regenerates from its script.
- LaTeX with the venue's official template, compiled by Tectonic (official prebuilt
  binary in ~/.local/bin; Homebrew needs Xcode Command Line Tools on this Mac).
  Figures use Python 3.9 + matplotlib + NumPy (pandas is broken here), TikZ,
  Graphviz, or SVG converted with rsvg-convert.
- External calls also allowed: official conference, CFP and template pages; the
  arXiv API and doi.org/Crossref for citation checks; Tectonic's download of the LaTeX
  packages it needs on first compile. No API keys.
- Built-in venue profiles: NeurIPS, ICML, ICLR. Each holds slow-changing conventions
  plus where to find the rules, with the date it was last checked, and is re-verified
  against the CFP on every run.
- Never submits anything anywhere.

CONSTRAINTS — paper-ideas:

- Never invent evidence, related work or novelty. Related work must be a verified record,
  and novelty is never asserted.
- External queries for unpublished work use keywords only, and every query is shown.
- Nothing is applied or run without approval. Experiments stay within the compute budget
  (default: CPU, 30 minutes each, 2 hours per round); ask before exceeding it or installing
  anything.
- The original code and results are never modified. A result that contradicts a claim is
  reported, and the claim is revised.
- External calls added: Semantic Scholar Graph API (no key) and Crossref search.

DELIVERABLES:

- .claude/skills/researcher-pal/SKILL.md — the skill: the workflow above plus tutoring rules
- .claude/skills/researcher-pal/references/concept_graph_template.md — template for concept entries and the Mermaid diagram
- .claude/skills/researcher-pal/references/exercise_template.md — templates for coded exercises (README, stub, tests) and worked problems
- .claude/skills/researcher-pal/references/knowledge_graph_template.md — format and merge rules for the cross-paper knowledge graph
- .claude/skills/researcher-pal/assets/animation_template.html — starter animation page with play/step/scrub controls, a slider and KaTeX
- ~/.claude/skills/researcher-pal — symlink to the skill so it works from any folder
- examples/attention-is-all-you-need/ — a full run on the ML test paper (graph, animations, exercises, solutions)
- examples/barabasi-albert-scaling/ — a light run on a non-ML test paper (graph, 1–2 animations, 2–3 exercises)
- examples/knowledge_graph.md — the knowledge graph after both example runs, showing topics merged across papers
- .claude/skills/paper-writer/SKILL.md — the paper-writer workflow (P1–P9)
- .claude/skills/paper-writer/references/venues/<venue>.md — one profile each for NeurIPS, ICML, ICLR
- .claude/skills/paper-writer/references/venue_profile_template.md — how to profile any venue from its CFP
- .claude/skills/paper-writer/references/writing_guide.md — section-by-section guidance, with per-venue tone
- .claude/skills/paper-writer/assets/figure_style.py — matplotlib helper for venue widths, fonts, palette
- .claude/skills/paper-writer/scripts/check_paper.py — page limit, anonymity, unsourced numbers, unresolved references
- ~/.claude/skills/paper-writer — symlink to the skill so it works from any folder
- examples/paper-toy-transformer-ablation/ — a 4-page workshop-style test paper (toy Transformer ablation: warmup and √d_k scaling, 3 seeds) produced for NeurIPS and ICLR formats
- .claude/skills/paper-ideas/SKILL.md — the paper-ideas workflow (I1–I7)
- .claude/skills/paper-ideas/references/idea_catalog.md — what to look for, per idea type and venue
- .claude/skills/paper-ideas/scripts/lit_search.py — keyword search over arXiv, Semantic Scholar and Crossref, returning verified records
- .claude/skills/paper-ideas/scripts/check_ideas.py — checks an ideas.md: complete cards, all four types, valid labels, verified cited IDs, working links
- ~/.claude/skills/paper-ideas — symlink to the skill so it works from any folder
- hooks added to paper-writer and researcher-pal SKILL.md
- examples/paper-toy-transformer-ablation/paper/ideas/ — ideas report, one applied edit, one approved experiment folded into both venue PDFs
- examples/barabasi-albert-scaling/ideas/ — ideas report plus one approved experiment

DONE CRITERIA:

- SKILL.md has valid frontmatter, and asking "help me learn arXiv 1706.03762" in
  Claude Code triggers the skill.
- Every example Mermaid diagram (both concept graphs and the knowledge graph)
  renders with mermaid.js in the in-app browser without errors.
- Every numbered equation and every Section 3.x of the Attention paper, and every
  numbered equation of the Barabási–Albert paper, is cited by at least one concept.
- The Attention example has 3–6 animations and the Barabási–Albert example has 1–2,
  each linked from its concept entry. Each one opens in the in-app browser with no
  console errors, and its play, step, scrub and slider controls visibly change the
  picture.
- For every coded exercise in both examples, pytest fails on the untouched stub and
  passes on the reference solution.
- The Attention final exercise runs on CPU in under 5 minutes.
- examples/knowledge_graph.md lists topics from both papers, and a topic used by both
  papers appears once with both papers listed.
- The example paper compiles with Tectonic for both venues with no errors, within
  each venue's page limit, and anonymized where required.
- check_paper.py finds no number in the example paper's text or tables missing from
  sources.md.
- Every example figure regenerates from its script, and every .bib entry is verified
  or flagged.
- Retargeting the example paper from NeurIPS to ICLR compiles, leaving only the
  issues venue_report.md flags.
- "Help me write my paper for NeurIPS" triggers paper-writer, and "help me learn
  arXiv …" still triggers researcher-pal (confirmed by you in a fresh session).
- Each example ideas.md covers all four idea types; every idea has an evidence pointer and a
  literature label.
- No search query contains 6+ consecutive words from the draft's sections (checked by script).
- lit_search.py returns verified records from at least 2 of the 3 services for a test query.
- The applied edit and the new experiment: both venue PDFs recompile and all checks pass;
  the original results files are unchanged.
- The Barabási–Albert experiment runs within budget, and its findings are in ideas.md.
- "Suggest improvements for my paper" triggers paper-ideas (confirmed by you in a fresh
  session).

OPEN QUESTIONS / ASSUMPTIONS:

- Skill is named researcher-pal (skill names can't contain underscores); the
  project folder keeps its name.
- Skill source lives in this project; ~/.claude/skills/researcher-pal is a
  symlink to it so it works from any folder. When Claude Code is opened in this
  folder, the skill may be listed twice (project + user copy).
- Test papers: Attention Is All You Need (arXiv 1706.03762) and Barabási & Albert,
  "Emergence of scaling in random networks" (arXiv cond-mat/9910332).
- Reference solutions live in a hidden .solutions/ folder — out of the way, but
  not truly secret.
- Example runs use the existing Python 3.9 at /Library/Frameworks/Python.framework
  with PyTorch 2.2.2 (the newest PyTorch for Intel Macs). Python 3.9 is past
  end-of-life. That install also has NumPy 2.0.2, which PyTorch 2.2.2 wasn't built
  for: importing torch prints a warning, but nothing in the exercises uses the two
  together.
- A globally installed pytest plugin (hydra-core's hydra_pytest) crashes pytest on
  this machine; the example pytest.ini blocks it with -p no:hydra_pytest.
- Topic status in the knowledge graph: known (the learner says so), learning
  (exercise started), learned (exercise passed or worked problem accepted).
- The example runs write examples/knowledge_graph.md instead of
  ~/researcher-pal/knowledge_graph.md, so your real graph doesn't start out with
  test progress. The learner's answers at step 5 are simulated there.
- The Barabási–Albert arXiv preprint numbers no equations. Its concept graph labels
  the nine equations E1–E9 and cites every one, which is how that done criterion
  was checked.
- The trigger criterion could not be checked automatically: `claude -p` hangs when
  run from this session's sandboxed shell. The skill is registered (it appears in
  Claude Code's skill list, and its description contains the test phrase), but
  please confirm by typing "help me learn arXiv 1706.03762" in a fresh session.
- .claude/launch.json starts a local static server (python3 -m http.server 8765).
  The in-app browser can't run scripts on file:// pages, so the Mermaid and
  animation checks use http://localhost. The browser pane also pauses animation
  frames when hidden, so the animation checker drives each page's clock directly.
- Proposal (not done): bundle the Mermaid-check page generator and the animation
  checker as scripts inside the skill, so each run reuses them instead of
  rewriting them.
- paper-writer example: the researcher's inputs (notes, rough draft, .bib) are
  simulated and marked as such; the results are real runs of the Attention example
  code. It is a format and workflow test, not a submission.
- Tectonic 0.17.0 was installed from its official GitHub release into ~/.local/bin (approved). The
  Homebrew attempt failed, but before stopping it upgraded cmake to 4.4.3 and installed a few
  libraries (e.g. graphite2).
- Tectonic runs XeTeX: templates that load `times` for pdfLaTeX (ICLR's does) need
  \usepackage[T1]{fontenc} in main.tex, or bold and small caps are silently substituted. Found by
  reading the rendered PDF; check_paper.py now fails on font substitutions.
- Venue cycles as of 2026-09-15: ICLR 2027 rules are published (full papers due Sep 25, 2026). The
  NeurIPS 2027 and ICML 2027 calls aren't published, so those profiles use the 2026 rules, labeled as such.
- arXiv's API rate-limits bursts (HTTP 429). Citation checks fall back to doi.org records for arXiv
  DOIs, and report a failed lookup as "not verified", never as a mismatch.
- The paper-writer trigger can't be tested from this session either (`claude -p` hangs); please
  confirm "help me write my paper for NeurIPS" in a fresh session.
- Each example venue folder keeps compile intermediates (main.aux/.log/.bbl, compile.out, checks.md),
  because check_paper.py reads them.
- Proposal (not done; declined for now on 2026-09-15): bundle the PDF page renderer used for the P7 visual review as a skill
  script. The same applies to the Mermaid and animation checkers proposed above.
- paper-ideas uses a fourth literature label, `not applicable (presentation)`, for writing-only ideas.
  The spec's three labels are about novelty, which a wording or figure fix doesn't have.
- Literature services during the example runs (2026-09-15): Crossref answered every query, Semantic Scholar
  (no key) answered 1 of 15, and arXiv answered none (HTTP 429 or timeouts, even with backoff). The test query
  still met the 2-of-3 criterion (Semantic Scholar + Crossref). Crossref returns titles without abstracts, so
  most related-work links in the example reports are judged from titles and marked that way.
- In the toy paper, experiment I-01 (ramp vs. learning-rate magnitude) came out mixed and weakened the claim "warmup
  is necessary". Per the stop-and-tell rule, the run stopped before any claim was edited. The researcher's decision to
  reword ("warmup matters", title included) was simulated in the example, and you confirmed keeping it on 2026-09-15.
- That experiment took 24.7 min against a 6-min estimate, because it shared the CPU with the literature searches
  and the Barabási–Albert experiment. That's still inside the 30-min budget, but pilots timed on a busy machine
  are unreliable. The findings file and the paper both say so.
- The paper-ideas trigger can't be tested from this session (`claude -p` hangs). Please confirm "suggest
  improvements for my paper" in a fresh session.

CHANGELOG:

- 2026-09-15 — created
- 2026-09-15 — filled in all sections from Q&A (Claude Code skill, Markdown +
  Mermaid graph, guided exercises, PyTorch)
- 2026-09-15 — Python 3.9+ (no Python 3.10+ with PyTorch on this Mac); added
  interactive HTML animations for 3–6 key concepts (new step 4); Mermaid render
  check moved to the in-app browser
- 2026-09-15 — any field, not just ML: exercise stack chosen by field, worked
  problems for papers with nothing to code; one knowledge graph of learned topics
  across papers; added a light second test run on a non-ML paper
- 2026-09-15 — added paper-writer, a separate skill that helps researchers write
  their own papers per venue (P1–P9): built-in NeurIPS/ICML/ICLR profiles plus any
  venue from its CFP; generated figures and tables; Tectonic compile checks; citation
  checks via arXiv and Crossref; two-venue test paper
- 2026-09-15 — Tectonic from its official prebuilt release instead of Homebrew (approved after the
  Homebrew install failed); SVG figures converted with rsvg-convert
- 2026-09-15 — added paper-ideas, a separate skill used by paper-writer and researcher-pal
  (I1–I7): four idea types, literature checks on arXiv, Semantic Scholar and Crossref, applying
  approved edits and running approved experiments (CPU, 30 min each, 2 h per round); tested on both
  existing examples
- 2026-09-15 — kept the toy paper's revised warmup claim (confirmed by you); added check_ideas.py to
  paper-ideas (approved), run before the I5 pause
