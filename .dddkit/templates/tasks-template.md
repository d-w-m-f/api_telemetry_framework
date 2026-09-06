---
filename: tasks.md
implements_uuid: [SAME_UUID_AS_DOMAIN_MD]
version: 1.0.0
status: draft
---

# Tasks: [MODULE_NAME]

**Input**: `plan.md` (required, with `repomap.md` finalized), `domain.md`.

## Format: `[ID] [P?] [Aggregate] Description`

- **[P]**: can run in parallel (different files, no dependency).
- **[Aggregate]**: which Aggregate from `domain.md`'s "Aggregates & Entities" section this task belongs to — this is the organizing axis (not user stories; dddkit modules are DDD-modeled, not feature-branch-shaped).
- An optional `(FR-###)` tag references `requirements.md` for traceability only — it is not the grouping key.
- Include exact file paths, resolved against `repomap.md`'s `code_glob`.

<!--
  ACTION REQUIRED: replace everything below with real tasks derived from
  plan.md and domain.md's actual Aggregates. Do not leave these as samples.
-->

## Phase 1: Setup

- [ ] T001 Create the module's source location per `repomap.md`'s `code_glob`
- [ ] T002 [P] Initialize dependencies per `plan.md`'s Technical Context

## Phase 2: [Aggregate Name]

**Goal**: [what this aggregate's implementation delivers]

- [ ] T003 [P] [AggregateName] Create [Entity] at `[resolved path]/[file]`
- [ ] T004 [AggregateName] Implement [invariant/behavior] (depends on T003)
- [ ] T005 [AggregateName] Create the business-rule file at `[resolved path]/business-rules.md` (or `[resolved path]/[module-file-name].md` for a `file`-kind module) documenting this aggregate's rules — **must land in the same pass as the first real code task above, not deferred**.

<!-- Repeat the phase above for each additional Aggregate. -->

## Phase N: Polish

- [ ] TXXX Tests for [module], if requested
- [ ] TXXX Run `.dddkit/scripts/validate-ddd.py` and resolve any SdSFC failures for this module

## Dependencies & Execution Order

- Setup blocks everything.
- Aggregate phases can proceed in parallel with each other unless one Aggregate's invariants depend on another's state — call that out explicitly per task, don't assume independence.
- Polish depends on all Aggregate phases being done.

## Cross-Module Dependencies

<!--
  If this module's implementation genuinely depends on another module,
  note it here by module name and what's needed from it - this is a
  plain-text note for the implementer, not a cross-file task-ID system.
  Modules stay independently plannable; a dependency here is an exception
  to call out, not the default.
-->

- [None, or: depends on `<OtherContext>/<other-module>` providing [...]]

## Notes

- `[P]` tasks touch different files with no dependency.
- Verify tests fail before implementing, if tests are part of this module's plan.
- Commit after each task or logical group.
