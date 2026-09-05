---
name: "checklist"
description: "Generate a custom, on-demand quality checklist for a module or project-wide artifact."
argument-hint: "What to check and what it targets, e.g. 'testability of the catalog module's requirements'"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root)"
metadata:
  author: "dddkit"
  source: "plan/004_checklist.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). If it doesn't state both a focus (what to check) and a target (what it checks against), ask for whichever is missing before generating anything.

## Goal

Generate a checklist reviewing a specific concern (testability, security, UX, whatever the user names) against the *current, real content* of a target artifact — not generic boilerplate. This is an on-demand tool usable at any point in the pipeline, not tied to one fixed step.

## Outline

1. **Resolve the target and its checklist location**:
   - **Module-scoped** (a Bounded Context + module, e.g. "the catalog module"): find `specs/BoundedContexts/**/domain.md` whose frontmatter `bounded_context`/`module` match. If more than one module matches, ask which one. Output path: `<module dir>/checklists/<name>.md`.
   - **Project-wide** (the requirements doc, `Constitution.md`, or anything not scoped to one module): output path `specs/checklists/<name>.md`.
   - `<name>` is a short kebab-case slug derived from the stated focus (e.g. "security", "requirements-testability").

2. **Read the actual target content** before writing a single item — `domain.md`/`vocabulary.md`/`repomap.md` for a module, `requirements.md`/`Constitution.md` for project-wide. Items must be grounded in what's actually there, not generic.

3. **Generate the checklist** using `.dddkit/templates/checklist-template.md`:
   - Group items into categories relevant to the stated focus.
   - Each item must be specific and falsifiable — "Every FR has a measurable acceptance scenario" beats "Requirements are good."
   - Keep the template's Review Ownership and Marker Semantics notes verbatim — they are load-bearing, not boilerplate to trim.
   - Number items sequentially (`CHK001`, `CHK002`, ...) across the whole file.

4. If a checklist already exists at the resolved path, do not overwrite it silently — ask whether to replace it, add a new dated section, or pick a different name (this may be a second checklist on the same target for a different concern).

## Behavioral Rules

- This skill only ever writes checklist items, never checks any box itself — `[x]` is reserved for a human (or a separate, explicit review pass) to set.
- Never place a project-wide checklist under a module's `checklists/` directory, or vice versa — the two locations exist so `/implement` (once built) can find exactly the checklists relevant to the module it's working on without also picking up unrelated project-wide ones.

## Completion Report

- The checklist's file path and item count.
- A one-line summary of what it reviews.
- Reminder that checking items off is a manual/reviewer step, not something to expect from `/implement` automatically.

## Done When

- [ ] The checklist file exists at the correctly resolved location (module- or project-scoped) with specific, falsifiable items grounded in the real target content.
- [ ] No item is pre-checked.
