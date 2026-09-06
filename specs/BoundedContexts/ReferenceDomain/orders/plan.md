---
filename: plan.md
implements_uuid: 55aa03b8-dc2a-4bfb-9dba-16b3d4ce2ee3
version: 1.0.0
status: draft
---

# Implementation Plan: orders

**Module**: `specs/BoundedContexts/ReferenceDomain/orders/` | **Date**: 2026-09-05

**Input**: this module's `domain.md` and `vocabulary.md`.

## Summary

`orders` owns the Order aggregate and the fixture's single contended
transaction. Technically it is two mapped tables (`orders`, `order_lines`)
behind a FastAPI write endpoint and a read endpoint, where placement is
implemented as one database transaction containing a **conditional UPDATE per
SKU** followed by the Order insert.

The conditional UPDATE is the heart of the plan and the reason Constitution
principle IV is satisfiable without pessimistic locking:

```sql
UPDATE products
   SET stock_quantity = stock_quantity - :qty
 WHERE sku = :sku AND sellable = true AND stock_quantity >= :qty
RETURNING unit_price_cents
```

A row is returned only if the stock was actually taken. Zero rows affected means
the SKU was absent, not sellable, or had insufficient stock — decided by the
database atomically, never by a prior `SELECT` in Python. The `RETURNING` clause
also supplies the price snapshot required by INV-004 in the same round trip, so
there is no window in which the price could change between reading it and
recording it.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (sync ORM, `psycopg` 3 driver), Pydantic v2, Uvicorn
**Storage**: PostgreSQL 16, default `READ COMMITTED` isolation — sufficient here precisely because the guard lives in the `WHERE` clause rather than in a prior read
**Testing**: pytest + httpx, including a threaded concurrency test that fires N simultaneous placements at a SKU with stock 1 and asserts exactly one acceptance (NFR-006)
**Performance Goals**: none imposed — this is the measurement target (Constitution II)
**Constraints**: no cache, broker, scheduler, or replica (NFR-005); stateless process (NFR-001); no authentication (NFR-007); all-or-nothing placement (INV-008)

## Constitution Check

*GATE: must pass before `repomap.md` is finalized below. Re-check after drafting this plan.*

Checked against `specs/Constitution.md` v1.0.0 and `.dddkit/DDD.md` section 3.

| Gate | Status | Notes |
|------|--------|-------|
| I. The Fixture Is Frozen | **PASS** | Implements the ratified invariants exactly; adds no lifecycle transition beyond the single status the domain declares. |
| II. Infrastructure Is a Variable | **PASS** | No queue, no outbox, no lock service. Placement is a plain database transaction. |
| III. Identical Starting State | **PASS** | Reset removes all Orders; Orders are never seeded, so a reset state contains none by construction. |
| IV. Concurrency Enforced by the Database | **PASS** | The conditional UPDATE above is the enforcement point. There is deliberately **no** `SELECT ... then decide` anywhere in the placement path. Verified by the NFR-006 concurrency test, not by inspection. |
| V. Machine-Readable Failure Modes | **PASS** | Every rejection in INV-001/002/003 and the stock/SKU failures carries a distinct `error_code` and a `4xx` status; `5xx` is reserved for genuine faults. |
| `DDD.md` §3 (SdSFC) | **PASS** | `code_glob` resolves to a project-owned directory that will hold `business-rules.md`. |

Re-checked after drafting: no gate changed status.

## Repomap Finalization

- **`module_kind`**: `folder` — placement logic, two mapped tables, request/response schemas, and the router are separate concerns; collapsing them into one file would obscure the one part that matters (the transaction).
- **`code_glob`**: `services/reference-api/app/orders/`
- **Internal layout notes**: `models.py` (SQLAlchemy `Order` and `OrderLine`), `schemas.py` (Pydantic placement request and order response), `placement.py` (the single transactional function implementing the conditional UPDATE and the all-or-nothing guarantee — deliberately isolated so the contended path is one readable unit), `router.py` (FastAPI routes), and `business-rules.md` (the SdSFC anchor carrying `implements_uuid`).

## Complexity Tracking

> Fill ONLY if the Constitution Check above has violations that must be justified.

No Constitution violation. Two deliberate deviations are recorded so a later
reader does not mistake either for an oversight:

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| The placement transaction writes to the `products` table, owned by the `catalog` aggregate. | INV-006 requires the Order and the stock decrement to be indivisible. | Eventual consistency permits a window of oversell and compensating correction; INV-003 forbids that window outright. Full reasoning in `catalog/domain.md`. |
| Order lines are sorted by SKU before their conditional UPDATEs are issued. | Two concurrent multi-line orders touching the same SKUs in opposite orders can deadlock in Postgres. A consistent global ordering makes the deadlock unreachable rather than merely retried. | Catching the deadlock and retrying would work, but adds a retry path whose timing characteristics would show up in the benchmark as though it were domain behavior — contaminating exactly what is being measured (Constitution II). |
