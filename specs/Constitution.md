<!--
  Sync Impact Report
  Version: (none) -> 1.0.0
  Modified principles: none (initial ratification)
  Added sections: Core Principles (I-V), Governance
  Removed sections: none
  Deferred TODOs: none — every placeholder token in
    .dddkit/templates/constitution-template.md was resolved at creation.
  Origin: seeded by /ddd-map-requirements from specs/Brainstorm/interview.md and
    specs/Brainstorm/requirements.md v1.0.0, per that skill's first-run
    Constitution-seeding step. All later amendments go through /ddd-constitution.
-->

---
filename: Constitution.md
version: 1.0.0
status: draft
ratified: 2026-09-05
last_amended: 2026-09-05
---

# api_throughput_n_telemetry Constitution

This is the project's own engineering constitution — distinct from `.dddkit/DDD.md`, which governs how DDD modeling itself is done and is not edited through this document. Amended exclusively through `/ddd-constitution` after the first draft.

## Core Principles

### I. The Fixture Is Frozen

Any domain declared a reference fixture MUST have its business rules fixed by decree and MUST NOT be refactored, extended, or "improved" once ratified. Changing a fixture's rules retroactively invalidates every comparative measurement already taken against it.

A change to a frozen domain is therefore a governance event, not an engineering one: it MUST be accompanied by an explicit statement of which prior measurements it invalidates. A fixture rule that turns out to be awkward is not grounds for changing it.

### II. Infrastructure Is a Variable, Not a Given

Caches, message brokers, read replicas, background workers, and alternative persistence engines are the things this project exists to measure. They MUST NOT be introduced into a measurement target as incidental implementation convenience.

Every infrastructure dependency added to a measured service MUST be justified as either (a) irreducibly required by the domain, or (b) the deliberate independent variable of a specific experiment. "It made the code nicer" is not a justification. When two designs satisfy the domain equally, the one with fewer moving parts MUST win.

### III. Measurements Start From an Identical State

Any service used as a measurement target MUST provide a documented, repeatable way to return to a known starting state, and that reset MUST be deterministic — two resets produce identical data.

Schema creation and seeding MUST be idempotent. A benchmark whose starting conditions drift between runs produces numbers that cannot be compared, which is indistinguishable from producing no numbers at all.

### IV. Concurrency Correctness Is Enforced by the Database

Invariants that can be violated by interleaved requests — stock levels, balances, uniqueness — MUST be enforced by the storage engine through atomic operations, constraints, or locking. They MUST NOT be enforced by a read-then-decide sequence in application code, which is a race condition with a comfortable syntax.

Any such invariant MUST have an automated test that exercises it concurrently. Sequential tests do not demonstrate concurrency correctness and MUST NOT be presented as if they do.

### V. Failure Modes Are Machine-Readable and Honest

Every rejection a service can produce MUST carry a stable, machine-readable code distinct to its cause, and MUST use a `4xx` status when the caller's request was understood and refused on domain grounds.

`5xx` is reserved for genuine faults. A load generator distinguishes "the system correctly refused 30% of my requests" from "the system fell over" solely by this signal; blurring the two makes every error-rate measurement meaningless.

## Governance

**Authority.** This constitution governs engineering practice for this repository. It does not govern DDD modeling mechanics — directory structure, naming, the SdSFC pattern, and the human-approval gate on new Bounded Contexts live in `.dddkit/DDD.md` and are amended there, not here. Where the two documents both speak, `.dddkit/DDD.md` prevails on modeling questions and this document prevails on engineering questions.

**Amendment procedure.** Amendments are made exclusively through `/ddd-constitution`. Every amendment MUST carry a Sync Impact Report prepended above the frontmatter, recording the version transition and what changed. Prior Sync Impact Reports are never deleted; a new one is prepended above them.

**Versioning policy.**
- **MAJOR** — a principle is removed, or redefined in a way that invalidates work done under the previous reading.
- **MINOR** — a new principle is added, or existing guidance is materially expanded.
- **PATCH** — wording, clarification, or typo fixes that leave the meaning intact.

**Compliance review.** `/ddd-go-planning` MUST check its plan against these principles before and after drafting, and any violation MUST be either resolved or recorded with justification in that plan's Complexity Tracking table. An unjustified violation blocks the plan, not the principle.

**Version**: 1.0.0 | **Ratified**: 2026-09-05 | **Last Amended**: 2026-09-05
