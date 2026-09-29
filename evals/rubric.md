# Evaluation rubric: learning material for a paper

Used to compare two sets of learning material for the same paper, blind (labelled X and Y), against the
paper's own text. Each criterion scores 0–3. The paper text is the only authority: a claim that contradicts
it is wrong even if it sounds right.

| # | Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| 1 | **Coverage of the central result** | misses it | mentions it without its derivation or conditions | covers it and most supporting steps | covers it, its derivation, and the conditions it needs |
| 2 | **Faithfulness** | fabricates results, citations or equations | several statements the paper doesn't support | minor imprecision only | every checked claim traces to the paper |
| 3 | **Prerequisite structure** | no ordering | a flat list | dependencies mostly explicit | explicit dependency order a newcomer can follow, with prerequisites named |
| 4 | **Exercises** | absent or unrelated | recall questions | target the method; solutions present | target the central result, are doable from the material, and the solutions are correct (checked) |
| 5 | **Honesty about limits** | none | vague hedging | notes some assumptions | flags what is assumed vs. derived, what the authors themselves call an ansatz, what was not read, and notation traps |
| 6 | **Usability** | unusable | a wall of text | organized and navigable | organized, navigable, and each part says what it is for |

**Fabrication is the one disqualifier.** A fabricated equation, result or citation caps criterion 2 at 0 and
must be quoted in the report, because the whole method rests on never inventing anything.

## Method
- Three papers published after the assistant's training cutoff, so neither condition can recall them.
- Two conditions per paper: **with the skill** (follow `researcher-pal/SKILL.md`) and **baseline** (same task,
  no skill), same model, same bounded scope, paper text supplied locally so neither side can fetch extras.
- A separate grader scores both blind, spot-checking at least three factual claims per side against the paper.
- Reported as per-criterion scores plus the grader's overall preference and reasoning.

## Known limits of this evaluation
- Three papers, one run each: differences of one point on one criterion are noise.
- The grader is an AI model, not a subject expert or a real learner. It checks faithfulness against the text;
  it cannot tell you whether the material actually teaches a human.
- Scope was bounded (concept map, three exercises, stuck points) so runs stay comparable. Animations,
  test harnesses and the cross-paper knowledge graph are not exercised here.
