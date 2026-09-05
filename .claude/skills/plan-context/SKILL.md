---
name: "plan-context"
description: "Produce the technical implementation plan for a module and finalize its repomap.md (code_glob + module_kind)."
argument-hint: "The Bounded Context and module to plan, e.g. 'Catalog/product-listing'"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); the target module must already have domain.md and vocabulary.md"
metadata:
  author: "dddkit"
  source: "plan/007_plan-context.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Prerequisites

Invoke `/discover-bounded-context` with `$ARGUMENTS` to resolve the target module; use its Resolution Result for every path below instead of re-deriving them. Refuse to proceed unless the module's `domain.md` and `vocabulary.md` exist. If `repomap.md` is missing entirely (shouldn't happen if `/model-context` was used), stop and say so — this skill only finalizes an existing skeleton, it doesn't create one.

## Goal

Produce `plan.md` for the module, and finalize its `repomap.md`: write the real `code_glob` and `module_kind` now that the technical structure is actually being decided.

## Outline

1. Read the module's `domain.md`, `vocabulary.md`, and current `repomap.md` skeleton.

2. Read `specs/Constitution.md`, if it exists, for project-wide principles this plan must satisfy.

3. Have a technical conversation with the user covering `.dddkit/templates/plan-template.md`'s Technical Context fields (language/version, primary dependencies, storage, testing, performance goals, constraints) — use `[NEEDS CLARIFICATION: ...]` sparingly, same discipline as `/map-requirements`: only when there's no reasonable default.

4. **Decide `module_kind` and `code_glob`**:
   - `module_kind: file` if the module is a single-responsibility unit with no internal substructure; `module_kind: folder` if it has its own internal layout (handlers, repository, service, etc.).
   - `code_glob` must be specific enough to resolve to exactly one path once the code exists — this is what `.dddkit/scripts/validate-ddd.py`'s SdSFC check (check 2) relies on. It's fine if it resolves to nothing yet (code not written); `build-index.py` treats that as a warning, not an error, at this stage.

5. **Constitution Check gate** (run before drafting and again after):
   - Against `specs/Constitution.md`'s principles, if it exists.
   - Against `.dddkit/DDD.md` section 3 (SdSFC): the plan must leave room for a business-rule file at the `code_glob` location. A plan that doesn't (e.g. a `code_glob` pointing at a third-party/vendored directory nothing should be added to) is a `DDD.md` violation, not just a project-principle one.
   - Any violation of either must be justified in the Complexity Tracking table, or the plan changes — never silently ignore a violation.

6. Write `plan.md` using `.dddkit/templates/plan-template.md`, no leftover bracketed placeholders.

7. **Update the module's `repomap.md` in place**: replace its `code_glob`/`module_kind` placeholders with the real, decided values. Leave `implements_uuid` untouched. Filling in the placeholders for the first time completes `repomap.md`'s v1.0.0 — it is not a version bump (`DDD.md` section 5). If you're instead *changing* an already-finalized `code_glob`/`module_kind` on a re-run, that is a MAJOR bump with a Sync Impact Report.

8. Run `.dddkit/scripts/build-index.py` so `.dddkit/index.json`'s `code_path` reflects the now-resolvable (or still-pending, if code doesn't exist yet) `code_glob`.

## Behavioral Rules

- No fixed "Project Structure" options menu (speckit-plan's single-project/web-app/mobile choices) — `code_glob` is already per-module and flexible enough that a canonical layout menu doesn't add anything here.
- Never touch another module's `plan.md` or `repomap.md`.

## Completion Report

- `plan.md` path, and the finalized `code_glob`/`module_kind`.
- Constitution Check result (pass, or violations with their Complexity Tracking justification).
- Suggested next step: `/generate-tasks` for this module.

## Done When

- [ ] `plan.md` exists with no unresolved `[NEEDS CLARIFICATION]` markers.
- [ ] `repomap.md`'s `code_glob`/`module_kind` are real values, not placeholders.
- [ ] `.dddkit/index.json` reflects the update.
- [ ] Any Constitution/DDD.md violation is either resolved or explicitly justified in Complexity Tracking.
