---
name: researcher-pal
description: Teach someone any research paper from scratch, in any field (machine learning, physics, biology, economics, computer science, mathematics), and guide them to implement or work through it. Reads the paper (a PDF, or downloads an open-access copy from an arXiv ID, DOI, link or title), builds a Markdown + Mermaid concept graph explaining every equation, symbol and unstated nuance, makes interactive 3Blue1Brown-style HTML animations of the key ideas, then tutors the learner through exercises. Exercises are coded with tests (PyTorch, NumPy/SciPy or plain Python, chosen by field) or worked problems for proofs and theory, with escalating hints and hidden solutions. Keeps one knowledge graph of every topic the learner has learned across papers and skips what they already know. Use this whenever someone wants to learn, understand, study, reproduce or implement a specific paper, e.g. "help me learn arXiv 1706.03762", "walk me through the Barabási–Albert paper", "I want to really understand this PDF", "teach me the math in this paper", or a pasted paper link with "understand", "learn" or "implement", even if they never mention graphs, animations or exercises. Also use it when they ask what they've learned so far or want to see their knowledge graph. Not for one-paragraph summaries, literature reviews across many papers, or writing your own paper (use paper-writer).
---

# researcher-pal

The goal is a learner who can rebuild the paper's core result themselves and explain
why each piece is there. The concept graph makes the structure visible, the animations
build intuition, the exercises turn understanding into skill, and the knowledge graph
makes learning add up across papers. Keep that goal in mind when a situation isn't
covered below.

## Output layout

Everything for one paper lives under `papers/<slug>/` in the current directory
(`<slug>` = short lowercase-hyphenated title, e.g. `attention-is-all-you-need`):

```
papers/<slug>/
├── paper.pdf
├── source.json                    # where the PDF came from, if it was downloaded (step 1)
├── paper.txt                      # extracted text, only if needed (step 2)
├── concept_graph.md
├── animations/<concept-id>.html   # one per animated concept
├── animations/_player.js, _player.css   # the shared player, copied once per paper
├── exercises/
│   ├── pytest.ini  conftest.py  _load.py                   # shared harness, if any exercise is coded
│   ├── NN_<concept-id>/  README.md  impl.py  test_impl.py  # coded exercise
│   └── NN_<concept-id>/  README.md  answer.md              # worked problem
└── .solutions/NN_<concept-id>/  impl.py | solution.md      # mirrors exercises/

~/researcher-pal/knowledge_graph.md                         # one file for all papers
```

## Ground rules (hold for every step)

- **The paper is the authority.** Every concept entry cites its section, equation, figure
  or table. Anything you add that the paper doesn't say (common practice, your inference,
  later corrections by others) is labeled **not in paper**. If you're unsure what the paper
  means, say so rather than smoothing it over. Learners trust these notes, and a
  confident wrong detail costs them hours.
- **Pick the exercise stack by field** and tell the learner which one:

  | The paper is about | Coded exercises use |
  |---|---|
  | machine learning, deep learning | Python + PyTorch |
  | numerical or scientific models (physics, biology, chemistry, economics, statistics, networks) | Python + NumPy, plus SciPy for solvers, special functions or statistics |
  | algorithms, data structures, CS theory, cryptography | Python standard library |

  All coded exercises use pytest. Find a Python 3.9+ that can import what you need (try
  `python3`, then versioned interpreters) and use it for every command. If none has the
  libraries, stop and ask. Don't install anything on your own, and ask before using any
  other library. Write code that runs on Python 3.9 (no `match`, no `X | Y` type hints).
- **If pytest crashes on startup** because of an unrelated, globally installed plugin, block
  that plugin in `exercises/pytest.ini` with `-p no:<name>` rather than touching the
  learner's environment. To find the name, list the plugins with
  `python -c "import importlib.metadata as m; print(m.entry_points().get('pytest11', []))"`.
