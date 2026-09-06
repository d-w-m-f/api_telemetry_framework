---
filename: plan.md
implements_uuid: e188f5df-2e2f-48c1-b127-c6887a5b5338
version: 1.0.0
status: draft
---

# Implementation Plan: catalog

**Module**: `specs/BoundedContexts/ReferenceDomain/catalog/` | **Date**: 2026-09-05

**Input**: this module's `domain.md` and `vocabulary.md`.

## Summary

`catalog` owns the Product aggregate — the sellable item, its price, and its
stock level — and serves the fixture's read path. Technically it is a small
SQLAlchemy-mapped table behind two FastAPI read endpoints plus a fixture-reset
operation, with the stock column carrying a database-level non-negativity
constraint so that the aggregate's central invariant is enforced by Postgres
rather than by application code.

The module deliberately owns the *table and its constraints* but not the
transaction that decrements stock: that transaction belongs to `orders`, which
enters this module's data through a single guarded statement. Keeping the
constraint here and the transaction there is what lets INV-003 hold without
`catalog` needing to know anything about ordering.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (sync ORM, `psycopg` 3 driver), Pydantic v2, Uvicorn
**Storage**: PostgreSQL 16, single database, schema created from the mapped models at startup (no migration tool — see Constitution Check)
**Testing**: pytest + httpx against a live Postgres from the same compose stack
**Performance Goals**: none imposed. This service is the *measurement target*; asserting its own latency budget would prejudge the number the benchmark exists to produce (Constitution II).
**Constraints**: no cache, broker, scheduler, or replica (NFR-005); stateless process (NFR-001); no authentication (NFR-007); money as integer minor units only.

## Constitution Check

*GATE: must pass before `repomap.md` is finalized below. Re-check after drafting this plan.*

Checked against `specs/Constitution.md` v1.0.0 and `.dddkit/DDD.md` section 3.

| Gate | Status | Notes |
|------|--------|-------|
| I. The Fixture Is Frozen | **PASS** | This plan implements the ratified rules; it does not add, relax, or reinterpret any. |
| II. Infrastructure Is a Variable | **PASS** | Dependencies are FastAPI and PostgreSQL only — both irreducibly required by the stated domain. No cache or broker is introduced for convenience. |
| III. Identical Starting State | **PASS** | Schema creation is `create_all` (idempotent by construction); the reset operation truncates and re-seeds from a literal, ordered fixture list, so two resets are byte-identical. |
| IV. Concurrency Enforced by the Database | **PASS** | Stock is guarded by a `CHECK (stock_quantity >= 0)` constraint at the column level. This module contributes the constraint; `orders` contributes the atomic statement that respects it. No read-then-decide path exists in this module, which performs no writes to stock at all. |
| V. Machine-Readable Failure Modes | **PASS** | Both read endpoints answer `404` with a stable `error_code` body for unknown or non-sellable SKUs; page-size violations answer `422` with their own code. |
| `DDD.md` §3 (SdSFC) | **PASS** | `code_glob` resolves to a directory owned entirely by this project, into which `business-rules.md` is written by `/ddd-implement`. Nothing vendored or third-party is involved. |

Re-checked after drafting: no gate changed status.

## Repomap Finalization

- **`module_kind`**: `folder` — the module has real internal structure (SQLAlchemy model, Pydantic schemas, a repository-ish query layer, and a FastAPI router), not a single-responsibility unit. A `file` module would force those four concerns into one file purely to satisfy the classification.
- **`code_glob`**: `services/reference-api/app/catalog/`
- **Internal layout notes**: `models.py` (SQLAlchemy `Product`, including the stock CHECK constraint), `schemas.py` (Pydantic request/response shapes), `queries.py` (the read functions, kept separate so the read path is measurable in isolation), `router.py` (FastAPI routes), `seed.py` (the deterministic fixture catalog), and `business-rules.md` (the SdSFC anchor carrying `implements_uuid`).

## Complexity Tracking

> Fill ONLY if the Constitution Check above has violations that must be justified.

No Constitution violation. One deviation from *classical DDD* — not from any
gate above — is recorded here rather than left implicit, because a later reader
will otherwise see it as an accident:

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| The Product aggregate's stock is mutated inside a transaction owned by the `orders` module, crossing an aggregate boundary. | INV-003 (stock never negative) must hold under concurrency. A transaction spanning both aggregates is the only way to take stock and record the Order indivisibly. | Eventual consistency between Order and Product — the textbook answer — permits a window of oversell followed by compensation. Oversell is exactly the defect this fixture exists to detect, so the fixture cannot be built on a model that tolerates it. |
