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

- **Add a paper:** drag a PDF anywhere into the window, use *Add PDF…*, or paste an arXiv ID or link.
- **Study this paper** runs researcher-pal: a concept map, animations and exercises land in the paper's folder
  and show up in the tabs. The skill pauses to ask you things; answer in the box at the bottom.
- **Suggest improvements** runs paper-ideas on a paper you've studied and writes a ranked report you can read
  in the Ideas tab. It stops and asks before applying an edit or running an experiment.
- **Settings** (⌘,) chooses the model, whether files can be written without asking, whether commands may run
  (needed for coded exercises), and a spending cap per run.

## Where things go

```
~/researcher-pal/
├── knowledge_graph.md          # topics across all papers, maintained by the skill
└── papers/<slug>/
    ├── paper.pdf               # what you dropped in (or .arxiv holding an ID)
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
