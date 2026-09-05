---
name: "generate-tasks"
description: "Break a module's plan.md into an ordered, aggregate-organized tasks.md."
argument-hint: "The Bounded Context and module to generate tasks for"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); the target module must already have plan.md"
metadata:
  author: "dddkit"
  source: "plan/008_generate-tasks.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Prerequisites

Invoke `/discover-bounded-context` with `$ARGUMENTS` to resolve the target module. Refuse to proceed unless `plan.md` exists for it; if it doesn't, say so and suggest `/plan-context` first.

## Goal

Produce `tasks.md` for the module: a concrete, dependency-ordered, ideally-parallelizable task breakdown, organized by **Aggregate** (from `domain.md`'s "Aggregates & Entities" section) — not by user story, since a dddkit module is DDD-modeled, not feature-branch-shaped.

## Outline

1. Read `plan.md`, `domain.md`, and the now-finalized `repomap.md` (`code_glob`) for the module.
2. Read `specs/Constitution.md`, if it exists, for any task-level constraints (e.g. mandatory test coverage).
3. Read `specs/brainstorm/requirements.md`, if it exists, to tag tasks with `(FR-###)` where a task clearly implements a specific requirement — this is a traceability tag, not the organizing key.

4. Build `tasks.md` from `.dddkit/templates/tasks-template.md`:
   - **Phase 1 (Setup)**: creating the source location, initializing dependencies per `plan.md`.
   - **One phase per Aggregate** in `domain.md`: tasks for that Aggregate's entities/behavior, each with an exact file path resolved against `repomap.md`'s `code_glob` — never a generic placeholder path like speckit's `src/models/[entity].py`.
   - **A task for the business-rule file** in each Aggregate phase (`business-rules.md` for `module_kind: folder`, or the file-module equivalent), placed in the same phase as that Aggregate's first real code task — not deferred to a separate "documentation" phase, since [009_implement](../../../plan/009_implement.md) must write it alongside the code, not after.
   - **Polish phase**: tests if requested, and a task to run `.dddkit/scripts/validate-ddd.py` and resolve any SdSFC failures before considering the module done.

5. **Cross-module dependencies**: if this module's implementation genuinely needs something from another module, add a plain-text note under "Cross-Module Dependencies" naming that module and what's needed — do not invent a cross-file task-ID reference system. Modules stay independently plannable by default; a dependency here is the exception, called out explicitly.

## Behavioral Rules

- Task IDs (`T001`, ...), `[P]` markers for parallel-safe tasks (different files, no dependency) — same mechanics as speckit-tasks, just regrouped by Aggregate instead of user story.
- Every task's file path must be concrete and resolvable, not a bracketed placeholder.

## Completion Report

- `tasks.md` path and phase count.
- Confirmation the business-rule file task is present for every Aggregate phase.
- Suggested next step: `/implement`.

## Done When

- [ ] `tasks.md` exists, dependency-ordered, phases matching `domain.md`'s Aggregates.
- [ ] Every task has a concrete file path (no `[bracketed placeholder]` left).
- [ ] Every Aggregate phase includes its business-rule-file task.
