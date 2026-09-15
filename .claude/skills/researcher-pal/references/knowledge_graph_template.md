# Knowledge graph template and merge rules

One file holds everything the learner has learned, across every paper:
`~/researcher-pal/knowledge_graph.md` by default, or another path the learner names.
It answers "what do I know, where did I learn it, and how do the pieces connect?"

## Contents
1. File structure
2. Topic IDs and merging
3. Status rules
4. Update procedure
5. Mermaid rules for a growing graph

---

## 1. File structure

Keep these four sections in this order. Replace everything in `<…>`.

```markdown
# Knowledge graph

> Maintained by researcher-pal: one map of what you've learned, across all papers.
> **Status:** ✅ learned · 🔶 learning · ☑️ known before (you said so)
> **Last updated:** <YYYY-MM-DD>

## Map

Arrows go from prerequisite to topic. Colors show status; boxes group topics by field.

​```mermaid
flowchart LR
  classDef learned fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef learning fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef known fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e

  subgraph math["Mathematics and probability"]
    softmax["Softmax"]:::known
  end
  subgraph dl["Deep learning"]
    sdpa["Scaled dot-product attention"]:::learned
  end
  softmax --> sdpa
​```

## Topics

| Topic | Status | Field | Papers | Evidence | Updated |
|---|---|---|---|---|---|
| `sdpa`: Scaled dot-product attention | ✅ learned | Deep learning | [Attention Is All You Need](<relative or absolute path>/concept_graph.md#sdpa-scaled-dot-product-attention) | exercise 01 passed | <YYYY-MM-DD> |
| `softmax`: Softmax | ☑️ known | Mathematics and probability | Attention Is All You Need; <other paper> | said known at start | <YYYY-MM-DD> |

## Papers

| Paper | Folder | Started | Topics learned / concepts in paper |
|---|---|---|---|
| Attention Is All You Need (arXiv 1706.03762) | `<path>/papers/attention-is-all-you-need/` | <YYYY-MM-DD> | <n> / <m> |
```

Sort the Topics table by field, then by ID. Keep the Papers table in the order papers were started.

---

## 2. Topic IDs and merging

- A topic ID is a short, field-neutral `snake_case` name for **the idea**, not for the
  paper's notation: `softmax`, `power_law`, `mean_field_approximation`,
  `preferential_attachment`. Concept IDs in `concept_graph.md` use the same IDs, so the
  two files line up.
- **Before creating a topic, look for an existing one with the same meaning** under
  another name (`layer_norm` vs `layernorm`, `power_law_distribution` vs `power_law`).
  Reuse the existing ID, and add the paper to its Papers cell.
- If two papers use one word for different ideas, give them distinct IDs
  (`attention_ml` vs `attention_psychology`) and say how they differ in the label.
- Paper-specific concepts are topics too, e.g. `ba_model`. They just tend to appear in one paper.
- Only add a topic once it has a status (known, learning or learned). Concepts the learner
  hasn't touched stay in that paper's concept graph.
- Fields: use broad, stable names ("Mathematics and probability", "Deep learning",
  "Network science", "Statistical physics", "Algorithms"), and reuse existing ones.

---

## 3. Status rules

| Status | Set when | Evidence to record |
|---|---|---|
| ☑️ `known` | the learner says they already know it (step 5) | "said known at start of <paper>" |
| 🔶 `learning` | its exercise or worked problem has started (step 7) | "exercise NN started" |
| ✅ `learned` | its tests pass, or its worked problem is accepted, or it was covered inside a passed exercise and the learner answered its check-yourself question | "exercise NN passed", "problem NN accepted" |

- Status only moves forward (`known` → `learning` → `learned` is allowed; so is
  `known` → `learned`). Never downgrade on your own. If the learner asks to reset a
  topic, set it back and say so in Evidence.
- When a topic reappears in a new paper, keep its status and append the paper. A topic
  that is `known` or `learned` gets the `known` class in the new paper's concept graph.

---

## 4. Update procedure

1. Read the whole file (if it exists) before changing anything.
2. Merge: for each topic with a new or changed status, update its row (status, papers,
   evidence, date) or add it. Add prerequisite edges for any pair of topics that are both
   in the file, using the paper's concept graph edges. Never delete topics, edges, or other
   papers' rows.
3. Update the Papers row for the current paper (create it at step 5).
4. Regenerate the Mermaid map from the Topics table, so the two never disagree.
5. Update "Last updated", write the file, and check that the Mermaid diagram renders (same
   check as in step 3 of the skill).

---

## 5. Mermaid rules for a growing graph

- Use `flowchart LR` and one `subgraph` per field. Subgraph IDs are short `snake_case` IDs,
  and labels are quoted.
- Node IDs are the topic IDs. Labels are always in double quotes, with no LaTeX, `"`, `<` or `>`.
- Classes: `:::learned`, `:::learning`, `:::known`.
- Edge direction is prerequisite → topic. Draw an edge only if both ends are in the file.
- Past about 60 topics, a single map stops being readable. Keep the full map, but add one
  smaller map per field under a `### <Field>` heading, with edges into the field from
  other fields drawn to a grey stub node (`classDef external fill:#f1f5f9,stroke:#94a3b8,color:#334155`).
