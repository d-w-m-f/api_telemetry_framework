---
implements_uuid: e188f5df-2e2f-48c1-b127-c6887a5b5338
filename: vocabulary.md
version: 1.0.0
status: draft
---

# Vocabulary: catalog

## Terms

| Term | Definition | Usage Context |
|------|------------|----------------|
| Product | A distinct sellable item in the reference fixture, identified for all time by its SKU. Always the whole aggregate — never a row, record, or DTO. | Domain modeling, and every catalog read. |
| SKU | The immutable, caller-visible identity of a Product. Chosen by the fixture author, never generated, never reassigned to a different Product. | Catalog lookups, and every order line, which names a SKU rather than an internal id. |
| Unit Price | The price of exactly one unit of a Product, as a whole number of minor units. Always "current" in this module — the price an order was actually charged is the `orders` module's Recorded Unit Price, not this. | Catalog reads; the source value copied at order placement. |
| Minor Units | The integral denomination money is expressed in (cents). All prices and totals are whole numbers of minor units; fractional money is not representable anywhere in this fixture. | Every monetary field, in storage and on the wire. |
| Stock Level | The whole, non-negative count of units currently available to be sold. Reduced only by an accepted Order. | Catalog reads; the value contended over during order placement. |
| Sellable | Whether a Product is currently offered. A Product that is not sellable is invisible to catalog reads and cannot be ordered — indistinguishable from absent. | Catalog filtering; order-line validation. |
| Catalog Read | Any operation that only observes Products and never changes them. The fixture's dominant workload. | Benchmark load profiles; the read path being measured. |
| Oversell | The state in which accepted orders have consumed more units of a SKU than existed. A violation of INV-003, never an acceptable outcome, and the specific defect concurrent benchmarking is expected to provoke. | Concurrency testing; invariant discussion. |

## Terms Inherited from Shared Language

- **SdSFC (Spec-driven Single-File Components)** — see `.dddkit/shared_language.md`. This module's business rules live beside its source, not under `specs/`.
- **Âncora de Módulo (Module Anchor)** — see `.dddkit/shared_language.md`. This module's anchor is the `business-rules.md` carrying its `implements_uuid`; it is how the module is located in the source tree.
- **Wildcard de Implementação (`code_glob`)** — see `.dddkit/shared_language.md`. A hint for locating this module, not the authority on where it is.
- **Grafo Spec-Código (Spec-Code Graph)** — see `.dddkit/shared_language.md`. The chain from this module's `uuid` to its anchor, which the linter proves.

## Notes

- If a term here conflicts with the same word used in another Bounded Context, that is expected — ubiquitous language is local to its context. Do not "fix" the conflict; document it in the relationship section of `domain.md` instead.
- **Deliberate local narrowing**: "Unit Price" means *current* price in this module, but the `orders` module uses "Recorded Unit Price" for the frozen value captured at placement. The two are equal only at the instant an order is accepted. Keeping the names distinct is what stops FR-014 from being quietly violated by an implementation that recomputes totals from the live catalog.
