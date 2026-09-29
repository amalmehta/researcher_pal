# Researcher Pal

Three [Claude Code](https://claude.com/claude-code) skills for working with research papers.

| Skill | What it does | Try saying |
|---|---|---|
| **researcher-pal** | Teaches you a paper: a concept map, interactive animations, and exercises that rebuild the method | "help me learn arXiv 1706.03762" |
| **paper-writer** | Helps you write your own paper for a specific venue (NeurIPS, ICML, ICLR or any other), with figures, tables and checked citations | "help me write my paper for NeurIPS" |
| **paper-ideas** | Suggests ranked ways to improve a paper and, with your approval, applies edits or runs experiments | "suggest improvements for my paper" |

## Install

1. Clone this repo.
2. Link the skills so Claude Code can use them from any folder:

   ```bash
   mkdir -p ~/.claude/skills && for s in researcher-pal paper-writer paper-ideas; do ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s; done
   ```

3. Open Claude Code and say one of the phrases above.

**Requirements:**
- Claude Code.
- Python 3.9+ for the exercises and scripts, plus PyTorch for machine-learning papers.
- [Tectonic](https://tectonic-typesetting.github.io) if you want to compile papers.

## What's in the repo

| Folder | Contents |
|---|---|
| `skills/` | The three skills, linked into ~/.claude/skills by the install step |
| `examples/attention-is-all-you-need/` | A full learning run: concept map, 4 animations, 12 exercises |
| `examples/barabasi-albert-scaling/` | A learning run on a non-ML paper, plus improvement ideas and an experiment |
| `examples/paper-toy-transformer-ablation/` | A short example paper built for NeurIPS and ICLR, plus improvement ideas and an experiment |
| `examples/knowledge_graph.md` | Topics learned across both papers |
| `app/` | The Mac app: drop a paper in and study it |
| `site/` | A static site for browsing the examples |
| `tests/`, `tools/` | Unit tests for the skills' scripts, and the check runner |
| `evals/` | How the learning skill is evaluated against papers it has never seen |
| `researcher_pal.md` | The full spec and changelog |

MIT licensed (see `LICENSE`). The papers' own text belongs to their authors.

The example papers' PDFs aren't included. Download them from arXiv:
[1706.03762](https://arxiv.org/abs/1706.03762) and [cond-mat/9910332](https://arxiv.org/abs/cond-mat/9910332).

## Browse the examples

```bash
python3.9 site/build_site.py
```

Then run `python3 -m http.server 8765` and open http://localhost:8765/site/dist/index.html.

## Checks

Everything the repo can verify runs from one script (CI runs the same one):

```bash
tools/checks.sh
```

It runs the unit tests for the skills' scripts, checks both example idea reports, builds the site, runs the
exercise tests (the stubs must fail and the reference solutions must pass), compiles both example papers and
re-runs every figure and value script to confirm the papers still match their data. `tools/checks.sh --quick`
skips the paper compile and the PyTorch exercises.

## Good to know

- **Literature search is rate-limited:** it uses free public APIs, and arXiv and Semantic Scholar often throttle requests, so results may come only from Crossref.
- **Nothing runs without approval:** paper-ideas never edits a paper or runs an experiment until you say so.
- **Example inputs are partly simulated:** the researcher's notes and draft in the example paper are made up, but its results come from real training runs.
