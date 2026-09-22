# Scaling AI Context to Repo Size

Notes on when (and when not) to adopt heavier AI-navigation tooling as this repo grows, prompted by a
planner-model note the project owner brought in (see `OPTIMIZED_CONTEXT.md` at repo root for the original).
That note is written for codebases spanning "millions of tokens" — this doc calibrates its four ideas
against what this repo actually is today, and names the trigger points for revisiting each one.

## Reality check

As of 2026-09-22: **~1,900 lines of application code** (Java + Python + Go + TypeScript), 179 files total,
1.6 MB on disk. The entire codebase fits in a single model context window with room to spare — nowhere near
the scale the source note assumes. That matters, because the note's heavier techniques trade setup/ops cost
for the ability to *avoid* reading large amounts of code — a trade this repo doesn't need to make yet, and
one that would run against this repo's own stated preference for explicit code over abstractions and
frameworks it doesn't need (see e.g. `.claude/rules/gingonic.md` §3, `springboot.md` §1).

## The four ideas, evaluated against that

| # | Idea | Verdict today | Why |
|---|------|----------------|-----|
| 1 | **Repo Map** (tree + symbol skeletons) | **Keep doing the tree half; already have it** | `CLAUDE.md`'s "Directory structure" block *is* this — a hand-compressed, few-hundred-token view of the whole repo's layout. Cheap, high-value, no reason to stop. |
| 2 | **Semantic Indexing** (embeddings + Elasticsearch, vector + BM25 dual retrieval) | **Skip** | Means standing up and operating a search service — an embedding pipeline kept in sync with every commit, a cluster to run — for a codebase plain `grep` searches in milliseconds. Zero payoff at this size, real ongoing cost. |
| 3 | **Agentic Navigation Tools** (`search_symbol`, `read_file(start,end)`, `find_references`) | **Mostly already have it; one real gap, not urgent yet** | This is the exact pattern an agent already uses in this repo: keyword/pattern search (grep/glob) plus targeted reads of a file's specific lines. The one thing plain text search can't do that a real symbol index can is *precision* — telling "the `list_products` function" from "a string that happens to contain those words." At one implemented sandbox language, that's a non-issue. |
| 4 | **Graph-Based Intelligence** (SCIP/LSIF) | **Skip** | Built for codebases where "what calls this?" spans hundreds of files across services no one holds in their head at once — needs a per-language indexer (scip-java, scip-go, scip-python, scip-typescript) plus something to query the resulting graph. Real infrastructure, no problem here for it to solve yet. |

## Trigger points — when to revisit

Concrete, not vague "someday" markers:

- **Symbol-precise search (`ctags`)**: worth wiring in once `go`, `java`, and `typescript` sandbox API
  variants actually exist alongside the Python one (see `docs/current_state.md`) — at that point there are
  4 near-identical functions like `list_products`/`get_order_header` across languages, and grep's
  string-matching starts producing real false positives that a symbol-aware jump wouldn't. Until then it's
  optional polish, not a bottleneck.
  - **How, when it's time**: `universal-ctags` is a single static binary with no per-language setup beyond
    what it already ships — a `tags` file regenerated on demand gives near-free "go to definition." Cheap
    enough that it doesn't need its own design doc when the time comes; just install it and use it.
- **Semantic Indexing / RAG**: revisit if source LOC crosses roughly **50,000–100,000** lines, or if this
  becomes a genuine multi-repo setup — not before. Below that, a human (or an agent) can `grep` faster than
  they can write a good enough vector query, and there's no embedding-drift problem to manage.
- **Graph-based (SCIP/LSIF)**: revisit only if cross-service call graphs become genuinely hard to trace by
  reading code directly — realistically, past the point semantic indexing already became worth it, not
  before it.

## Keeping the repo map itself honest

The tree in `CLAUDE.md` is only as good as its last edit, and it has already gone stale twice in one
session — a directory marked "empty scaffold" that had since been filled in, and a one-line summary of
`docs/` that undercounted it by several files. That's a discipline gap, not a case for new infrastructure:
the fix is the [`update-repo-map`](../.claude/skills/update-repo-map/SKILL.md) skill (`.claude/skills/`),
invoked on demand (e.g. before a commit that changes top-level structure) to diff the block against the
real filesystem, correct stale claims, and report what changed — rather than a generated file with a CI gate,
which would be real enforcement but doesn't have anywhere to run yet (`docs/ci.md`'s pipeline is still only
planned). Worth reconsidering once that CI exists: add a "map is up to date" check there as a stronger,
enforced version of what the skill does on request today.

## Bottom line

Nothing in `OPTIMIZED_CONTEXT.md` is wrong for the codebase it's describing — it's just describing a
codebase two orders of magnitude bigger than this one. The right move now is the cheap, already-adopted
half of idea #1 (kept honest by the skill above), continuing to rely on plain search for #3, and leaving
#2 and #4 alone until one of the trigger points above actually fires.
