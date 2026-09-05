---
name: "implement-progress"
description: "Report a module's implementation progress: task completion, roadmap phase status, and SdSFC compliance. Read-only."
argument-hint: "The Bounded Context and module to check"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); the target module must have tasks.md"
metadata:
  author: "dddkit"
  source: "plan/010_implement-progress.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Goal

Report where a module's implementation stands. **Strictly read-only** — this skill never writes or modifies any file, including `tasks.md` and `roadmap.md`.

## Outline

1. Invoke `/discover-bounded-context` with `$ARGUMENTS` to resolve the target module. If `tasks.md` doesn't exist for it, say so and suggest `/generate-tasks` — there's nothing to report yet.

2. **If `roadmap.md` exists**: report its phase table as-is (Phase, `tasks.md` Range, Status, Session Notes), plus a raw checkbox tally per phase's task range from `tasks.md` itself, so the two can be cross-checked.

3. **If `roadmap.md` doesn't exist**: this module never needed splitting across sessions. Report a flat tally straight from `tasks.md`'s phases:

   ```text
   | Phase | Total | Done | Remaining | Status |
   |-------|-------|------|-----------|--------|
   | Setup | 2 | 2 | 0 | DONE |
   | [Aggregate] | 5 | 3 | 2 | IN PROGRESS |
   ```

4. **SdSFC status line**: check whether the business-rule file(s) `repomap.md` implies (`business-rules.md` or the file-module equivalent) actually exist at the resolved `code_glob` location. Report this alongside the task tally — "tasks done" and "SdSFC-compliant" are both meaningful and cheap to check together; don't make the user run `/implement` again just to find out the second one is still missing.

## Behavioral Rules

- No file writes, ever, under any circumstance — not to `tasks.md`, not to `roadmap.md`.
- Don't treat a missing `roadmap.md` as an error; it only exists for modules big enough to need one.

## Completion Report

The status table(s) above, plus the SdSFC status line, plus a one-line overall verdict (e.g. "3 of 5 tasks done, business-rule file missing — run `/implement` to continue").

## Done When

- [ ] An accurate progress report was printed with no file modified.
- [ ] The report matches `tasks.md`'s actual current checkbox state (and `roadmap.md`'s, if present) with no false positives/negatives.
