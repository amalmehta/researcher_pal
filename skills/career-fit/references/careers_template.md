# careers.md format

Copy the structure below into `~/researcher-pal/career/careers.md`. Everything in `<…>` gets replaced. Keep the
section order and the ID prefixes (C for companies, R for roles, S for sources): `check_careers.py` relies on them.

---

```markdown
# Career fit

> **As of <YYYY-MM-DD>.** Based on profile.md, <n> papers and <m> case studies in your library, and <k> learned
> topics in your knowledge graph. Openings change weekly: refresh before acting on one.

## Ikigai

| Circle | What we found | Evidence |
|---|---|---|
| What you love | <themes> | [library: <slug>], [profile] |
| What you're good at | <skills> | [kg: <topic id>], [profile] |
| What the world needs | <problems these organizations work on> | [S1], [S4] |
| What you can be paid for | <the role types that pay for it> | [S2], [S7] |

## Best fit

### 1. <Role (R#)> at <Company (C#)>
- **Love:** <why> [library: …] · **Good at:** <why> [profile]
- **World needs:** <why> [S#] · **Paid for:** <posting or role evidence> [S#]
- **Weakest circle:** <which, and why>
- **Next step:** <a paper to add to the library (title or arXiv ID), a skill, or a project>

## Companies you'd love to work at

### C1: <Company>
- **What they work on that matches you:** <…> [S#]
- **Why you:** <…> [library: …] [profile]
- **Openings:** <role title, location, read on YYYY-MM-DD> [S#] | no current posting found (checked YYYY-MM-DD)
- **Fit notes:** <constraints met or not; anything to watch>

## Roles you'd love

### R1: <Role type>
- **What it involves:** <…> [S#]
- **What it needs:** <…> [S#]
- **What you have:** <…> [profile] [kg: …]
- **Gaps:** <…>
- **Example postings:** <Company, title, date> [S#]

## Dropped

| Candidate | Why it was dropped |
|---|---|
| <Company> | <constraint from the profile, or weak fit> |

## Sources

| ID | Title | Publisher | Date read | URL |
|---|---|---|---|---|
| S1 | <page title> | <site> | <YYYY-MM-DD> | <https://…> |
```
