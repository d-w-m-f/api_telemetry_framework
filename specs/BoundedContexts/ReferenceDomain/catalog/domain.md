---
uuid: e188f5df-2e2f-48c1-b127-c6887a5b5338
filename: domain.md
version: 1.0.1
status: draft
bounded_context: ReferenceDomain
module: catalog
---

# Domain: catalog

## Overview

The `catalog` module owns the **Product** — the sellable item that the reference
e-commerce fixture offers, together with the stock level that says how many of it
remain. It is the read side of the fixture: it answers "what can be bought, at
what price, and is any left?"

It exists as its own module rather than folded into `orders` because Product and
Order have genuinely different lifecycles. A Product is long-lived, mutated only
by stock movement, and read overwhelmingly more often than written. An Order is
created once and never changes. Collapsing them would put the fixture's hottest
read path and its only contended write path behind a single boundary, which is
precisely the distinction the benchmark is built to observe.

## Aggregates & Entities

### Product

- **Root Entity**: Product — a distinct sellable item, identified for all time by
  its SKU. Carries its display name, its current unit price, the quantity on
  hand, and whether it is currently offered for sale.
- **Entities**: none. The Product aggregate is deliberately a single entity with
  no internal children — the fixture has no variants, bundles, or media, and
  adding them would make each re-implementation a different amount of work.
- **Value Objects**:
  - Sku — the immutable, human-readable identity of a Product.
  - Money — an amount expressed as a whole number of minor units (cents). Never
    a fractional type, so that totals are exact and identical across every
    architecture implementing this fixture.
  - StockLevel — a non-negative whole count of units available to be sold.
  - Sellability — whether the Product is currently offered. Modeled as a plain
    boolean rather than a lifecycle state, matching the fixture's frozen mandate.

## Invariants

- **INV-001**: A SKU identifies exactly one Product, and is never reassigned to a
  different Product — not even after the original ceases to be sellable.
- **INV-002**: A Product's unit price is a whole number of minor units and is
  never negative. Zero is permitted; a negative price is not representable.
- **INV-003**: A Product's stock level is a whole number and is never negative.
  This holds under every possible interleaving of concurrent order placements,
  not merely when requests arrive one at a time.
- **INV-004**: A Product that is not sellable is invisible to catalog reads. To a
  reader it is indistinguishable from a Product that never existed — there is no
  observable state between "offered" and "absent".
- **INV-005**: A Product's stock level changes only as the recorded consequence
  of an accepted Order. Stock is never adjusted as a side effect of a read.

## Relationships to Other Bounded Contexts

- **`LabExperiments`** — Open Host Service: `ReferenceDomain` publishes a frozen
  HTTP contract that `LabExperiments` drives as an opaque load target.
  `LabExperiments` conforms to that contract and never reaches into this
  module's storage. The contract is deliberately stable: changing it would
  invalidate the comparative history already measured through it.

**Intra-context relationship (same Bounded Context, recorded here because it
constrains this module's design):** the sibling `orders` module decrements this
module's stock as part of accepting an Order. That is a **cross-aggregate write
inside a single transaction**, which classical DDD would normally forbid in
favour of eventual consistency between aggregates.

It is accepted here deliberately and knowingly. Eventual consistency between
Order and Product permits a window in which stock is oversold and later
compensated — and INV-003 forbids exactly that. Because oversell under
concurrency is one of the defects this fixture exists to detect, the fixture
cannot itself be built on a model that tolerates it. The compromise is the
narrower one: a single transactional boundary spanning two aggregates, entered
only by `orders`, and never the reverse.

## Open Questions

None. Every ambiguity in this module was resolved by the fixture framing: where a
choice existed, the simpler and more frozen option was taken, and the reasoning
is recorded in `specs/Brainstorm/requirements.md` under Assumptions.
