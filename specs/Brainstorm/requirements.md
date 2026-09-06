---
filename: requirements.md
version: 1.0.0
status: draft
---

# Requirements

<!--
  Produced by /map-requirements. Every requirement gets a stable ID
  (FR-### / NFR-###) so later work can trace coverage back to it. Re-runs
  append new requirements, continuing the numbering — never renumber
  existing IDs, since other artifacts may already reference them.
-->

## Functional Requirements

### Catalog

- **FR-001**: System MUST return a paginated list of catalog products, each carrying at minimum its SKU, name, unit price, and available stock quantity.
- **FR-002**: System MUST return a single product by its SKU, and MUST respond `404` when no product carries that SKU.
- **FR-003**: System MUST exclude products marked not-sellable from catalog listings, and MUST respond `404` for a direct read of a not-sellable product's SKU — a not-sellable product is indistinguishable from a nonexistent one to a catalog reader.
- **FR-004**: System MUST accept a page size parameter on listings, MUST apply a documented default when it is absent, and MUST reject a page size above the documented maximum rather than silently clamping it.

### Order Placement

- **FR-005**: System MUST accept an order consisting of an opaque customer reference and one or more lines, each naming a SKU and an integer quantity.
- **FR-006**: System MUST reject an order carrying zero lines.
- **FR-007**: System MUST reject an order line whose quantity is less than 1.
- **FR-008**: System MUST reject an order naming the same SKU on more than one line, rather than merging those lines.
- **FR-009**: System MUST reject an order referencing a SKU that does not exist or is not sellable.
- **FR-010**: System MUST reject an order whose requested quantity for any SKU exceeds that SKU's available stock at the moment of placement.
- **FR-011**: System MUST decrement each ordered SKU's stock by the ordered quantity when, and only when, the order is accepted.
- **FR-012**: System MUST NOT allow a SKU's stock to fall below zero under any interleaving of concurrent order placements. Two concurrent orders for the last available unit MUST result in exactly one acceptance and one rejection.
- **FR-013**: System MUST apply order placement atomically: a rejected order MUST leave stock and persisted orders exactly as they were before the request.
- **FR-014**: System MUST record the unit price in effect at placement time on each order line, and MUST NOT recompute it afterwards from the current catalog price.
- **FR-015**: System MUST compute and persist an order total equal to the sum of its lines' quantity × recorded unit price.
- **FR-016**: System MUST return the created order's identifier on acceptance.

### Order Retrieval

- **FR-017**: System MUST return a previously placed order by its identifier, including its lines, recorded unit prices, total, status, and placement timestamp.
- **FR-018**: System MUST respond `404` for an order identifier that was never placed.

### Fixture Operation

- **FR-019**: System MUST provide an operation that resets the database to a known seed catalog and removes all placed orders, so that a benchmark run starts from a documented, identical state.
- **FR-020**: System MUST expose a health endpoint that reports whether the database is reachable, distinguishing "process up" from "process up and able to serve".

### Error Semantics

- **FR-021**: Every rejection defined above MUST carry a stable, machine-readable error code in its response body, distinct per rejection reason, so a load generator can tell an expected domain rejection from an infrastructure failure.
- **FR-022**: System MUST answer domain rejections (FR-006 through FR-010) with a `4xx` status and MUST reserve `5xx` for genuine faults — a business-rule rejection is never a server error.

## Non-Functional Requirements

- **NFR-001**: The API process MUST be stateless — all mutable state lives in PostgreSQL — so the benchmark harness can run additional replicas without changing observable behavior.
- **NFR-002**: The full stack MUST start from a fresh clone with a single `docker compose up` and no manual setup step.
- **NFR-003**: Schema creation and seeding MUST be idempotent: repeating them MUST converge to the same state rather than erroring or duplicating rows.
- **NFR-004**: Two runs of FR-019 (reset) MUST produce identical catalog contents, so measurements taken across runs are comparable.
- **NFR-005**: The service MUST NOT introduce caching, message brokers, background schedulers, or read replicas. These are the architectural variables the benchmark exists to compare; embedding them in the fixture would prejudge the measurement.
- **NFR-006**: FR-012 MUST be demonstrated by an automated concurrency test, not asserted by inspection — oversell is precisely the defect a high-concurrency benchmark manufactures.
- **NFR-007**: The service MUST NOT require authentication, so that measured latency reflects domain work rather than auth overhead.

## Assumptions

<!-- Reasonable defaults chosen instead of asking, when no reasonable default existed to skip entirely. -->

- Money is stored and transported as an integer count of minor units (cents), never as a float. A single implicit currency is assumed; no currency field is modeled, because a fixture compared against itself never needs conversion.
- The customer reference is an opaque, caller-supplied string. No customer entity, account, or authentication is modeled (per NFR-007).
- Pagination defaults to 50 items with a maximum of 200 (FR-004). These numbers are arbitrary but must be documented and stable, since page size affects measured throughput.
- Order identifiers are UUIDs, generated server-side. A caller-supplied idempotency key is deliberately not modeled — retry semantics are a benchmark variable, not fixture behavior.
- Timestamps are UTC, ISO 8601.
- "Not sellable" is modeled as a single boolean on the product rather than a lifecycle state machine, matching the fixture's frozen-and-simple mandate.
- Orders are terminal once placed: there is no cancellation, fulfillment, or return transition. Order status exists as a field for shape realism but has exactly one value in this fixture.
- The reset operation (FR-019) is exposed unauthenticated alongside the domain API, since the whole service is a disposable measurement target rather than a deployed system. It is a fixture-control operation, not a domain capability.

## Open Clarifications

<!--
  Max 3 per /map-requirements run, prioritized scope > security/privacy >
  UX > technical detail. Resolve before the requirements are considered
  ready to feed /map-contexts.
-->

None this run. Every ambiguity encountered had a defensible default given the
fixture framing, and is recorded under Assumptions above rather than deferred.
