---
filename: interview.md
version: 1.0.0
status: draft
---

# Interview

<!--
  This file grows by APPENDING a new "## Round N" section each time
  /interview runs again — never rewrite or delete a prior round's answers.
  Bump the version (MINOR) whenever a round adds real new material; PATCH
  only for a pure wording correction to something already recorded.
-->

## Round 1 — [DATE]

### Vision

[What is this product/system, in the user's own words? What problem does it solve, for whom?]

### Target Users

[Who uses this? Are there multiple distinct kinds of users?]

### Key Workflows

[The handful of things a user actually does with this system, described narratively.]

### Constraints & Non-Goals

[Anything explicitly out of scope, or a hard constraint the user already knows about (must integrate with X, must not use Y).]

## Notes

- This file is free-form capture, not structured requirements — do not restructure it into FR-###/NFR-### form here. That happens in `/map-requirements`, producing `specs/brainstorm/requirements.md`.
- Do not name or propose Bounded Contexts here. That happens in `/map-contexts`, gated by `DDD.md` section 4 (explicit human approval required).
