---
filename: interview.md
version: 1.0.1
status: draft
---

# Interview

<!--
  This file grows by APPENDING a new "## Round N" section each time
  /interview runs again — never rewrite or delete a prior round's answers.
  Bump the version (MINOR) whenever a round adds real new material; PATCH
  only for a pure wording correction to something already recorded.
-->

## Round 1 — 2026-09-05

> **Provenance note.** The repository owner opened this round with: *"develop a
> backend app with fastAPI + postgreSQL, with dockerized infra ... You have
> liberty to define business rules, scope of solution and etc, but dont
> overcomplicate the backend infrastructure."* The vision and constraints below
> are the owner's. The domain detail was delegated to the agent under that
> explicit grant of liberty, and is recorded here as the owner's standing
> position until they say otherwise. This round was therefore not a live
> back-and-forth; where an answer was chosen rather than given, it is marked
> **(delegated)**.

### Vision

A backend service that implements the e-commerce fixture this repository already
describes: a catalog you can read, and orders you can place against it. Its
purpose is not to be a product. It is a **measurement target** — a realistic but
deliberately frozen workload that different API architectures can be
re-implemented against, so that throughput and telemetry comparisons between
those architectures are fair.

That framing drives every other decision here. The domain is a fixture, so it is
valuable precisely to the extent that it stays still. Interesting business
complexity is a liability: it would make each re-implementation a different
amount of work, which is exactly the confound the benchmark exists to avoid.

The existing Bounded Contexts in `specs/BoundedContexts/contexts.md` already
anticipate this work — this round extends that structure rather than starting
from a blank slate. No new Bounded Context is proposed here (that decision
belongs to `/map-contexts` and its approval gate).

### Target Users

Two kinds, and neither is an end consumer:

1. **The load generator** — the primary caller. Not a person. It hammers a small
   number of endpoints at high concurrency and cares about latency, error rate,
   and correctness under contention. It is the reason the API exists.
2. **The benchmark author** — a human re-implementing this same domain in a
   different architecture (hexagonal, CQRS, MVC). They read the specs to know
   what "the same domain" means, and need the rules to be unambiguous enough
   that two implementations can be compared without arguing about semantics.

There is no admin UI, no merchant persona, and no authenticated shopper.
(delegated)

### Key Workflows

- **Browse the catalog.** List products with pagination; fetch one product by
  its SKU. Read-heavy, and the workload the benchmark will lean on hardest.
- **Place an order.** Submit a customer reference plus a set of lines (SKU +
  quantity). The service validates the products exist and are sellable, checks
  there is enough stock, decrements it, snapshots the prices, and persists the
  order. This is the write path and the only place real contention happens —
  two concurrent orders for the last unit of a SKU must not both succeed.
- **Read an order back.** Fetch a placed order by its id, to confirm what was
  actually recorded. (delegated)
- **Seed / reset the fixture.** Load a known catalog and return the database to
  a known state, so benchmark runs start from identical conditions and are
  repeatable. Without this the comparisons do not mean anything. (delegated)

### Constraints & Non-Goals

**Hard constraints (owner-stated):**
- FastAPI and PostgreSQL.
- Dockerized infrastructure.
- **Do not overcomplicate the infrastructure.** Explicitly the owner's words.
  Where a simpler option exists, take it.

**Constraints that follow from the fixture framing:** (delegated)
- The domain is **frozen by decree** once agreed. Rules are followed, not
  discovered or refactored — a change invalidates the comparative history
  already collected against it.
- Stock correctness under concurrency is the one place where being "simple" is
  not allowed to mean "sloppy", because oversell is exactly the kind of bug a
  high-concurrency benchmark manufactures. This is a correctness requirement,
  not a performance one.

**Non-goals:** (delegated)
- Authentication, authorization, users, sessions, carts, payments, shipping,
  tax, discounts, inventory reservation/expiry, returns, search/ranking.
- Migrations tooling. The schema is created from the model at startup; a fixture
  database has no history worth migrating.
- Caching, message queues, and read replicas. Those are *architectural variables
  the benchmark exists to test*, so baking them into the fixture would prejudge
  the thing being measured.
- Horizontal scaling and production hardening of this particular service.

### Open Threads

Recorded for a future round rather than answered now:
- Whether `LabExperiments` (the measuring side) eventually calls this service
  directly, or only ever drives it through a generic load generator.
- Whether the fixture should later expose deliberate slow paths (N+1 queries, a
  synthetic delay) so architectures can be compared on pathological workloads
  as well as healthy ones.

## Notes

- This file is free-form capture, not structured requirements — do not restructure it into FR-###/NFR-### form here. That happens in `/map-requirements`, producing `specs/Brainstorm/requirements.md`.
- Do not name or propose Bounded Contexts here. That happens in `/map-contexts`, gated by `DDD.md` section 4 (explicit human approval required).
