---
filename: roadmap.md
implements_uuid: [SAME_UUID_AS_DOMAIN_MD]
version: 1.0.0
status: draft
---

# Roadmap: [MODULE_NAME]

Created because this module's `tasks.md` is too large for one `/implement` session. Splits it into phases that can each be completed and checkpointed independently. If `tasks.md` fits in one session, this file doesn't need to exist at all — `/implement-progress` falls back to reading `tasks.md` directly when there's no roadmap.

## Phases

<!-- ACTION REQUIRED: mirror tasks.md's own phase breakdown. -->

| Phase | tasks.md Range | Status | Session Notes |
|-------|-----------------|--------|----------------|
| 1. Setup | T001-T002 | Not Started | |
| 2. [Aggregate Name] | T003-T005 | Not Started | |

## Notes

- `/implement` updates the Status/Session Notes columns as it completes each phase — never the checkbox state in `tasks.md` beyond marking tasks `[X]` as it goes.
- `/implement-progress` reads this file when present, and reports a flat `tasks.md` tally when it isn't.
