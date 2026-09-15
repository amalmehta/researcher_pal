# ICLR 2027

> **Cycle:** ICLR 2027 · **Last checked:** 2026-09-15
> **Sources:** [Call for papers](https://iclr.cc/Conferences/2027/CallForPapers) · [Author guidelines](https://iclr.cc/Conferences/2027/AuthorGuidelines) · [AI policy for authors](https://iclr.cc/Conferences/2027/AIPolicyForAuthors) · [Style files](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip) · [Submission policies blog post](https://blog.iclr.cc/2026/09/02/submission-policies-for-iclr-2027/)
>
> Re-verify everything at P2. This is a snapshot.

## Deadlines
| Item | Date |
|---|---|
| Abstract | Sep 18, 2026, 11:59 PM AoE |
| Full paper | Sep 25, 2026, 11:59 PM AoE |

## Length and layout
| Field | Value | Source |
|---|---|---|
| Main-text page limit (submission) | 9 pages, "strictly enforced" | author guidelines, template |
| Page limit (rebuttal / camera-ready) | 10 pages | author guidelines |
| Not counted | references, appendices, AI use statement, ethics statement, reproducibility statement, acknowledgements | author guidelines, template |
| Columns | one | template |
| Text block | 5.5 in × 9 in; left margin 1.5 in | template ("33 picas wide and 54 picas long") |
| \textwidth / \columnwidth (measured) | 397.48 pt / 397.48 pt | probe on the official template |
| Body font | 10 pt Times, 11 pt leading; paragraphs separated by ½ line, no indent | template |
| Paper size | US Letter | template |

## Template
| Field | Value |
|---|---|
| Main files | `iclr2027_conference.sty`, `iclr2027_conference.bst`, shell `iclr2027_conference.tex`, optional `math_commands.tex` |
| Submission (anonymous) | keep `%\iclrfinalcopy` commented out |
| Camera-ready | uncomment `\iclrfinalcopy` |
| Compiling with Tectonic | add `\usepackage[T1]{fontenc}` after `\usepackage{iclr2027_conference,times}` in `main.tex`. Without it, XeTeX's default TU encoding has no Times shapes, and bold, italics and small caps are substituted (found 2026-09-15) |
| Citations | natbib author-year: `\citet{}` in running text, `\citep{}` parenthetical |
| Captions | figure caption *after* the figure; table title *before* the table; both lower case except first word and proper nouns |
| Order at the end | AI use statement → ethics statement → reproducibility statement → (author contributions, acknowledgements) → references → appendix |

## Anonymity
- Double blind: "any paper where author identity is revealed in either the main text or the supplementary material will be desk rejected."
- Non-anonymous arXiv versions are allowed; cite them in the third person.
- Reporting results on a public challenge leaderboard is allowed.
- Papers are de-anonymized at the end of review (reviews and discussion become public on OpenReview).

## Required and recommended sections
| Section | Status | Where | Counts toward the limit? |
|---|---|---|---|
| AI use statement | **required**, ≤ 1 page | unnumbered, end of main text before references | no |
| Ethics statement | recommended (needed if there are ethics concerns), ≤ 1 page | end of main text before references | no |
| Reproducibility statement | recommended, about a paragraph pointing to where the details are | end of main text before references | no |

## AI-use policy (summary; read the full policy at P2)
- Disclosure is required in the paper **and** in the OpenReview submission form, and the two must match.
- *Required-disclosure* tasks include generating synthetic datasets, formulating claims or hypotheses, help with proofs,
  designing experiments, implementing methods, cleaning datasets and interpreting results.
- *Recommended-disclosure* tasks include drafting parts of the paper, creating or modifying figures, editing for
  readability, formatting references, suggesting structure and proposing a title. **Using this skill falls here, so disclose it.**
- The template's statement ends with the authors taking responsibility for all AI-assisted content. An LLM-produced
  falsehood, plagiarism or misrepresentation is treated as a Code of Ethics violation.

## Supplementary material
- The appendix goes after the references in the same PDF; reviewers aren't required to read it.
- Code submission is encouraged and must be anonymized.

## Reviewer expectations (**convention**)
- Strong empirical evidence with ablations and clear baselines; reviewers probe whether gains survive controls.
- Clarity matters: reviews and author discussion are public.
- Representation learning and deep learning audience; theory papers are welcome but should connect to practice.

## Other policies
- At most 20 submissions per author. Authors with no prior major-venue publications are limited to one submission
  without a qualified reciprocal reviewer among its authors.
- A reciprocal reviewing requirement applies (see the blog post).
