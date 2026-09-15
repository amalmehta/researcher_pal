# Concept graph template

Copy the structure below into `papers/<slug>/concept_graph.md`. Everything in `<…>`
gets replaced. Keep the section order: overview first, then the map, coverage table and
concepts. Learners scan the map, then dive into entries.

Concept IDs are the same as the learner's knowledge graph topic IDs
(`references/knowledge_graph_template.md`, section 2). Reuse an existing topic's ID when
the paper uses that idea, and give it the `known` class if its status is `known` or
`learned`. The example below is from an ML paper, but the structure is the same for any
field. Swap "Shape" for "Units" or "Type" where that fits better.

---

```markdown
# <Paper title>: concept graph

> **Source:** <arXiv ID + version, or file name>, <authors>, <year>. Section, equation and
> table numbers refer to this version.
> **Legend:** **not in paper** = common practice or inference, not stated by the authors.
> 🎬 = has an interactive animation.

## The paper in five lines

<What problem it solves, the key idea, what is new, the headline result, and what to
watch out for. Five short lines at most.>

## Map

Arrows go from prerequisite to concept. Start from the grey nodes you don't know yet.

​```mermaid
flowchart TD
  classDef prereq fill:#eceff1,stroke:#90a4ae,color:#263238
  classDef core fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
  classDef novel fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef known fill:#dcfce7,stroke:#16a34a,color:#14532d

  subgraph S3["§3 Model"]
    sdpa["Scaled dot-product attention 🎬"]:::novel
  end
  softmax["Softmax"]:::prereq
  softmax --> sdpa
​```

## Coverage

Every item from the paper inventory appears here. An item with no concept is a gap to fix.

| Paper item | What it is | Concept(s) |
|---|---|---|
| §3.2.1, Eq. (1) | scaled dot-product attention | [sdpa](#sdpa-scaled-dot-product-attention) |
| Table 3 | model variations | [...](#...) |

## Concepts (dependency order)

### <concept-id>: <Concept name>

- **Kind:** prerequisite | core | novel
- **Source:** §x.y, Eq. (n), Fig. k, Table t
- **Depends on:** [<id>](#anchor), … · **Outside prerequisites:** <e.g. matrix multiplication>
- **Animation:** [animations/<concept-id>.html](animations/<concept-id>.html)  ← only if one exists
- **Exercise:** `exercises/NN_<concept-id>/`  ← added in step 6

**Intuition.** 2–4 sentences: the problem this solves and the picture to hold in
your head.

**The math.**

$$
<equation exactly as in the paper>
$$

| Symbol | Meaning | Shape |
|---|---|---|
| $Q$ | queries, one row per position | $(n, d_k)$ |

**Nuances and gotchas.**
- <A choice the paper makes in passing that matters, with a citation.>
- <What you must decide that the paper doesn't say.> **not in paper**
- <The classic implementation bug for this concept.>

**Check yourself.** <One or two questions whose answers show real understanding, not recall.>
```

---

## Mermaid rules (renderers are strict, so follow these)

- Use `flowchart TD`. Node IDs are short `snake_case`. Never use the IDs `end`, `graph`,
  `subgraph`, `style`, `class`, `click`, or IDs starting with `o`/`x` right after
  `--` (e.g. `A --o1` parses as a circle edge).
- **Always** put labels in double quotes: `id["Label (with parens)"]`. Don't put `"`
  inside a label; use `#quot;`. Avoid `<` and `>`; write `#lt;`/`#gt;` or use words.
- Don't use LaTeX in node labels. Write `sqrt(d_k) scaling`, not `$\sqrt{d_k}$`.
- Apply classes with `:::prereq`, `:::core`, `:::novel` or `:::known`.
- Past about 15 nodes, group them into `subgraph` blocks named after paper sections, so
  the map mirrors how the paper is organized.
- Mark animated concepts with ` 🎬` at the end of the label, inside the quotes.
- The GitHub anchor for `### sdpa: Scaled dot-product attention` is
  `#sdpa-scaled-dot-product-attention` (lowercase, spaces become `-`, punctuation dropped).

## Math in Markdown

Use `$…$` inline and `$$…$$` on their own lines for display math (renders on GitHub and
in VS Code). Copy equations from the LaTeX source when available. Give every symbol a
row in the table, with its tensor shape. Shapes are where implementations break.
