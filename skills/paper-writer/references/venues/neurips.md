# NeurIPS 2026 (latest official cycle)

> **Cycle:** NeurIPS 2026 rules (the 2026 deadlines have passed; the NeurIPS 2027 call wasn't published when checked).
> · **Last checked:** 2026-09-15
> **Sources:** [Call for papers](https://neurips.cc/Conferences/2026/CallForPapers) · [Main track handbook](https://neurips.cc/Conferences/2026/MainTrackHandbook) · [Paper checklist guidelines](https://neurips.cc/public/guides/PaperChecklist) · [Style files](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip) · [Code submission policy](https://neurips.cc/public/guides/CodeSubmissionPolicy)

## Deadlines (2026 cycle, for reference)
| Item | Date |
|---|---|
| Abstract | May 4, 2026 AoE |
| Full paper | May 6, 2026 AoE |
| Notification | Sep 24, 2026 AoE |

## Length and layout
| Field | Value | Source |
|---|---|---|
| Content page limit (submission) | 9 pages **including figures and tables**; "Papers that exceed the page limit will not be reviewed" | template, handbook |
| Page limit (camera-ready) | 10 pages | handbook |
| Not counted | acknowledgments, references, checklist, optional technical appendices | template |
| Columns | one | template |
| Text block | 5.5 in × 9 in; left margin 1.5 in | template |
| \textwidth / \columnwidth (measured) | 397.48 pt / 397.48 pt | probe on the official template |
| Body font | 10 pt Times, 11 pt leading; paragraphs separated by ½ line, no indent | template |
| Paper size | US Letter | template |
| Fonts | only Type 1 or embedded TrueType (no Type 3) | template |
| Max PDF size | 50 MB | handbook |

## Template
| Field | Value |
|---|---|
| Main files | `neurips_2026.sty`, shell `neurips_2026.tex`, `checklist.tex` |
| Submission | `\usepackage{neurips_2026}` (= `main` track): anonymized, with line numbers |
| Track options | `main`, `position`, `eandd`, `creativeai`, `sglblindworkshop`, `dblblindworkshop` (+ `\workshoptitle{}`), `education` |
| Camera-ready | add `final` to the track, e.g. `[main, final]` |
| Preprint | `[preprint]`: non-anonymous, "Preprint. Work in progress." footer; don't name the conference |
| Citations | natbib loaded by default; author-year or numeric, consistently. `\citet` inline. `nonatbib` if it clashes |
| Captions | figure caption *after* the figure; table caption *before* the table; tables without vertical rules (booktabs) |
| Acknowledgments | inside the `ack` environment, which hides it automatically in anonymized submissions |
| End matter order | main text → (ack) → references → appendices → **checklist** (`\input{checklist.tex}` after `\newpage`) |
| Math | use LaTeX display environments, not `$$`, so line numbers work |

## Anonymity
- All submissions are anonymized, with no identifying information.
- Self-citation in the third person ("In the previous work of Jones et al. [4]"). For your own unpublished papers, cite
  "A. Anonymous" and put an anonymized copy in the supplementary material.
- No acknowledgments at submission (use the `ack` environment).
- External links must allow anonymous browsing.
- Non-anonymous preprints are allowed, but aggressive advertising of the submission may be a violation.

## Required sections
| Section | Status | Where | Counts toward the limit? |
|---|---|---|---|
| **NeurIPS paper checklist** | **required**: "papers not including the checklist will be desk rejected" | after references and appendices | no |
| Limitations | encouraged (checklist item 2; a separate "Limitations" section recommended) | main text | yes |
| Broader impacts | not a required section, but consider negative societal impacts (checklist item 10) | anywhere in the paper | yes if in the main text |
| Funding and competing interests | required in the camera-ready version | acknowledgments | no |

**Checklist rules:** 16 items (claims, limitations, theory, reproducibility, open access, experimental details,
statistical significance, compute, code of ethics, broader impacts, safeguards, licenses, new assets, human subjects,
IRB, LLM usage). Answer each with `\answerYes{}`, `\answerNo{}` or `\answerNA{}` plus a 1–2 sentence justification that
points to sections. Delete the instruction block, but keep the heading, questions and guidelines unmodified. Checklist
answers are visible to reviewers and published with the paper. "No" with a good justification is acceptable.

## LLM policy
- LLMs may assist with writing or research, and authors are responsible for all content, including anything that could be
  plagiarism or misconduct. LLMs can't be authors.
- Describe LLM use in the experimental setup only if it's an important, original or non-standard part of the method.
  Checklist item 16 says writing, editing or formatting help doesn't need a declaration.
- Prompt injection aimed at LLM reviewers is forbidden and leads to desk rejection.

## Supplementary material
- Technical appendices go in the same PDF, with no page limit, but the paper must stand alone ("adding critical
  experiments that support the main claims to an appendix is inappropriate").
- Code and data go in one anonymized ZIP of up to 100 MB. The code guidelines ask for training and evaluation code plus dependencies.

## Reviewer expectations (**convention**)
- Significance for a broad ML audience, plus rigor that the checklist makes explicit: error bars with a stated method,
  compute resources, limitations. Reviewers are told not to penalize honest limitations.
- Clear claims in the abstract and introduction that match the evidence (checklist item 1).

## Other policies
- Every author needs an OpenReview profile at submission.
- A paper can't be submitted to more than one track, and track choice can't be switched.
- Reciprocal reviewing and dual-submission policies are in the handbook.
