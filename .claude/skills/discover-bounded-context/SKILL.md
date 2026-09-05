---
name: "discover-bounded-context"
description: "Resolve a module reference (uuid, Context/module pair, or bare module name) to its spec files, code location, and business-rule-file path."
argument-hint: "A module uuid, 'BoundedContext/module', or just 'module' if unambiguous"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root)"
metadata:
  author: "dddkit"
  source: "plan/011_discover-bounded-context.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Goal

Given a module reference, resolve it to the concrete file set another skill (or a human) needs: the module's spec folder, `domain.md`, `vocabulary.md`, `repomap.md`'s `code_glob`/`module_kind`/resolved `code_path`, and the expected business-rule-file path — whether or not that last one exists yet. This skill only **locates**; it never modifies a module or acts on it. Other skills in the SDK (`/plan-context`, `/generate-tasks`, `/implement`, `/implement-progress`) invoke this skill to resolve their target module instead of independently re-deriving paths — if you are one of those skills, invoke this one and use its Resolution Result rather than repeating this logic inline.

## Outline

1. **Classify the input** (`$ARGUMENTS`):
   - Looks like a UUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`): resolve by UUID.
   - Contains a `/` (e.g. `Catalog/product-listing`): treat as `BoundedContext/module`.
   - Otherwise: treat as a bare module name.

2. **Resolve by UUID**: look it up directly in `.dddkit/index.json`.
   - If absent, run `python3 .dddkit/scripts/build-index.py` once and retry.
   - Still absent: report "no module with uuid `<uuid>`" and stop — don't guess.

3. **Resolve by name** (`BoundedContext/module` or bare `module`): scan `specs/BoundedContexts/**/domain.md` frontmatter for a `module` match (and `bounded_context` match too, if given).
   - **Exactly one match**: proceed with it.
   - **Bare module name matches more than one Bounded Context**: stop and list every `BoundedContext/module` match — ask the caller (human or invoking skill) to specify which one. Never guess which one was meant.
   - **No match**: report "no module named `<name>`" and stop.

4. **Cross-check freshness**: compare the resolved module's `domain.md` uuid/path against `.dddkit/index.json`. If the index doesn't have it, or its recorded `spec_path` doesn't match, run `python3 .dddkit/scripts/build-index.py` once before reporting — a stale index should never silently produce a wrong path.

5. **Read `repomap.md`** for `code_glob`/`module_kind`. If they're still template placeholders (module hasn't been through `/plan-context` yet), report that explicitly rather than attempting to resolve a placeholder as if it were a real glob.

6. **Derive the business-rule-file path**: `<resolved code_path>/business-rules.md` for `module_kind: folder`, or `<resolved code_path minus extension>.md` for `module_kind: file`. Report it either way, noting whether it currently exists.

7. **Report the Resolution Result** in this shape, so a calling skill can read it straight from this skill's response:

   ```text
   Resolution Result for <BoundedContext>/<module> (uuid: <uuid>)
   - Spec folder: specs/BoundedContexts/<Context>/<module>/
   - domain.md:   <path> (read it for aggregates/invariants)
   - vocabulary.md: <path>
   - repomap.md:  module_kind=<folder|file|UNRESOLVED>, code_glob=<glob|UNRESOLVED>
   - code_path:   <resolved path, or "unresolved - run /plan-context first">
   - business-rule file: <path> (exists|missing)
   ```

## Behavioral Rules

- Read-only: this skill never writes to any file (it may trigger `build-index.py`, which only rewrites `.dddkit/index.json`, never spec or code files).
- Never silently pick between multiple name matches — ask instead.

## Completion Report

The Resolution Result block above, or a clear "not found" / "ambiguous, specify which" message.

## Done When

- [ ] Exactly one module was resolved and its full file set reported, or the caller was told precisely why resolution couldn't be completed (not found / ambiguous).
