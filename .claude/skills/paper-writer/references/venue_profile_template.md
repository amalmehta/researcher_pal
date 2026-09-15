# Venue profile template

A venue profile records what the skill needs to tailor a paper to one venue. Built-in profiles live in
`references/venues/`. For any other venue, build one from its call for papers (CFP) with this template and
save it as `paper/<slug>/<venue>/venue.md`.

**Rules change every year.** A profile is a starting point, never the authority. At P2, re-read the
current CFP and author guide, correct the profile, and list every change in `venue_report.md`.

## How to build or refresh a profile

1. Find the official pages: the call for papers, the author guide or handbook, the LLM/AI policy, and
   the style-file download. Use the venue's own domain (e.g. `iclr.cc`, `neurips.cc`, `icml.cc`), never a
   third-party template mirror.
2. Download the official template zip into `paper/<slug>/<venue>/template/`. Compile its example file
   unchanged with Tectonic to confirm it builds.
3. Measure the real text dimensions by adding this probe to a copy of the example file and compiling:
   ```latex
   \typeout{PW-DIMENSIONS textwidth=\the\textwidth\space columnwidth=\the\columnwidth\space textheight=\the\textheight}
   ```
   Read the values from the log. Figures are sized from these numbers, not from memory.
4. Fill in every field below. Give each rule a source link and a short quote when you can. If you can't
   find a field, write `unknown` and ask the researcher. Never guess.

## Fields

```markdown
# <Venue> <year>

> **Cycle:** <which year's rules these are> · **Last checked:** <YYYY-MM-DD>
> **Sources:** [CFP](<url>) · [Author guide](<url>) · [AI policy](<url>) · [Style files](<url>)

## Deadlines
| Item | Date (time zone) |
|---|---|
| Abstract | |
| Full paper | |
| Supplementary material | |

## Length and layout
| Field | Value | Source quote |
|---|---|---|
| Main-text page limit (submission) | | |
| Page limit (camera-ready) | | |
| Not counted toward the limit | references / appendix / statements / checklist | |
| Columns | one / two | |
| \textwidth, \columnwidth (measured) | | from the probe |
| Body font and size | | |
| Paper size | US Letter / A4 | |
| Max PDF size | | |

## Template
| Field | Value |
|---|---|
| Download URL | |
| Main style file | |
| Anonymous (submission) option | |
| Camera-ready option | |
| Preprint option | |
| Citation style | natbib author-year / numeric, which commands |
| Caption placement | figure captions below? table captions above? |

## Anonymity
- <rules for author info, self-citation, acknowledgements, code links, supplementary material>

## Required and recommended sections
| Section | Required? | Where it goes | Counts toward limit? |
|---|---|---|---|
| e.g. Impact statement / AI use statement / Limitations / Checklist | | | |

## LLM / AI-use policy
- <what's allowed, what must be disclosed and where; quote the key sentences>

## Supplementary material
- <format, size, deadline, anonymization>

## Reviewer expectations (slow-changing conventions)
- <what this community tends to reward and penalize, e.g. ablations, error bars, theory, clarity>
- Mark anything that's convention rather than written rule as **convention**.

## Other policies
- <paper caps per author, reciprocal reviewing, dual submission, prompt-injection bans>
```

## Using a profile

- **P2:** compare the profile with the current CFP. Update the profile and record each difference in `venue_report.md`.
- **P3:** size the outline to the page limit and required sections.
- **P4:** use the measured widths with `assets/figure_style.py`.
- **P7:** `scripts/check_paper.py` reads the page limit and anonymity settings you pass it from the profile.
