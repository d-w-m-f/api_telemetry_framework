---
filename: tasks.md
implements_uuid: 55aa03b8-dc2a-4bfb-9dba-16b3d4ce2ee3
version: 1.0.0
status: draft
---

# Tasks: orders

**Input**: `plan.md` (required, with `repomap.md` finalized), `domain.md`.

## Format: `[ID] [P?] [Aggregate] Description`

- **[P]**: can run in parallel (different files, no dependency).
- **[Aggregate]**: which Aggregate from `domain.md`'s "Aggregates & Entities" section this task belongs to — this is the organizing axis (not user stories; dddkit modules are DDD-modeled, not feature-branch-shaped).
- An optional `(FR-###)` tag references `requirements.md` for traceability only — it is not the grouping key.
- Include exact file paths, resolved against `repomap.md`'s `code_glob`.

## Phase 1: Setup

- [X] T001 Create the module source location `services/reference-api/app/orders/` per `repomap.md`'s `code_glob`

> The shared composition root (`app/db.py`, `app/errors.py`, `app/main.py`,
> `Dockerfile`, `docker-compose.yml`) is created by `ReferenceDomain/catalog`'s
> Phase 1 and is a prerequisite here — see Cross-Module Dependencies. It is not
> duplicated as tasks in this file.

## Phase 2: Order

**Goal**: an Order can be placed atomically, cannot oversell under any concurrent interleaving, and is immutable once recorded.

- [X] T002 [Order] Create the `Order` and `OrderLine` models at `services/reference-api/app/orders/models.py` — server-generated UUID id, customer reference, status, `total_cents`, `placed_at`; lines carrying SKU, quantity, `unit_price_cents`, with a unique constraint on `(order_id, sku)` enforcing INV-002 in the database and `CHECK (quantity >= 1)` enforcing INV-003
- [X] T003 [P] [Order] Create request/response schemas at `services/reference-api/app/orders/schemas.py` — `PlaceOrderRequest` (≥1 line, quantity ≥1, no duplicate SKU: INV-001, INV-002, INV-003), `OrderOut`, `OrderLineOut`
- [X] T004 [Order] Implement placement at `services/reference-api/app/orders/placement.py` — one transaction: lines sorted by SKU (deadlock avoidance per `plan.md`), a conditional `UPDATE ... WHERE sku=:sku AND sellable AND stock_quantity >= :qty RETURNING unit_price_cents` per line, rejection on zero rows affected, then the Order insert. **No `SELECT`-then-decide anywhere in this path** (INV-004, INV-006, INV-008; Constitution IV) (depends on T002)
- [X] T005 [Order] Implement routes at `services/reference-api/app/orders/router.py` — `POST /orders` returning 201 with the new id, `GET /orders/{id}` returning the recorded lines/prices/total or 404, every rejection carrying a distinct machine-readable code with a `4xx` status (FR-005…FR-018, FR-021, FR-022) (depends on T003, T004)
- [X] T006 [Order] Create the business-rule file at `services/reference-api/app/orders/business-rules.md` documenting this aggregate's rules, the placement data flow, validations, and edge cases — **must land in the same pass as T002–T005 above, not deferred**

## Phase 3: Polish

- [X] T007 [P] Tests at `services/reference-api/tests/test_orders.py` — placement happy path, empty lines, quantity < 1, duplicate SKU, unknown SKU, non-sellable SKU, insufficient stock, price snapshot independence from later catalog changes, all-or-nothing on partial failure
- [X] T008 Concurrency test at `services/reference-api/tests/test_concurrency.py` — N simultaneous placements against a SKU with stock 1 must yield exactly one acceptance and N-1 rejections, with final stock 0 (NFR-006, INV-006). **Required: a sequential test does not demonstrate this and must not be presented as if it does** (Constitution IV)
- [X] T009 Run `.dddkit/scripts/validate-ddd.py` (and `.dddkit/linter/target/release/dddkit check`) and resolve any SdSFC failures for this module

## Dependencies & Execution Order

- T001 and the shared composition root block everything else.
- T002 blocks T004; T003 and T004 block T005.
- T006 is written alongside T002–T005, not after them.
- T008 depends on T004 and T005 both being complete — it exercises the real HTTP path, not the placement function in isolation, because the property under test is a property of the whole request path.
- Polish depends on Phase 2 being complete.

## Cross-Module Dependencies

- **Depends on `ReferenceDomain/catalog`** for:
  - the `products` table and its `Product` model (catalog T008), which T004 issues its conditional `UPDATE` against;
  - the `CHECK (stock_quantity >= 0)` constraint created there, which is the database-level backstop for INV-006 — this module's guard lives in a `WHERE` clause, and the constraint is what makes a mistake in that guard fail loudly rather than silently oversell;
  - the shared composition root created in catalog's Phase 1 (`app/db.py`, `app/errors.py`, `app/main.py`, and the Docker files).
- This is the deliberate cross-aggregate write documented in both modules' `domain.md` and justified in `plan.md`'s Complexity Tracking. It is the one exception to module independence in this Bounded Context, and it runs in one direction only.

## Notes

- `[P]` tasks touch different files with no dependency.
- Verify tests fail before implementing, if tests are part of this module's plan.
- Commit after each task or logical group.
