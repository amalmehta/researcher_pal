# Researcher Pal.app

A Mac app for the reading side of this project: drop in a paper, and it studies it for you and then
suggests what would make it stronger.

It has no model of its own. It drives the `claude` command already installed on this Mac, with the three
skills in `skills/`, so there is **no API key and no separate billing** — it uses your Claude Code login.

## Build

```bash
app/make_app.sh --run
```

That produces `app/build/ResearcherPal.app` and opens it. Needs Xcode's Swift toolchain. Move the `.app`
to /Applications if you want it permanently.

## Before the first run

The app needs the CLI to be logged in. In Terminal:

```bash
claude
```

then type `/login` and follow the prompts. If the login has expired, the app shows an orange banner saying so.

## Using it

- **Add a paper:** drag a PDF anywhere into the window, use *Add PDF…*, or type anything that identifies it: an
  arXiv ID, a DOI, a link to its page (arXiv, a journal, OpenReview, ACL Anthology, PubMed Central, …) or its
  title. The app downloads an open-access copy right away and names the paper after its real title. It never gets
  around a paywall: if there's no open copy, it says what it tried, and you download the PDF yourself and drop it in.
  A title that matches several papers lists them so you can paste the right one's DOI or arXiv ID.
- **Study this paper** runs researcher-pal: a concept map, animations and exercises land in the paper's folder
  and show up in the tabs. The skill pauses to ask you things; answer in the box at the bottom.
- **Learn with a tutor** appears once a paper's material is built: the assistant keeps that material as it is,
  asks what you already know and where to start, then tutors you one exercise at a time and records what you
  learn in the knowledge graph.
- **Career fit** (top of the sidebar): write a few lines *About me*, press *Find my fit*, and the career-fit skill
  researches the companies and roles you'd love and your best fit (ikigai), from your library and profile. Every
  company and opening links its source and date; your profile never leaves the Mac (searches use keywords only).
- **Case studies** of real incidents sit in their own sidebar section. Each is built like a paper (concept map,
  animations, exercises) from numbered sources instead of a PDF; the Sources tab lists them.
- **Suggest improvements** runs paper-ideas on a paper you've studied and writes a ranked report you can read
  in the Ideas tab. It stops and asks before applying an edit or running an experiment.
- **Permission requests:** when the assistant wants to run a command (download the paper, extract its text, test
  an exercise) or change a file outside the paper's folder, a card shows exactly what, with *Allow*, *Allow all*
  (for the rest of the conversation) and *Deny*. The run waits until you answer.
- **Settings** (⌘,) chooses the model, whether files can be written without asking, whether commands ask first,
  run without asking or never run (studying a paper needs them), and a spending cap per run.

## Where things go

```
~/researcher-pal/
├── knowledge_graph.md          # topics across all papers, maintained by the skill
├── profile.md                  # About me, for Career fit
├── career/careers.md           # the latest career-fit report
├── case-studies/<slug>/        # same layout as a paper, with sources.md instead of paper.pdf
└── papers/<slug>/
    ├── paper.pdf               # what you dropped in, or the downloaded open-access copy
    ├── source.json             # for a download: title, DOI, arXiv ID and where the PDF came from
    ├── concept_graph.md        # Concept map tab
    ├── animations/*.html       # Animations tab
    ├── exercises/NN_*/         # Exercises tab
    └── ideas/ideas.md          # Ideas tab
```

Nothing is hidden in an app container: it's plain files you can open, edit and back up.

## Shape of the code

| File | What it does |
|---|---|
| `Sources/ResearcherPal/Library.swift` | Finds papers on disk, adds PDFs and arXiv IDs |
| `Sources/ResearcherPal/ClaudeRunner.swift` | Runs `claude -p --output-format stream-json`, turns the stream into a transcript, resumes the session when you reply |
| `Sources/ResearcherPal/WebPane.swift` | Renders Markdown (with equations and diagrams) and animations in a web view |
| `Sources/ResearcherPal/ResearcherPalApp.swift` | Window, library sidebar, tabs, run panel, settings |
| `make_app.sh` | Builds and assembles the `.app` bundle |
| `make_icon.swift` | Draws the app icon (a page with a concept graph); `make_app.sh` turns it into `AppIcon.icns` |

## Known limits

- **Not signed or notarized.** It's ad-hoc signed for this Mac. Another Mac will refuse it until you sign it
  properly or right-click → Open.
- **Long runs block on questions.** The skills pause by design; if a run looks stalled, it is usually waiting
  for your answer in the box.
- **Writing a paper (paper-writer) is not in the app yet** — that workflow needs its own screens for results,
  code and drafts. Use Claude Code for it.
