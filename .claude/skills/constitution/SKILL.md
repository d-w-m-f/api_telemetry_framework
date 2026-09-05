---
name: "constitution"
description: "Create or amend the project's own engineering constitution at specs/Constitution.md, distinct from the framework's DDD.md."
argument-hint: "Principles or values to add/change in the project constitution"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root)"
metadata:
  author: "dddkit"
  source: "plan/003_constitution.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Scope Guard

This command's own work is limited to updating `specs/Constitution.md`. It never touches `.dddkit/DDD.md` — that document is the framework's own DDD-modeling constitution, governed separately by `DDD.md` section 4 (human-approval gate for new Bounded Contexts), not by this skill.

- Classify every part of the user input as either constitution content or a separate, non-governance intent.
- If the input includes feature implementation, code generation, or other build requests, do **not** execute them — extract them as deferred intents and list them under a `Next Actions` section at the end, suggesting the right command (e.g. `/map-requirements`, `/model-context`) without invoking it.
- If it's unclear whether something is constitution content, ask before changing anything.

## Outline

1. Load `.dddkit/templates/constitution-template.md` as the structural scaffold.

2. Check whether `specs/Constitution.md` exists:
   - **If it exists**: load it as the current source of truth. Preserve everything still applicable while applying the requested change.
   - **If it does not exist**: this skill may create it directly from the user's supplied principles (it does not require a prior `/map-requirements` run to have seeded it) — but if the user hasn't actually supplied any real principles yet, suggest running `/map-requirements` first instead of generating a constitution from nothing.

3. Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]` in the working document. Collect/derive values:
   - If the user's input supplies a value, use it.
   - Otherwise infer from existing repo context (`interview.md`, `requirements.md` if present).
   - `ratified`: the original adoption date — today's date if this is the first creation, otherwise unchanged.
   - `last_amended`: today's date whenever a change is made.
   - `version` (`CONSTITUTION_VERSION` in the template) bumps by strict SemVer:
     - **MAJOR**: a principle is removed or redefined in a backward-incompatible way.
     - **MINOR**: a new principle is added, or existing guidance is materially expanded.
     - **PATCH**: wording, clarification, or typo fixes only.
   - If the bump type is ambiguous, state your reasoning before finalizing it.

4. Draft the updated content:
   - Replace every placeholder with concrete text. Any bracketed token intentionally left for later must be explicitly justified in the Sync Impact Report as a deferred TODO, not silently left.
   - Each principle: a short name line, then a clear, testable statement (MUST/SHOULD, not vague "should try to").
   - Governance section: amendment procedure, the versioning rule above, compliance review expectations.

5. Produce a Sync Impact Report — an HTML comment prepended above the frontmatter closing, matching the format already established for `.dddkit/DDD.md`: version change (old → new), modified/added/removed principles, deferred TODOs.

6. Validate before writing:
   - No unexplained bracket tokens remain.
   - The version in the Sync Impact Report matches the frontmatter and the footer line.
   - Dates are ISO 8601 (`YYYY-MM-DD`).
   - Principles are declarative and testable.

7. Write the result to `specs/Constitution.md` (overwrite in place).

## Completion Report

- New version and the reasoning for the bump level chosen.
- Any deferred TODO placeholders needing manual follow-up.
- A `Next Actions` section for any deferred non-governance intents extracted in the Scope Guard step (omit this section if there were none).

## Done When

- [ ] `specs/Constitution.md` reflects the requested change, correctly versioned, with a valid Sync Impact Report and no unexplained bracket placeholders.
- [ ] `.dddkit/DDD.md` was not modified.
- [ ] Completion reported per above.
