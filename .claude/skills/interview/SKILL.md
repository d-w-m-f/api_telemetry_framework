---
name: "interview"
description: "Interview the user about what they want to build, capturing it in their own words as specs/brainstorm/interview.md."
argument-hint: "Describe what you want to build, or run with no arguments to start the conversation"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root)"
metadata:
  author: "dddkit"
  source: "plan/001_interview.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

Treat this as the opening of the conversation if non-empty, not as the whole answer — this skill's job is a real back-and-forth, not a one-shot form fill.

## Goal

Capture what the user wants to build, in their own words, as `specs/brainstorm/interview.md`. This is exploratory and free-form. It is explicitly **not** the place to produce structured functional requirements (that is `/map-requirements`) or to name Bounded Contexts (that is `/map-contexts`, gated by `DDD.md` section 4 — the LLM is forbidden from inferring Bounded Contexts here).

## Outline

1. Check whether `specs/brainstorm/interview.md` exists **and has real content**. Test for content, not mere existence — a zero-byte or placeholder-only file is Round 1, not a re-run.
   - **If it is missing, empty, or still unfilled template text**: this is Round 1. Copy `.dddkit/templates/interview-template.md` as the starting point (overwriting an empty file is fine; overwriting a file with real rounds in it is never fine).
   - **If it has at least one real `## Round N` section**: this is a re-run. Read the existing rounds for context before asking anything, so you don't re-ask what's already answered. You will **append** a new `## Round N — [DATE]` section — never rewrite or delete a prior round.
   - **If `specs/BoundedContexts/contexts.md` already has entries**: acknowledge the existing Bounded Contexts briefly and frame new questions as extending that structure, not starting from a blank slate.

2. Ask open-ended questions covering, at minimum:
   - **Vision**: what the system is and what problem it solves, for whom.
   - **Target users**: who uses it, and whether there are meaningfully different kinds of users.
   - **Key workflows**: the handful of things a user actually does with it.
   - **Constraints & non-goals**: anything explicitly out of scope or a known hard constraint.

   There is no cap on clarifying questions here (unlike `/map-requirements`'s max-3 rule) — this is meant to be a real conversation. Don't rush to a single round of questions and stop; follow up on interesting or ambiguous answers.

3. If the user starts describing formal requirements ("it must support X req/s", "it must validate emails") or names Bounded Contexts unprompted, capture what they said in this file anyway (it's still useful raw material) but note in your response that formal requirements mapping and context mapping happen in `/map-requirements` and `/map-contexts` respectively — don't silently promote their words into those artifacts yourself.

4. Write the round's content into `specs/brainstorm/interview.md`:
   - New file: use the template as-is, frontmatter `version: 1.0.0`.
   - Re-run: append the new `## Round N` section. Bump `version` — MINOR if this round adds real new material, PATCH if it's purely correcting/clarifying something already recorded in a prior round.

5. If `.dddkit/shared_language.md` exists, you may reference it for context, but do not enforce term reuse against it — that behavior is intentionally deferred (see `plan/012_cross-cutting-conventions.md`) and not part of this skill yet.

## Completion Report

Report to the user:
- The file path and its resulting version.
- A one-line summary of what was captured this round.
- Suggested next step: `/map-requirements` (if not yet run) to turn this into testable requirements, or `/interview` again later to add more ground.

## Done When

- [ ] `specs/brainstorm/interview.md` exists (or was appended to) with real narrative content — no leftover template placeholders like `[DATE]` or bracketed prompts.
- [ ] No Bounded Context names, `domain.md`, or `vocabulary.md` files were created as a side effect.
- [ ] Completion reported with file path, version, and next-step suggestion.
