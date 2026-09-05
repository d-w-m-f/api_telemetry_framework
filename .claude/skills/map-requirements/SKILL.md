---
name: "map-requirements"
description: "Interview the user to extract testable functional and non-functional requirements into specs/brainstorm/requirements.md, seeding the project Constitution on first run."
argument-hint: "Optional focus area for this requirements pass"
compatibility: "Requires a dddkit project (.dddkit/ directory at the repo root)"
metadata:
  author: "dddkit"
  source: "plan/002_map-requirements.md"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

## Goal

Extract testable, unambiguous functional and non-functional requirements into `specs/brainstorm/requirements.md`. Unlike `/interview` (free-form capture of "what to build"), this skill's output must be structured and verifiable: "what the system must satisfy." On its first run in a project, also seed `specs/Constitution.md` from whatever durable, project-wide principles surfaced.

## Outline

1. Read `specs/brainstorm/interview.md` if it exists, for context — but this skill can run standalone if it doesn't.

2. Read the existing `specs/brainstorm/requirements.md` if present, so you know the highest `FR-###`/`NFR-###` numbers already used — new requirements continue that numbering, they never renumber or overwrite existing IDs (other artifacts may already reference them).

3. Conduct a requirements-focused Q&A. For unclear aspects:
   - Make an informed guess based on context and industry standards, and document it under **Assumptions** in the output, rather than asking.
   - Only use `[NEEDS CLARIFICATION: specific question]` when the choice significantly impacts scope, has multiple reasonable interpretations with different implications, or has no reasonable default.
   - **Cap: max 3 `[NEEDS CLARIFICATION]` markers per run** (the cap resets each time this skill is invoked — it is not a project-lifetime budget). Prioritize by: scope > security/privacy > user experience > technical detail.

4. Write/append to `specs/brainstorm/requirements.md` using `.dddkit/templates/requirements-template.md` (new file) or the existing file's structure (re-run):
   - Each requirement gets a stable, sequential ID (`FR-001`, `NFR-001`, ...).
   - New file: `version: 1.0.0`. Re-run: bump MINOR for new requirements added, PATCH for wording-only fixes to existing ones.

5. **Constitution seeding** — check whether `specs/Constitution.md` already exists:
   - **If it does not exist**: extract only the principles that are genuinely project-wide and durable (e.g. "all public endpoints require authentication", "p95 latency under 200ms") — not feature-specific requirements, which stay in `requirements.md`. Present the extracted principles to the user for confirmation/edits, then write `specs/Constitution.md` using `.dddkit/templates/constitution-template.md`, version `1.0.0`, with a Sync Impact Report noting this as the initial ratification.
   - **If it already exists**: do not touch it. Note in your completion report that further amendments go through `/constitution`.

## Behavioral Rules

- This skill does **not** produce a requirements-quality checklist as a byproduct — that is `/checklist`'s job, run separately if the user wants one.
- Never bump `specs/Constitution.md`'s version after its initial creation here — only `/constitution` owns amendments from that point on.

## Completion Report

- Requirements file path, version, and count of requirements added this run.
- Any unresolved `[NEEDS CLARIFICATION]` markers (should be zero unless the cap was hit and some were deferred).
- Whether `Constitution.md` was created this run, already existed, or doesn't exist yet (and why, if requirements didn't surface any durable principle).
- Suggested next step: `/map-contexts` once at least one `/interview` and one `/map-requirements` run exist.

## Done When

- [ ] `specs/brainstorm/requirements.md` has testable, ID'd requirements with no more than 3 new unresolved `[NEEDS CLARIFICATION]` markers.
- [ ] `Constitution.md` exists if this was the first run and any durable principle surfaced; otherwise left untouched.
- [ ] Completion reported per above.
