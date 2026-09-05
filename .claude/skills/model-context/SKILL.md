---
name: "model-context"
description: "Model the modules inside a Bounded Context: propose module boundaries, scaffold them, and fill in domain.md/vocabulary.md through a modeling conversation."
argument-hint: "The Bounded Context name, and optionally a specific module to model"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root); the target Bounded Context must already exist under specs/BoundedContexts/"
metadata:
  author: "dddkit"
  source: "plan/006_model-context.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Prerequisites

The target Bounded Context must already exist as a folder under `specs/BoundedContexts/` (created by `/map-contexts`). If it doesn't, say so and suggest `/map-contexts` first.

## Goal

For one Bounded Context, model its modules through a real conversation about aggregates, entities, invariants, and ubiquitous language — then scaffold each approved module (`domain.md`, `vocabulary.md`, `repomap.md` skeleton) using the existing scaffolding script, and fill `domain.md`/`vocabulary.md` in completely. `repomap.md` is left as a skeleton — its `code_glob`/`module_kind` are `/plan-context`'s job, not this skill's.

## Outline

1. **Determine scope**: if `$ARGUMENTS` names a specific module, work on just that one. If it names only the Bounded Context (or the context has unmodeled aggregates the user hasn't named yet), offer batch mode: walk through every module needed for that context in this session, one at a time, using the same propose-then-approve-then-model loop for each.

2. **Propose module boundaries** before scaffolding anything, mirroring `/map-contexts`' propose-then-approve pattern:
   - From the conversation and whatever's in `interview.md`/`requirements.md` relevant to this context, propose a candidate module list: one module per aggregate boundary, each a kebab-case name with a one-line description of its aggregate root.
   - If a proposed module clearly spans multiple aggregates with no single clear root, say so and suggest splitting it — don't scaffold an ill-defined module just because the user suggested one name for it.
   - Wait for the user to confirm (or adjust) the module list before creating anything.

3. **For each approved module that doesn't already exist**, scaffold it by running:
   ```
   python3 .dddkit/scripts/scaffold-context.py --context <Context> --module <module>
   ```
   Do not hand-roll folder creation or UUID assignment — this script is the single source of truth for that mechanic. If it exits non-zero (e.g. the module already exists), read its error and resolve before continuing.

4. **Model each module through conversation**, then fill in (replacing every template placeholder — no `[ACTION REQUIRED]` comment or bracketed prompt should remain):
   - `domain.md`: Overview, Aggregates & Entities, Invariants, Relationships to Other Bounded Contexts.
   - `vocabulary.md`: the module's ubiquitous language terms, and which shared-language terms it draws on.
   - Do **not** touch `repomap.md` beyond what `scaffold-context.py` already wrote (uuid filled in, `code_glob`/`module_kind` left as placeholders).

5. **After all modules in this run are filled in**, run:
   ```
   python3 .dddkit/scripts/build-index.py
   ```
   A "matched nothing" warning for these modules' unresolved `code_glob` is expected and fine at this stage — `/plan-context` resolves that later.

## Behavioral Rules

- One module per aggregate boundary is the default heuristic — this is DDD's own aggregate-design guidance, not a dddkit-specific invention.
- Never create a Bounded Context here — that's `/map-contexts`' job and its own approval gate. If the user tries to introduce a new context mid-conversation, stop and redirect to `/map-contexts`.
- Ground-language consistency checking against `.dddkit/shared_language.md` is deferred (not yet a defined behavior — see `plan/012_cross-cutting-conventions.md`); reference it for context only, don't enforce term reuse.

## Completion Report

- Which module(s) were scaffolded/modeled this run, and their UUIDs.
- Confirmation that `.dddkit/index.json` was refreshed.
- Suggested next step: `/plan-context` for each modeled module.

## Done When

- [ ] Every module discussed this run has `domain.md` and `vocabulary.md` fully written, with a real `uuid` in `repomap.md`'s skeleton.
- [ ] `repomap.md`'s `code_glob`/`module_kind` remain unresolved placeholders (not this skill's job to fill).
- [ ] `.dddkit/index.json` includes the new module(s).
