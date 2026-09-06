---
filename: tasks.md
implements_uuid: e188f5df-2e2f-48c1-b127-c6887a5b5338
version: 1.0.0
status: draft
---

# Tasks: catalog

**Input**: `plan.md` (required, with `repomap.md` finalized), `domain.md`.

## Format: `[ID] [P?] [Aggregate] Description`

- **[P]**: can run in parallel (different files, no dependency).
- **[Aggregate]**: which Aggregate from `domain.md`'s "Aggregates & Entities" section this task belongs to — this is the organizing axis (not user stories; dddkit modules are DDD-modeled, not feature-branch-shaped).
- An optional `(FR-###)` tag references `requirements.md` for traceability only — it is not the grouping key.
- Include exact file paths, resolved against `repomap.md`'s `code_glob`.

## Phase 1: Setup

> These tasks create the shared composition root that both `catalog` and
> `orders` are mounted into. It lives **outside** either module's `code_glob`
> and is therefore not covered by the spec-code graph — see Cross-Module
> Dependencies. It is placed in this module's tasks because `catalog` is
> implemented first, not because it belongs to `catalog`.

- [X] T001 Create the module source location `services/reference-api/app/catalog/` per `repomap.md`'s `code_glob`
- [X] T002 [P] Declare runtime dependencies in `services/reference-api/requirements.txt` per `plan.md` (FastAPI, SQLAlchemy 2.0, psycopg 3, Pydantic v2, Uvicorn, pytest, httpx)
- [X] T003 [P] Create `services/reference-api/app/db.py` — engine, session factory, and declarative `Base` (NFR-001: no state held in the process)
- [X] T004 [P] Create `services/reference-api/app/errors.py` — the machine-readable error-code enum and the exception→response handlers (FR-021, FR-022)
- [X] T005 Create `services/reference-api/app/main.py` — FastAPI app, startup schema creation via `create_all`, router registration (NFR-003: idempotent)
- [X] T006 [P] Create `services/reference-api/Dockerfile` (python:3.12-slim, non-root, uvicorn entrypoint)
- [X] T007 [P] Create `services/reference-api/docker-compose.yml` — Postgres 16 with a healthcheck, plus the API service gated on it (NFR-002: one `docker compose up`, no manual step)

## Phase 2: Product

**Goal**: the Product aggregate is queryable, its stock invariant is enforced by Postgres rather than by application code, and the fixture catalog is reproducible.

- [X] T008 [Product] Create the `Product` model at `services/reference-api/app/catalog/models.py` — SKU primary key, name, `unit_price_cents`, `stock_quantity`, `sellable`, with `CHECK (stock_quantity >= 0)` and `CHECK (unit_price_cents >= 0)` table constraints (INV-002, INV-003)
- [X] T009 [P] [Product] Create response schemas at `services/reference-api/app/catalog/schemas.py` — `ProductOut`, `ProductPage` (money as integer minor units only)
- [X] T010 [Product] Implement reads at `services/reference-api/app/catalog/queries.py` — `list_products(limit, offset)` filtering to sellable, and `get_product(sku)` returning `None` for absent-or-unsellable (INV-004) (depends on T008)
- [X] T011 [Product] Implement routes at `services/reference-api/app/catalog/router.py` — `GET /catalog/products` with page-size default 50 / max 200 rejected above the cap, and `GET /catalog/products/{sku}` returning 404 with a stable error code (FR-001, FR-002, FR-003, FR-004) (depends on T009, T010)
- [X] T012 [P] [Product] Create the deterministic fixture catalog at `services/reference-api/app/catalog/seed.py` — a literal, ordered product list; identical on every run (FR-019, NFR-004)
- [X] T013 [Product] Create the business-rule file at `services/reference-api/app/catalog/business-rules.md` documenting this aggregate's rules, data flow, validations, and edge cases — **must land in the same pass as T008–T012 above, not deferred**

## Phase 3: Polish

- [X] T014 [P] Create `services/reference-api/app/admin.py` — `POST /admin/reset` (truncate orders, re-seed catalog) and `GET /health` reporting database reachability (FR-019, FR-020)
- [X] T015 [P] Tests at `services/reference-api/tests/test_catalog.py` — listing, pagination bounds, unknown SKU, non-sellable SKU invisibility
- [X] T016 Run `.dddkit/scripts/validate-ddd.py` (and `.dddkit/linter/target/release/dddkit check`) and resolve any SdSFC failures for this module

## Dependencies & Execution Order

- Setup (T001–T007) blocks everything else.
- T008 blocks T010; T009 and T010 block T011.
- T013 is written alongside T008–T012, not after them.
- Polish depends on Phase 2 being complete.
- This module's Aggregate has no dependency on `orders`' Aggregate: `catalog` never reads or writes Orders. The dependency runs strictly the other way.

## Cross-Module Dependencies

- **`ReferenceDomain/orders` depends on this module**, not the reverse: order placement issues a conditional `UPDATE` against the `products` table defined by T008, and relies on the `CHECK (stock_quantity >= 0)` constraint created there for its own INV-006. Changing the `Product` model's stock column is therefore a breaking change for `orders`.
- **Shared composition root**: T003–T007 and T014 create files under `services/reference-api/` that lie outside *both* modules' `code_glob`. No module owns them, and consequently the spec-code graph does not cover them — a gap noted here deliberately rather than papered over by stretching a `code_glob` to swallow files it does not own.

## Notes

- `[P]` tasks touch different files with no dependency.
- Verify tests fail before implementing, if tests are part of this module's plan.
- Commit after each task or logical group.
