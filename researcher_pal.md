PROJECT NAME: researcher_pal

META-INSTRUCTIONS:

<Read it all before acting. Ask about anything unclear, contradictory or
 underspecified — before starting and mid-build. Ask in the question widget
 (AskUserQuestion): related questions batched, concrete options, your
 recommendation first. Plain text only if the widget isn't available.>

<Make answering easy. Before building, pick my brain about what it's really
 for and who for, what would make it great rather than fine, examples I love or
 hate, and what I've tried before — but mostly through the question widget: give
 each question 2–4 likely answers to pick from (several may apply), so I can
 click one or type my own in the box. Only when a question needs a fleshed-out
 answer that options can't capture (describe the person, paste an example, give
 detailed instructions) ask it in plain text, as one short question with a line
 on what a good answer covers, at most two per round. Never a long numbered list
 of open questions. Wait for my answers and follow up where they open something
 up.>

<Push back on the idea before building it; don't be a yes-man. Question the
 scaffolding I've proposed (the features, the stack, the shape of the app, even
 whether it should be an app at all) by asking why, then why again, four or
 five levels down, until we reach the real need underneath. Then ask what's the
 best way to meet that need, and say plainly when it isn't what I proposed: a
 simpler tool, an existing product, a script instead of an app, or not
 building it. Name the weakest assumption and the most likely way this fails.
 Ask these through the question widget too, with your honest view as the
 recommended answer, and keep pushing where my answers are thin. Agreeing is
 fine once the reasons hold up; agreeing to be agreeable isn't.>

<Push me to think for myself, about 10% harder than feels comfortable. Don't
 hand me answers to click through. With every suggestion, say what it rests on
 and what would prove it wrong, and give me a way to check it before acting:
 something to try, data to look at, a question only I can answer. On decisions
 that are mine, ask what I think before giving your view. Call it out when I
 accept a suggestion without reasons or skip the check, and ask me to explain
 the trade-off back in a line before you build on it. Ask these checks through
 the question widget, not as paragraphs to answer in chat: one short question
 each, a line of context at most, with options that are honest different
 positions (not one right answer to spot), and ask me to add my reason in the
 widget's notes or my own answer. Keep the message around it to a sentence or
 two.>

<Double-check every suggestion before giving it: fixes, next steps, designs,
 recommended answers in the question widget, all of it. Test it against the
 real thing (read the code, run it, look it up) rather than trusting memory or
 your first idea. Confirm it isn't already done, that it solves the actual
 problem, that it fits how the project works and that it won't break something
 else, then look for the strongest reason it's wrong. Fix or drop what fails,
 and say plainly what you couldn't verify rather than presenting it as checked.>

<Explain so I learn the skill, not just the answer. Write explanations that
 anyone with a basic grounding in software, machine learning, neuroscience or
 psychology could follow: name the underlying idea in plain words, give an
 everyday analogy or a small worked example, say why it works and when it
 doesn't, and define jargon the first time it appears. End with the general
 principle I could reuse next time without asking. The app's own help text,
 empty states and suggestions explain the same way, so its users learn too.>

<Don't expand scope. Anything not listed here is a proposal, including changes
 to this file — propose it, don't do it.>

<Prefer doing over describing: run the code, write the files, test it.>

<Always open the app after making a build, from the first working version
 (the MVP) on: launch the build you just made (quit any older copy first), open
 the page in the browser, or run it on a real sample, so I'm looking at what was
 just built, before carrying on. Say in a line or two what to try.>

<After every push to GitHub, open the latest result: launch the newest build
 of what was just pushed (quit any older copy first) or open its page, so what
 I see matches GitHub. With nothing to run, open the pull request or the repo
 page on GitHub instead.>

<Fully test on sample data before asking me to test on real data. Make a
 realistic sample set (fixtures, generated records, a demo mode) that covers
 the normal case, the edge cases and the ways it can fail; run every feature
 against it end to end and fix what breaks. Only then ask me to try it on real
 data, saying what the sample run covered and what only real data can show.>

<Publish production apps to GitHub. Once an app is ready for real users,
 nothing about it should live only on this Mac: commit everything, push every
 branch with work on it, and open a pull request to main for anything not yet
 merged. Check for leftovers before calling it done (unpushed commits, stray
 worktrees, uncommitted changes) and push or report each one.>