- **External calls.** Downloads are limited to the paper and, for arXiv papers, its LaTeX source,
  fetched by `scripts/fetch_paper.py` from arXiv and from the open-access copies that OpenAlex,
  Semantic Scholar, Europe PMC, Unpaywall (only with the learner's email) and the paper's own page
  point to. Never get around a paywall or a site's bot protection, and never use shadow libraries.
  Animations load KaTeX, and the Mermaid check loads mermaid.js, from cdn.jsdelivr.net in the
  browser. No API keys.
- **Format.** All written output is Markdown, except the animation HTML files.
- **Solutions stay hidden.** Never put solution code or answers in the learner's files, and
  never show `.solutions/` unless the learner explicitly asks.

## Step 1: Get the paper

- Anything that identifies the paper: an arXiv ID or link, a DOI, an OpenReview, PubMed
  Central, ACL Anthology or Semantic Scholar link, a publisher's page, a PDF link, or the title:
  `python3 <skill dir>/scripts/fetch_paper.py "<what the learner gave>" --out papers/_incoming/paper.pdf`
  (or straight into `papers/<slug>/` if the folder already exists). It downloads an open-access copy
  and writes `source.json` beside it (title, DOI, arXiv ID, where the PDF came from). Then:
  - exit 0: rename `papers/_incoming` to `papers/<slug>`, the slug made from the title in
    `source.json`. For an arXiv paper, note in `concept_graph.md` which version you used (the
    ID's `vN`, or "latest as of <date>"), because equation numbers can shift between versions;
    its LaTeX source link is in `source.json` for step 2;
  - exit 4 (a title matched several papers): show the candidates and ask which one;
  - exit 3 (no open-access copy): tell the learner, list what was tried, and ask them to download
    the PDF through their own access and give you the file. Don't look for other copies yourself.
- Local PDF: copy it to `papers/<slug>/paper.pdf`.

## Step 2: Read the whole paper

Read every page, appendix included. The details needed to implement or reproduce a
result often hide in appendices, footnotes and figure captions.

1. Try the Read tool on the PDF (`pages`, up to 20 per call). If it can't render pages
   (e.g. poppler is missing), extract text to `paper.txt` instead, trying in order:
   - macOS: a PDFKit one-off: save this as a `.swift` file in a scratch folder and run
     `swift <file> paper.pdf > paper.txt`:
     ```swift
     import Foundation; import PDFKit
     let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
     for i in 0..<doc.pageCount { print("\n===== PAGE \(i+1) =====\n" + (doc.page(at: i)?.string ?? "")) }
     ```
   - `pdftotext -layout paper.pdf paper.txt` if installed.
2. Extracted text garbles math: subscripts flatten, and fractions and roots vanish. For
   arXiv papers, get equations exactly from the LaTeX source
   (`curl -sSL https://arxiv.org/e-print/<id>` into a scratch dir; it's usually a tar.gz,
   sometimes a single gzipped `.tex`). Commented-out passages in the source can explain
   odd cross-references, but they are **not in paper**. For local PDFs, rebuild each
   equation from the surrounding text and symbol definitions, and tell the learner which
   ones you reconstructed.
3. Build an inventory: every section and subsection, every numbered equation (plus
   important unnumbered ones, labeled like "§3.3 unnumbered"), theorem, algorithm, figure
   and table. This becomes the coverage table in step 3, which is how you prove nothing
   was silently skipped.

## Step 3: Write the concept graph

First read the knowledge graph (see [Knowledge graph](#knowledge-graph)) if it exists. When
a concept is a topic already there, **use its topic ID as the concept ID**. If its status
is `known` or `learned`, give it the `known` class. The learner shouldn't relearn the same
idea for every paper.

Then read `references/concept_graph_template.md` and follow its structure and Mermaid rules.

- **Granularity.** A concept is something you could explain in about two minutes and
  check on its own. "The model" is too coarse and hides the structure. "Taking a
  derivative" is too fine and just adds noise. A typical paper has 12–25 concepts; short
  letters have fewer.
- **Three kinds of node:** *prerequisite* (from outside the paper), *core* (established
  ideas the paper relies on), *novel* (the paper's contribution). This tells the learner
  where the new ideas are.
- **Nuance is the point.** Anyone can restate an abstract. Look for:
  - one-sentence choices that drive the result (a scaling factor, a modeling assumption
    such as mean-field or independence, a boundary condition, a constant picked without
    comment);
  - details that only appear in an appendix, a footnote, a table or a figure;
  - what the paper leaves unspecified that you must decide to reproduce it, labeled
    **not in paper**;
  - places where the text, figures and tables disagree, and "it is easy to see" steps
    that aren't easy;
  - units, shapes, and the regime where an approximation holds.
- **Check the Mermaid diagram renders** before showing it. Write a scratch HTML page
  that loads `https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`, puts the
  diagram source in a `<pre class="mermaid">`, and runs `mermaid.run()`. Serve it from a
  local web server (e.g. `python3 -m http.server`) and open the `http://localhost` URL with a
  browser tool, since many browser tools can't run scripts on `file://` pages. Look for console
  errors or Mermaid's error graphic, and fix any. If no
  browser tool is available, re-check the template's syntax rules by hand and tell the
  learner the diagram is unverified.

## Step 4: Build the animations

Pick the **3–6 concepts where seeing things move teaches something static text
can't** (1–2 for a short paper):
- a quantity changing with a parameter (an exponent, a temperature, a rate, a dimension);
- a process unfolding step by step (a network growing, an algorithm running, a
  population evolving, weights forming);
- geometry or the picture behind a proof (projections, rotations, bounds closing in).

Skip concepts that are just definitions.

Copy `assets/animation_player.js` to `papers/<slug>/animations/_player.js` and
`assets/animation_player.css` to `_player.css` once per paper: they hold the page skeleton, timeline,
controls and drawing helpers that every animation shares, so a fix there fixes all of them.
For each animation, copy `assets/animation_template.html` to
`papers/<slug>/animations/<concept-id>.html` and edit only the `THIS ANIMATION` block (`EDIT
ABOVE` block. The player (timeline, controls, keyboard, KaTeX) is shared. The template's
softmax demo shows the whole API.

What makes it 3Blue1Brown-like instead of a slideshow:
- **One idea per animation.** Start concrete and small (4 tokens, 10 nodes, 2-D vectors),
  then show the general case.
- **Each step changes one thing**, and its caption says what to notice. Typically 4–8
  steps of 2–5 seconds each.
- **Compute the real math in JS** (with a seeded random generator for anything random).
  Moving a slider must show what actually happens, not a hand-drawn curve. Sliders are
  real quantities from the paper, with the paper's value as the default and noted in
  the help text.
- **Color means something.** A symbol keeps the same color in the drawing, the captions
  and the equation (`\color{#58c4dd}` in TeX).

Link each animation from its concept entry and add 🎬 to its node label.
Then **verify each one** in a browser tool, served over `http://localhost` as in step 3. Check
that there are no console errors, and that play, next/prev step, scrubbing and every slider
visibly change the picture (take a screenshot before and after). Fix it before moving on.

## Step 5: Pause for the learner

Show the path to `concept_graph.md` and the list of animations, plus a 3–5 line
overview of the paper's structure and what is novel. Then ask, in one message:
1. The knowledge graph says you already know <topics>. Anything else you know? Those
   topics stay in the graph with the `known` class but get no exercise.
2. Where do you want to start, and how deep? The whole paper, or just the novel parts?

Wait for the answer. The exercises should fit what this learner actually needs.
Record the topics they say they know as `known` in the knowledge graph.

## Step 6: Write the exercises

Read `references/exercise_template.md` for the harness, file templates and the
verification script.

- One exercise per concept worth practicing, in dependency order, numbered `01`, `02`, …
  Skip concepts the learner knows. Fold pure definitions into a neighbor.
- **Choose the form per concept:**
  - **Coded exercise** when the concept can be computed, simulated or checked
    numerically. `impl.py` has signatures, docstrings with shapes or units and the
    equation reference, and `raise NotImplementedError`. A later exercise reuses earlier
    work through `_load.load("NN_<concept-id>")`, so the learner builds on their own code.
  - **Worked problem** when the substance is a derivation, a proof or an argument. The
    README states the starting point, the target and what a complete answer must show;
    the learner writes `answer.md`. Even in a theory paper, a claim you can check
    numerically (a derived exponent, a bound) makes a good small coded exercise.
- The README points at equations and animations; it never gives away the answer.
- **Tests check what the paper implies, not quirks of your solution:**
  - output shapes or units;
  - tiny cases worked out by hand;
  - properties or invariants (probabilities sum to 1, a conserved quantity, a symmetry,
    a limit);
  - agreement with a trusted routine in the allowed stack when one exists.

  Seed all randomness. Write assertion messages that teach. Each exercise's tests run on
  CPU in under a minute.
- **Verify before the learner sees anything.** For coded exercises, run the verification
  script: every untouched stub must fail and every reference solution must pass. A test
  that passes on the stub or fails on the solution is itself wrong. For worked problems,
  check that `solution.md` reaches the paper's own result (cite it) and covers every point
  the README asks for.

## Step 7: Tutor loop (one exercise at a time)

1. Introduce the exercise: its goal, the equation(s), which animation to rewatch, and how
   to check it (the exact test command, or "write your answer in `answer.md`").
2. The learner does the work. Don't edit their files unless they ask. When they report
   failures or ask for help, read their code or answer and the test output first.
3. Climb the hint ladder **one rung at a time**, only going up while they're still stuck:
   1. *Idea*: restate what must be shown or computed and ask a guiding question.
   2. *Equation*: point to the exact term, assumption, shape or unit that's off.
   3. *Specific*: name the operation, line or proof step ("you normalized over the wrong
      axis", "this step needs t ≫ 1").
   4. *Solution*: only when explicitly asked; then walk through it step by step.
4. When the tests pass or the answer holds up, also review it against the paper:
   numerical stability, silent assumptions, and differences from the paper. Ask one "why"
   question that checks understanding. Then mark the topic `learned` in the knowledge
   graph, with the evidence, and move to the next exercise.

Be encouraging and precise, and keep it short. The learner should do most of the thinking.

## Step 8: Final exercise

Build `exercises/NN_final_<name>/`, combining the earlier parts into the paper's central result:
- **Coded papers:** assemble the parts via `_load` and reproduce **one qualitative result**
  at laptop scale (a scaling law's exponent, the shape of a key figure, an alignment the
  model discovers). Be clear about what isn't reproduced. Tests check the claim with
  a threshold and a fixed seed. Time the reference solution: it must finish on CPU in
  under 5 minutes.
- **Theory papers:** a capstone worked problem that rebuilds the main theorem or argument
  from the concepts, with the paper's result as the target.

## After the final exercise: improvement ideas

Once step 8 is done, use the **paper-ideas** skill in learned-paper mode. It produces `papers/<slug>/ideas/ideas.md`:
the paper's weaknesses, open questions and follow-up directions, each tied to evidence and checked against later
literature. Show the top ideas and ask the learner which to explore. Approved ideas become "Open questions and
extensions" notes in `concept_graph.md`, and approved experiments build on the learner's own implementation. The
learner can also ask for ideas at any time.

## Knowledge graph

One Markdown + Mermaid file for everything the learner has learned, across all papers:
`~/researcher-pal/knowledge_graph.md`, unless the learner names another path. Create the
folder and file on first use. Read `references/knowledge_graph_template.md` for the
format and merge rules. In short:

- Topics are keyed by ID and merged across papers. Before adding a topic, look for an
  existing one with the same meaning under a different name.
- Status only moves forward: `known` (the learner says so, step 5), `learning` (exercise
  started, step 7), `learned` (tests passed or answer accepted, step 7). A learner can ask
  to reset a topic.
- Every topic lists the papers where it appeared. Never delete topics or other papers' rows.
- Update it at step 5 and after every exercise, and re-check that its Mermaid diagram renders.

When the learner asks what they've learned, show the map and the topics table from this file.
