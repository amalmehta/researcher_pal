# ICML 2026 (latest official cycle)

> **Cycle:** ICML 2026 rules. The ICML 2027 call for papers was not yet on icml.cc when checked
> (`/Conferences/2027/CallForPapers` returned 404). Third-party deadline lists put ICML 2027 full papers in late
> January 2027, but that is **unverified**, so check again at P2. · **Last checked:** 2026-09-15
> **Sources:** [Call for papers](https://icml.cc/Conferences/2026/CallForPapers) · [Author instructions](https://icml.cc/Conferences/2026/AuthorInstructions) · [Style files](https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip) · [Example paper](https://media.icml.cc/Conferences/ICML2026/Styles/example_paper.pdf) · [LLM policy](https://icml.cc/Conferences/2026/LLM-Policy)

## Deadlines (2026 cycle, for reference)
| Item | Date |
|---|---|
| Abstract | Jan 23, 2026 AoE |
| Full paper | Jan 28, 2026 AoE |

## Length and layout
| Field | Value | Source |
|---|---|---|
| Main-body page limit (submission) | 8 pages | CFP, author instructions |
| Page limit (camera-ready) | 9 pages | CFP, author instructions |
| Not counted | references, impact statement, acknowledgements, appendices | CFP, template |
| Columns | two; overall width 6.75 in, 0.25 in gap, height 9 in | template |
| \textwidth / \columnwidth (measured) | 487.82 pt / 234.88 pt | probe on the official template |
| Body font | 10 pt Times, 11 pt leading | template |
| Paper size | US Letter only | author instructions |
| Max PDF size | 50 MB at submission, 20 MB camera-ready | CFP, author instructions |

**Discrepancy:** the template's example text still says the total file size "may not exceed 10MB". The CFP and
author instructions say 50 MB. Follow the CFP, but keep PDFs small anyway.

## Template
| Field | Value |
|---|---|
| Main files | `icml2026.sty`, `icml2026.bst`, `algorithm.sty`, `algorithmic.sty`, `fancyhdr.sty`, shell `example_paper.tex` |
| Submission (anonymous) | `\usepackage{icml2026}`: author info is written with `\icmlauthor` and hidden automatically |
| Camera-ready | `\usepackage[accepted]{icml2026}` |
| Preprint | `\usepackage[preprint]{icml2026}` |
| Required commands | `\icmltitlerunning{}`, the `\twocolumn[ ... ]` title block, `\printAffiliationsAndNotice{}` (keep it, even empty) |
| Citations | natbib APA via `icml2026.bst`: `\cite{}` parenthetical, `\yrcite{}` for year only after naming authors |
| Captions | figure captions *below*; table captions *above*; no titles inside figure graphics |
| Abstract | one paragraph, ideally 4–6 sentences |
| Figures | vector PDF for plots; lines at least 0.5 pt; wide figures with `figure*` at the top or bottom of the page |

## Anonymity
- No author information in the submission (the style hides `\icmlauthor` unless `[accepted]` is set).
- Self-citations in the third person; don't anonymize the reference list itself (except unpublished manuscripts,
  which are then submitted anonymized as supplementary material).
- No acknowledgements, grant numbers, or code links that reveal identity; anonymize supplementary code, including
  names in licenses.
- Preprints and talks are fine, but don't advertise the work as an ICML submission during review.

## Required and recommended sections
| Section | Status | Where | Counts toward the limit? |
|---|---|---|---|
| Impact Statement | **required** (main track) | unnumbered section at the end, next to acknowledgements, before references | no |
| Financial conflict disclosure | required if applicable | last paragraph of the introduction | yes (it's in the body) |
| Lay summary | required, in the OpenReview form (4–6 sentences) | submission form, not the PDF | — |
| Accessibility | recommended practices (color-blind-safe figures, inclusive language) | throughout | — |

The template gives a verbatim boilerplate impact statement for papers without specific societal concerns. Use it only when that is true.

## LLM policy
- Generative AI may be used for writing and research, and the authors take full responsibility for all content.
- LLMs cannot be authors.
- Prompt injection is "strictly forbidden and will result in desk rejection."
- No mandatory in-paper AI disclosure was found in the 2026 CFP. Re-check at P2 and follow any disclosure the current cycle asks for.

## Supplementary material
- Supplementary manuscripts and code/data, due at the same deadline as the paper, anonymized.
- No supplementary material with the camera-ready version; the appendix goes in the main PDF.

## Reviewer expectations (**convention**)
- Technical depth and precision; theory is common and welcome; experiments should be clean and well controlled.
- Two-column density: concise prose, compact figures at column width, and tables that fit one column where possible.

## Other policies
- An author can be designated as the reciprocal reviewer for at most 2 of their submissions. Authors with 4 or more
  submissions must serve as reviewers.
- Camera-ready PDFs must pass the ICML format checker (papercheck.icml.cc).