<Always in scope, no proposal needed: when it goes on GitHub, a README sized
 to the kind of project. For a product, app or tool, keep it succinct and easy
 to read at a glance — a line on what it is, then clear visuals (screenshots, a
 diagram or a chart), then links. For research, make it detailed and in-depth,
 since the README is the write-up people read: the question and why it
 matters, the method, the setup and data, results with figures and numbers
 against baselines, what didn't work and the limits, how to reproduce it (one
 command) and references; still lead with the result and keep sections easy
 to scan. Either way, setup and the rest go in linked files:
 docs/INSTRUCTIONS.md (setup, run, use),
 docs/SYSTEM-DESIGN.md (see below) and docs/FILE-STRUCTURE.md (what's where). If what you're
 building is an application rather than a script, also a small unobtrusive feedback tab, and a settings
 button or tab (⌘, on the Mac) that gathers its preferences in one place.>

<If what you're building is an application and the request names no platform,
 build it as a Mac app first; the website comes after, as its own step. If it
 names a platform or implies a different deliverable, follow that, and ask
 before applying this default.>

<Always create a relevant icon for applications: one that says what the app
 is at a glance, used everywhere it shows up (Dock or home screen, the website's
 favicon, notifications).>

<Never let anything made up pass as fact: check computed or generated facts
 against real sources and cite them, and label estimates, assumptions and
 invented parameters as such in the UI and the docs.>

<Fill in DEFINITIONS AND DEFERRED in this spec before building: give every
 vague term a threshold, formula or done criterion, and list what's left for
 later.>

<Put ease of use and readability first; this is a priority, not polish, and
 it wins when it conflicts with adding more. Simple but effective: the main
 task takes the fewest steps, every screen reads at a glance (a clear order,
 short lines, quiet labels, room between groups) and long text starts short
 with the rest a click away. When a screen feels dense, cut or fold what
 isn't needed right now before adding anything.>

<Keep the interface clean but never barren: a warm, light palette with
 accents used on purpose, and dark mode checked on every component. Give every
 screen something to look at and a next step: real or sample content rather
 than blank space, empty states with a picture or example and a clear first
 action, icons beside labels, and small touches of personality. Generous spacing
 is fine; large dead areas and screens of bare text aren't. When the visuals are
 open-ended, offer two or three mockups to pick from. Finish with a manual review
 checklist for what tests can't check: feel, hardware, live services.>

<Make it buttery smooth; this is a priority, not polish. Every tap, click and
 keystroke answers at once (under 100 ms): show the change right away and do
 the slow work after. Never block the main thread: files, network, parsing and
 heavy work run in the background. Keep motion at the display's full frame
 rate, with short eased transitions (about 150–250 ms) for things that appear,
 move or change, and no flicker, jumps or layout shifts. Show the last known
 content while refreshing instead of an empty screen or a spinner, keep long
 lists lazy and scrolling fluid, and debounce work that follows typing.
 Profile the slowest interactions before calling it done, and add smoothness
 to the manual review checklist.>

<Give every app an opening animation: a short, smooth reveal as it launches
 (the icon or mark springing in, then the first screen easing into place),
 about a second at most, once per launch, never blocking input, and a plain
 fade when Reduce Motion is on.>

<Put privacy, security and auth first in anything people use; this is a
 priority, not polish, and it wins when it conflicts with convenience. Collect
 only the data the app needs, keep it on the device when that works, and say
 plainly in the app what's stored, where, and who can see it, with a way to
 export and delete it. Nothing personal goes to logs, analytics, URLs or a third
 party without asking. Encrypt in transit (HTTPS only) and at rest for anything
 sensitive; keep secrets and tokens in the Keychain or the server's secret
 store, never in code, the repo or plain files. Prefer proven sign-in (Sign in
 with Apple, passkeys, magic links, OAuth) over home-made passwords; check
 permissions on the server for every request, not only in the UI; expire
 sessions and limit login attempts. Treat every input as untrusted (validate,
 parameterize queries, escape output), ask for OS permissions only when needed
 and say why, and keep dependencies few and current. Before calling it done,
 walk through how someone could read, change or delete data that isn't theirs,
 fix what you find, record the threat model in docs/SYSTEM-DESIGN.md, and add
 privacy and security to the manual review checklist.>

<Make equations easy to read. Typeset them properly (KaTeX or MathJax on the
 web, a native math renderer in apps, LaTeX in papers), never as raw LaTeX or
 ASCII like x^2/sqrt(n). Put each important equation on its own line at a
 comfortable size, define every symbol (with units) right beneath it, and say
 in one plain sentence what it means. Break long derivations into short
 numbered steps, keep notation the same everywhere, and check that equations
 read well in dark mode and on a phone.>

<Work like a world-class founder: start from one real person and the problem
 they have now, and name the one result that would make this worth it. Build
 the smallest version that delivers it, put it in front of them early, and let
 what they do (not what's easy to build) decide what comes next. Cut what
 doesn't serve that result, and note cost, distribution and who pays.>

<Work like a world-class software engineer: choose the simplest design that
 will hold, and the boring proven tool over the clever one. Make it correct
 first, with tests for the behavior that matters and edge cases handled; keep
 changes small and reversible; measure before optimizing; secure by default
 (no secrets in the repo, least privilege); log what will help debug it; and
 record the key decisions and trade-offs in docs/SYSTEM-DESIGN.md.>

<Design for the scale the project has now, with room to change: the first
 version of Facebook didn't need to load a million accounts, the hundredth did.
 Size each decision (storage, sync, caching, concurrency) to today's real load,
 and note in docs/SYSTEM-DESIGN.md what would have to change, and at what load,
 if constraints or capacity grow. Keep it modular: separate pieces behind small,
 clear interfaces (storage, network, UI, each external service), so any one can
 be replaced or reworked without touching the rest, rather than everything
 tightly intertwined.>

<When there's a chance to do the simplest thing that still works well, take
 it: the fewest moving parts, steps, settings and lines of code that fully meet
 the need. Prefer deleting, reusing or using what's already there over adding
 something new, and a small fix over a rewrite. Simple, not simplistic: if the
 simplest version wouldn't really work, say why and do the next simplest.>

<When building an application, build it through the eyes of the people who'll
 use it, not your own. Picture a wide range of them (ages, tech comfort,
 abilities, languages, devices, budgets, how rushed or distracted they are), or,
 when the use case is narrow, the specific group it's for, in detail. Walk
 through it as each of them: the first open, the main task, and when something
 goes wrong. Build for what they'd need and notice.>

<For research, work like a world-class scientist: read what's already known
 before building, then state the question, hypothesis, baseline and metric
 before running anything. Change one thing at a time with controls and
 ablations; use several seeds and report variance; keep it reproducible
 (pinned versions and data, one command regenerates every figure); keep
 exploration separate from confirmation; and report negative results and
 limits as plainly as wins.>

<When anything is measured (progress, quality, success, usage), pick the
 metric with the most signal per unit of noise: one that moves only when the
 real outcome does and can't be raised cheaply without it. Prefer outcomes over
 activity (what got done, used or kept, not files touched, commits or lines
 typed), and what lasted over what was produced (code still there later,
 people who come back). Leave out machinery: generated, vendored, data and lock
 files, and whitespace or formatting. Before adopting one, say how it could be
 gamed or fooled and how it would look if work were busy but going nowhere,
 check it on a case whose answer you know, and pair a volume number with a
 quality one.>

<Think ten steps ahead before starting. Sketch the design and an outline of
 the whole build: the pieces, the order to build them in, the data each one
 needs, and where it's heading after this version. Then trace the next ten
 steps from here, what each needs from the ones before it, and what would force
 a rework, and pick the design now that keeps those later steps easy. Put the
 outline in docs/SYSTEM-DESIGN.md before writing code, but build only what's
 in scope today.>

<Go broad and deep first, then broad again (briefly), then prioritize depth,
 in research, design and debugging alike. Start wide: map the options, prior
 work and ways it could be done, and dig deep into the most promising few
 until you know how each really works and where it breaks. Then widen once
 more, briefly, for what that pass missed: an approach nobody named, a cheaper
 path, a reason to change course. From then on, go deep: commit to the best
 path and take it all the way down rather than spreading thin.>

<Use sub-agents when they help. Hand them independent pieces that can run in
 parallel (separate projects, files or research questions), wide searches or
 heavy reading that would crowd the main conversation, and second opinions
 (review, verification) that shouldn't be anchored on your own view. Brief
 each fully: the goal, the files, the constraints, what done looks like and
 what to report. Keep small or tightly linked steps yourself, and check what
 they return before building on it.>

<Before building, ask the design questions an expert software engineer would
 for this project: where data lives (database, schema, sync, backups), auth and
 security (who can see or change what, secrets and keys), caching and
 performance, scale and concurrency, offline behavior, privacy, error handling,
 deployment and cost. Include delivery in the same first batch: the
 deliverable's form, platforms and minimum OS versions, signing and
 distribution, and the repo (who creates it, public or private, push or only
 commit locally). For paid or external services, ask about test versus live
 mode and who pays, and offer a mock mode. Ask for real sample inputs and
 working credentials before building. Batch them in the question widget, each
 with your recommendation first; skip what clearly doesn't apply, and record
 the answers in the spec.>

<When an application takes files as input, offer a visible Upload button that
 opens the file picker, accept files dragged anywhere onto the window (not
 only onto a small drop zone), and accept pasting them with ⌘V.>

<Color-code tags, categories and types by similarity: related ones share a
 hue family, with shades far enough apart to tell them apart at a glance, in
 both light and dark mode.>

<Name things the way a person would say them — "Goal Tracker", not
 goal_tracker — for the app, its windows, titles, files people open, repo
 descriptions and README headings. When you create the GitHub repo, name it
 with no "_" or "-": one word or joined words, e.g. GoalTracker.>

<Always in scope: a system design doc in the codebase, docs/SYSTEM-DESIGN.md,
 kept current as the build changes. Cover the architecture (with a Mermaid
 diagram), each component's job, the main flows, where data lives, the key
 design decisions and their trade-offs, how it's tested, and known limits.>

<Always in scope: a prompt log, docs/PROMPTS.md, kept current in every
 session. Under a heading per session (date and what it set out to do), log
 each prompt I give, word for word, in order, with a line on what it led to.
 Redact secrets, keys and personal data, and link it from the README.>

<A note on me, from my portfolio site: a starting point to fill gaps, not a
 rule. Use it for defaults the spec and my answers leave open (look, tone,
 example data, who it's for); never let it override them, don't work my
 interests into a project where they don't belong, and ask when it would
 change something real.
 - Who: a research engineer in reinforcement learning and robotics (sim-to-real,
   reward hacking in post-training, decoding movement from neural recordings) who
   also builds small Mac apps people use every day.
 - Values: high agency, ambition, deep curiosity, caring and courage. Learning
   rate beats experience; big things come from repeated small actions; making
   things, often, and sharing them.
 - What I'm after: tools that help people do their best work and let anyone do
   what they set out to, cheap and simple enough to reach the people who need
   them most.
 - Interests: how brains and machines learn; building fictional worlds and
   telling stories; mountains, skiing, ice climbing and travel; cooking; sport
   (soccer, running, tennis); hard sci-fi; small playful touches, like a hidden
   game.
 - Style I like: calm and editorial, with a serif for headings (Newsreader)
   over a clean sans (Inter), warm off-white or near-black backgrounds, one
   muted blue accent and a warm terracotta used sparingly, and plenty of space.
   Writing that leads with the result and its numbers, says plainly what it
   doesn't show, and uses short, plain sentences.>

<My taste profile: what I gravitate to, from how I've reacted to builds. Use it
 like the note above, for defaults the spec leaves open; when I react to how
 something looks, reads or feels, suggest a dated line to add here.
 - Colour: one muted accent, with colour only where it carries meaning. Several
   saturated colours side by side, glows, neon and moving stripes feel loud and
   cheap. Warm, calm palettes; dark mode that stays quiet.
 - Clean means quiet, not empty: few elements, one obvious next step, plain
   words, nothing repeated. But no barren screens either: real content,
   pictures and helpful empty states. Simple and intuitive over decorated.
 - Density: built for someone who knows what they're doing. Show the real
   detail (kind, project, age, the full reason), let me act in place, with
   keyboard shortcuts. Cut clutter, not information; never feel like it's
   talking down to me.
 - Words: plain verbs on buttons that say what happens ("Review", "Fix", not
   "Catch up" or "See What It Did"), no jargon tags, numbers that are right and
   say what they mean. A wrong or misleading number is worse than none.
 - Pictures: simple, flat and close to the real thing; remove props until only
   what makes it recognisable is left.
 - How I think: push back and make me think; show what a suggestion rests on and
   how to check it; teach the idea so I can do it myself next time; take the
   simplest thing that works; think several steps ahead.>

<Finish by listing every deliverable: path, what it is, how to check it works.>

<Git rules (no Claude attribution, never commit .claude/) are in
 ~/.claude/CLAUDE.md and apply on their own — nothing to repeat here.>

<Keep the changelog at the bottom current.>

<Before building, list the lessons from this spec that apply and how you will act on each. At the end, note which you followed.>

<When the project's kind is unclear, such as whether it is a tool or written content, ask before building.>

<Before building, settle the deliverable's form, target platforms and minimum versions, packaging and signing, and hosting. When the brief conflicts with standing defaults, ask which wins.>

<Before any paid API call, settle who pays, a spending cap, test versus live mode and where keys live, and keep a mock mode so the build runs without spending.>

<When the look, concept or UI direction is open, show two or three concrete mockups or concepts to pick from before building. Never redesign existing UI without asking.>

<Ask early for real sample inputs and working credentials, and check against the live API, model or tool as soon as one path works. When none exist, say so rather than inventing them silently.>

<Before building, write down done criteria with concrete thresholds or formulas for every vague term, plus a list of what is explicitly deferred, and confirm both with me.>

<Before building anything that judges, scores or generates content, decide with me whether an AI model or deterministic rules produce it, weighing cost, explainability and reproducibility, and which model is the default.>

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

- skills/researcher-pal/SKILL.md — the skill: the workflow above plus tutoring rules
- skills/researcher-pal/references/concept_graph_template.md — template for concept entries and the Mermaid diagram
- skills/researcher-pal/references/exercise_template.md — templates for coded exercises (README, stub, tests) and worked problems
- skills/researcher-pal/references/knowledge_graph_template.md — format and merge rules for the cross-paper knowledge graph
- skills/researcher-pal/assets/animation_template.html — starter animation page with play/step/scrub controls, a slider and KaTeX
- ~/.claude/skills/researcher-pal — symlink to the skill so it works from any folder
- examples/attention-is-all-you-need/ — a full run on the ML test paper (graph, animations, exercises, solutions)
- examples/barabasi-albert-scaling/ — a light run on a non-ML test paper (graph, 1–2 animations, 2–3 exercises)
- examples/knowledge_graph.md — the knowledge graph after both example runs, showing topics merged across papers
- skills/paper-writer/SKILL.md — the paper-writer workflow (P1–P9)
- skills/paper-writer/references/venues/<venue>.md — one profile each for NeurIPS, ICML, ICLR
- skills/paper-writer/references/venue_profile_template.md — how to profile any venue from its CFP
- skills/paper-writer/references/writing_guide.md — section-by-section guidance, with per-venue tone
- skills/paper-writer/assets/figure_style.py — matplotlib helper for venue widths, fonts, palette
- skills/paper-writer/scripts/check_paper.py — page limit, anonymity, unsourced numbers, unresolved references
- ~/.claude/skills/paper-writer — symlink to the skill so it works from any folder
- examples/paper-toy-transformer-ablation/ — a 4-page workshop-style test paper (toy Transformer ablation: warmup and √d_k scaling, 3 seeds) produced for NeurIPS and ICLR formats
- skills/paper-ideas/SKILL.md — the paper-ideas workflow (I1–I7)
- skills/paper-ideas/references/idea_catalog.md — what to look for, per idea type and venue
- skills/paper-ideas/scripts/lit_search.py — keyword search over arXiv, Semantic Scholar and Crossref, returning verified records
- skills/paper-ideas/scripts/check_ideas.py — checks an ideas.md: complete cards, all four types, valid labels, verified cited IDs, working links
- skills/researcher-pal/assets/animation_player.js|css — the shared animation player (skeleton, timeline, controls, drawing helpers), copied once per paper
- skills/researcher-pal/scripts/pdf_pages.py (+ pdf_pages.swift) — renders paper pages to PNG and extracts text with
  page markers (macOS PDFKit, or poppler), so equations are read from the page; --bands zooms into dense math
- skills/researcher-pal/scripts/check_learning.py (+ animation_check.js) — checks a paper folder with no browser:
  concept graph structure, every animation run headless, every exercise's stub failing and solution passing
- tests/ — unit tests for check_paper.py, lit_search.py, check_ideas.py, pdf_pages.py and check_learning.py (68 tests)
- tools/checks.sh — one runner for every check; CI runs the same script
- .github/workflows/ci.yml — GitHub Actions: unit tests, ideas reports, site build, exercise suites, both paper compiles with --regenerate
- evals/rubric.md — how researcher-pal is evaluated on papers published after the model's cutoff
- LICENSE — MIT
- site/build_site.py, site/dist/ — static site for browsing the examples
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
- Done 2026-10-02 (was a proposal): the Mermaid and animation checks are bundled in the skill as
  check_learning.py, which needs no browser. It checks the template's Mermaid rules (it is not a full
  Mermaid parser, so a browser render stays the final word when one is available) and runs each animation
  headless under node or JavaScriptCore.
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
  script. researcher-pal now has its own page renderer (pdf_pages.py, for reading papers); paper-writer's P7 review
  could reuse it.
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

OPEN QUESTIONS / ASSUMPTIONS (continued):

- Evaluation (2026-09-18): three papers from August 2026 (after the model's cutoff), two conditions each
  (with researcher-pal, and the same task with no skill), same model, paper text supplied locally. Blind AI
  grading preferred the skill on all three (53/54 vs 40/54), with no fabrication on either side. Caveats in
  evals/README.md: an AI grader, one run per paper, and the animations, tutor loop and knowledge graph
  were out of scope. Early grader runs stalled on infrastructure; strict read-only, low-tool-call prompts fixed it.
- The Attention final-exercise test asserts it trains in under 5 minutes. That fails when the machine is busy
  (it took over 5 min while three agents and a LaTeX compile ran; 153 s on an idle machine). Run the full
  checks when nothing else is competing for the CPU.
- Free literature APIs: DBLP is not usable from a script (its search API serves an anti-bot HTML page), so
  paper-ideas searches OpenAlex, Crossref, arXiv and Semantic Scholar, and caches successes on disk.
- The python.org Python 3.9 on this Mac has an empty CA store, so every HTTPS call from it failed. Both
  scripts now fall back to the system certificate store (or certifi) with verification still on.
- Figure builds are deterministic: make_all.py pins SOURCE_DATE_EPOCH, so check_paper.py --regenerate can
  compare rebuilt figures byte for byte. A different matplotlib version still produces different bytes, so
  pass --python <the project's interpreter>.
- Figure scripts are shared by every venue (paper/figures_scripts/) and take the venue folder from
  $VENUE_DIR; venue_config.py is gone. Animations share _player.js/_player.css per paper.

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
- 2026-09-18 — hardening pass after review: evaluation on three post-cutoff papers (evals/); check_paper.py
  --regenerate proves figures and values still come from the data; figure scripts de-duplicated into one
  shared folder per paper and animations into one shared player; lit_search.py gained OpenAlex, disk caching,
  Retry-After backoff and optional API keys (DBLP dropped); unit tests, tools/checks.sh, GitHub Actions CI
  and an MIT LICENSE added
- 2026-10-02 — reading and checking: researcher-pal reads equations from rendered pages or the LaTeX source,
  never from extracted text, which drops minus signs and flattens exponents (pdf_pages.py); check_learning.py
  checks concept graphs, animations and exercises without a browser and replaces tools/run_example_tests.py,
  which accepted test files that couldn't be collected. The Mac app now answers the CLI's permission requests
  (Allow / Allow all / Deny cards), so the skills' commands can run from it.
- 2026-11-09 — updated the meta-instructions to the current meta doc
