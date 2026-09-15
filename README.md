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
   for s in researcher-pal paper-writer paper-ideas; do ln -s "$PWD/.claude/skills/$s" ~/.claude/skills/$s; done
   ```

3. Open Claude Code and say one of the phrases above.

**Requirements:**
- Claude Code.
- Python 3.9+ for the exercises and scripts, plus PyTorch for machine-learning papers.
- [Tectonic](https://tectonic-typesetting.github.io) if you want to compile papers.

## What's in the repo

| Folder | Contents |
|---|---|
| `.claude/skills/` | The three skills |
| `examples/attention-is-all-you-need/` | A full learning run: concept map, 4 animations, 12 exercises |
| `examples/barabasi-albert-scaling/` | A learning run on a non-ML paper, plus improvement ideas and an experiment |
| `examples/paper-toy-transformer-ablation/` | A short example paper built for NeurIPS and ICLR, plus improvement ideas and an experiment |
| `examples/knowledge_graph.md` | Topics learned across both papers |
| `site/` | A static site for browsing the examples |
| `researcher_pal.md` | The full spec and changelog |

The example papers' PDFs aren't included. Download them from arXiv:
[1706.03762](https://arxiv.org/abs/1706.03762) and [cond-mat/9910332](https://arxiv.org/abs/cond-mat/9910332).

## Browse the examples

```bash
python3.9 site/build_site.py
```

Then run `python3 -m http.server 8765` and open http://localhost:8765/site/dist/index.html.

## Good to know

- **Literature search is rate-limited:** it uses free public APIs, and arXiv and Semantic Scholar often throttle requests, so results may come only from Crossref.
- **Nothing runs without approval:** paper-ideas never edits a paper or runs an experiment until you say so.
- **Example inputs are partly simulated:** the researcher's notes and draft in the example paper are made up, but its results come from real training runs.
