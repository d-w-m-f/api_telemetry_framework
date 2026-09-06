---
uuid: 55aa03b8-dc2a-4bfb-9dba-16b3d4ce2ee3
filename: domain.md
version: 1.0.0
status: draft
bounded_context: ReferenceDomain
module: orders
---

# Domain: orders

## Overview

The `orders` module owns the **Order** — the permanent record of a purchase that
was accepted, capturing what was bought, how many, and at what price at the
moment it was accepted. It is the write side of the fixture, and the only place
where concurrent requests genuinely contend with one another.

It exists as its own module rather than folded into `catalog` because an Order is
immutable and append-only where a Product is long-lived and mutable, and because
the act of accepting an Order is the fixture's single interesting transaction.
Keeping it separate makes the contended path explicit rather than incidental,
which is what allows different architectures to be compared on it fairly.

## Aggregates & Entities

### Order

- **Root Entity**: Order — an accepted purchase, identified by a server-generated
  identifier. Carries the customer reference it was placed under, its lines, its
  total, its status, and the instant it was placed. Once created it never changes.
- **Entities**: Order Line — one per distinct SKU in the Order, holding the SKU,
  the quantity ordered, and the unit price recorded at placement. A Line has no
  identity or meaning outside its Order and is never addressed independently;
  it is an entity rather than a value object only because quantity and recorded
  price together describe a distinct thing within the Order.
- **Value Objects**:
  - Customer Reference — an opaque, caller-supplied string. Deliberately not a
    modeled customer: the fixture has no accounts and no authentication.
  - Quantity — a whole number of units, always at least one.
  - Money — a whole number of minor units, identical in meaning to `catalog`'s
    Money. Shared without translation, since both modules sit in the same
    Bounded Context.
  - Order Status — the lifecycle position of an Order. In this fixture it has
    exactly one value; it exists for shape realism, not behavior.

## Invariants

- **INV-001**: An Order has at least one Order Line. An empty Order is not a
  representable state, not merely a rejected input.
- **INV-002**: No two Order Lines within the same Order name the same SKU. A
  request that repeats a SKU is rejected rather than merged, so that a request
  body maps to exactly one possible Order.
- **INV-003**: Every Order Line's quantity is at least one.
- **INV-004**: An Order Line's recorded unit price is the Product's unit price at
  the instant the Order was accepted, and never changes afterwards. It is never
  recomputed from the live catalog, however much later the Order is read.
- **INV-005**: An Order's total is exactly the sum over its Lines of quantity
  multiplied by recorded unit price. Because both are whole numbers of minor
  units, this is exact and carries no rounding.
- **INV-006**: An Order exists only if, in the same transaction that created it,
  every one of its Lines successfully decremented the stock of its SKU. There is
  no interleaving of concurrent placements that yields a persisted Order whose
  stock was never taken — this is INV-003 of `catalog` stated from the write side.
- **INV-007**: An Order is immutable once placed. It is never amended, cancelled,
  or re-priced; the fixture models no transition out of its initial status.
- **INV-008**: Acceptance is all-or-nothing. A rejected placement leaves both the
  set of Orders and every Product's stock exactly as they were before the request.

## Relationships to Other Bounded Contexts

- **`LabExperiments`** — Open Host Service: `ReferenceDomain` publishes a frozen
  HTTP contract that `LabExperiments` drives as an opaque load target.
  `LabExperiments` conforms to that contract, observes only its responses and
  timings, and never reaches into this module's storage. Order placement is the
  specific operation that contract exists to put under contention.

**Intra-context relationship (same Bounded Context):** this module reads and
decrements Product stock owned by the sibling `catalog` module, within the single
transaction that accepts an Order. The direction is strictly one-way — `catalog`
never reads or writes Orders. The reasoning for permitting this cross-aggregate
write, and why eventual consistency was rejected, is recorded in full in
`catalog`'s `domain.md`; it is referenced here rather than restated so that the
two modules cannot drift into giving different accounts of the same compromise.

## Open Questions

None. The one genuine modeling tension — a transaction spanning the Order and
Product aggregates — was resolved deliberately rather than deferred, and is
documented above and in `catalog/domain.md` instead of being left open.
