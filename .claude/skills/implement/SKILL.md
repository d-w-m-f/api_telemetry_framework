---
name: "implement"
description: "Execute a module's tasks.md, writing real code and its business-rules.md alongside it."
argument-hint: "The Bounded Context and module to implement, optionally a specific phase"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); the target module must already have tasks.md and a finalized repomap.md"
metadata:
  author: "dddkit"
  source: "plan/009_implement.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Prerequisites

Invoke `/discover-bounded-context` with `$ARGUMENTS` to resolve the target module. Refuse to proceed unless `tasks.md` exists and `repomap.md`'s `code_glob`/`module_kind` are real (not placeholders, per the Resolution Result) — if either is missing, say so and point at `/generate-tasks` or `/plan-context`.

## Outline

1. **Checklist gate**: if the module directory has a `checklists/` folder, scan every `*.md` in it. Count total/checked/unchecked items per file (`- [ ]` vs `- [x]`/`- [X]`). If anything is unchecked, show the status table and **stop, asking whether to proceed anyway** — never modify checklist markers yourself. Proceed automatically only if everything is already checked, or the user explicitly says to proceed.

2. Load context: `tasks.md`, `plan.md`, `domain.md`, `repomap.md`, and `roadmap.md` if it exists.

3. **Roadmap handling**:
   - If `roadmap.md` exists, work only within its next "Not Started" (or explicitly requested) phase this run, unless the user asks for the whole module in one pass.
   - If it doesn't exist yet, and `tasks.md` is large enough that finishing it in one session is unrealistic, create `roadmap.md` from `.dddkit/templates/roadmap-template.md`, mirroring `tasks.md`'s own phase breakdown, before starting work. A small module doesn't need one — don't create it just to have it.

4. **Execute tasks phase by phase**, respecting `tasks.md`'s dependency order and `[P]` parallel markers:
   - Write real code at the location `repomap.md`'s `code_glob` resolves to (create the file/directory if it doesn't exist yet — this is normal on a module's first `/implement` run).
   - **When a phase's business-rule-file task comes up, write it in that same pass, alongside the code it documents** — never defer it to a later cleanup task. Fill it in for real (data flow, validations, edge cases per `.dddkit/templates/business-rules-template.md`'s sections), grounded in the code just written — not generic boilerplate.
   - Mark each completed task `[X]` in `tasks.md` as you go.
   - If `roadmap.md` exists, update the current phase's Status/Session Notes columns as it completes.

5. **After finishing this run's scope** (a roadmap phase, or the whole module), run:
   ```
   python3 .dddkit/scripts/validate-ddd.py
   ```
   Read the output for this module specifically. **A failure blocks declaring the module (or this phase) done** — matching the SdSFC-is-non-negotiable stance in `DDD.md`. Report the failure and what's needed to fix it; do not mark remaining tasks `[X]` to paper over it.

## Behavioral Rules

- Checklists are read-only from this skill's side — report and gate on them, never check/uncheck an item.
- Halt on a non-parallel task failure; for `[P]` tasks, continue with the ones that succeeded and report the ones that didn't.

## Completion Report

- Tasks completed this run, and which remain.
- The business-rule file(s) written or updated.
- `validate-ddd.py` result for this module — pass, or what's failing and why the run isn't "done" yet.
- If `roadmap.md` exists, its updated phase status; suggest `/implement-progress` to check overall standing, or `/implement` again for the next phase.

## Done When

- [ ] Every task attempted this run is either `[X]` or reported as failed with a reason.
- [ ] The relevant business-rule file(s) exist and are filled in with real content, not template placeholders.
- [ ] `.dddkit/scripts/validate-ddd.py` passes for this module before it is reported as fully done (a partially-done roadmap phase is reported as such, not as "done").
