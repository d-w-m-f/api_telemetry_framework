---
name: "map-contexts"
description: "Propose Bounded Contexts from interview.md and requirements.md, and — after explicit approval — write contexts.md and create the context folders."
argument-hint: "Optional focus, e.g. 'reconsider only the reporting side'"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); requires at least one /interview and one /map-requirements run"
metadata:
  author: "dddkit"
  source: "plan/005_map-contexts.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Prerequisites

Refuse to proceed, and say so plainly, unless **both** exist:
- `specs/brainstorm/interview.md`
- `specs/brainstorm/requirements.md`

Direct the user to `/interview` and/or `/map-requirements` if either is missing.

## Goal

Identify the project's Bounded Contexts from `interview.md` + `requirements.md`, get explicit human approval, then write `specs/BoundedContexts/contexts.md` and create the corresponding folders. This is the highest-blast-radius skill in the SDK — it shapes the whole tree everything else builds on — so every write here is gated by approval and, once a context is approved, it is never silently renamed, merged, or deleted by a later run of this same skill.

## Outline

1. Read `interview.md` and `requirements.md` in full.

2. Read the current state:
   - `specs/BoundedContexts/contexts.md`, if it exists (parse Bounded Context names the same way `.dddkit/scripts/validate-ddd.py` does: backtick-wrapped `` `PascalCaseWord` `` tokens anywhere in the file).
   - Existing `PascalCase` folders directly under `specs/BoundedContexts/`.

3. **Analyze and propose**:
   - Candidate Bounded Contexts derived from the interview/requirements content, each with a one-line focus statement (per `.dddkit/templates/context-map.md`'s per-context fields: Focus, Complexity, Volatility, Typical Implementation).
   - **Existing drift**, if any: a context named in `contexts.md` with no matching folder, or a folder with no matching entry in `contexts.md` (exactly what `validate-ddd.py` check 3 flags). Propose the additive fix for each — create the missing folder, or add the missing `contexts.md` entry (asking the user for its focus/description if it's an existing folder with real content to describe) — never propose deleting a folder or removing an entry.
   - If a proposed new context looks like it overlaps significantly with an existing one, say so and ask whether it should be folded into the existing context instead of created separately — do not decide this silently either way.

4. **Wait for explicit approval** of the full proposal (new contexts + drift fixes) before writing anything. This is non-negotiable per `DDD.md` section 4.

5. **On approval, apply only additive changes**:
   - Append new Bounded Context subsections to `contexts.md` (or create the file from `.dddkit/templates/context-map.md` if it doesn't exist yet) — every context name backtick-wrapped, matching the existing convention.
   - Create missing `PascalCase` folders under `specs/BoundedContexts/` — folders only, no `domain.md`/`vocabulary.md`/module content. That is `/model-context`'s job.
   - **Never** rewrite, rename, merge, or delete an existing context's subsection or folder in this step, even if the approved proposal implied a rename — if the user wants an existing context renamed or merged, that is a manual migration outside this skill's scope; say so explicitly rather than attempting it.
   - **Version the file**: new file, `version: 1.0.0`. Appending to an existing `contexts.md` is a MINOR bump (`DDD.md` section 5: adding a Bounded Context is MINOR) — bump it and prepend a Sync Impact Report noting which context(s) were added and which drift items were reconciled. A run that only reconciles drift (adds a missing entry/folder for something that already existed) without introducing a brand-new context is still a MINOR bump — the file's content changed, even if no new concept did.

6. Update the **How to Map New Functionality** section of `contexts.md` with a one-line decision rule per context, if it's missing or clearly stale after this run's additions.

## Behavioral Rules

- Never create a module folder, `domain.md`, or `vocabulary.md` — strictly the context layer.
- Never touch an existing Bounded Context's folder or `contexts.md` subsection beyond what was explicitly approved this run.

## Completion Report

- The approved context list (new + reconciled), and which folders were created.
- Any proposal the user did not approve, left for a future run.
- Suggested next step: `/model-context` for each new context.

## Done When

- [ ] `contexts.md` accurately lists every approved Bounded Context, backtick-wrapped, with no context silently renamed/merged/removed.
- [ ] Every listed context has a matching folder, and every existing folder is named in `contexts.md` — `validate-ddd.py` check 3 passes for every context this run touched.
- [ ] Nothing was written without prior explicit approval.
