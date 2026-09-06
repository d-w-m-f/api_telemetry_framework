---
implements_uuid: 55aa03b8-dc2a-4bfb-9dba-16b3d4ce2ee3
filename: vocabulary.md
version: 1.0.0
status: draft
---

# Vocabulary: orders

## Terms

| Term | Definition | Usage Context |
|------|------------|----------------|
| Order | The permanent, immutable record of an accepted purchase. Always the whole aggregate, including its Lines. An Order that was rejected does not exist — there is no such thing as a failed Order. | Order placement and retrieval; the write path being measured. |
| Order Line | One entry within an Order: a SKU, a quantity, and the unit price recorded at placement. Never addressed or modified independently of its Order. | Placement requests; order retrieval. |
| Placement | The single operation that validates a requested purchase, takes stock for it, and records an Order — atomically. The fixture's only contended transaction. | Concurrency discussion; benchmark write profiles. |
| Recorded Unit Price | The price of one unit as it stood at the instant of Placement, frozen onto the Order Line. Distinct from `catalog`'s Unit Price, which is the live current price; the two coincide only at the moment of acceptance. | Order retrieval; total computation. |
| Order Total | The sum over an Order's Lines of quantity times Recorded Unit Price, in minor units. Persisted rather than derived on read, so a stored Order can never disagree with its own arithmetic. | Order retrieval; INV-005 verification. |
| Customer Reference | An opaque, caller-supplied string identifying who placed an Order. Not a modeled customer, not authenticated, and never validated against anything. | Placement requests. |
| Rejection | A refusal to place an Order on domain grounds — unknown SKU, insufficient stock, malformed lines. Always answered `4xx` with a stable machine-readable code, and always leaves the system exactly as it was. Never a fault. | Error semantics; benchmark error-rate accounting. |
| All-or-Nothing | The property that a Placement either records an Order and takes all its stock, or changes nothing at all. Never a partial decrement. | INV-008; transaction design. |

## Terms Inherited from Shared Language

- **SdSFC (Spec-driven Single-File Components)** — see `.dddkit/shared_language.md`. This module's business rules live beside its source, not under `specs/`.
- **Âncora de Módulo (Module Anchor)** — see `.dddkit/shared_language.md`. This module's anchor is the `business-rules.md` carrying its `implements_uuid`.
- **Wildcard de Implementação (`code_glob`)** — see `.dddkit/shared_language.md`. A hint for locating this module, not the authority on where it is.
- **Achado Corrigível vs. Falha (Fixable Finding vs. Failure)** — see `.dddkit/shared_language.md`. Relevant here because this module's spec-to-code link is what the linter checks once `/ddd-implement` has run.

## Notes

- If a term here conflicts with the same word used in another Bounded Context, that is expected — ubiquitous language is local to its context. Do not "fix" the conflict; document it in the relationship section of `domain.md` instead.
- **Deliberate local narrowing**: "Rejection" here means a domain refusal only. An infrastructure fault is never called a Rejection, because the whole point of the distinction (Constitution principle V) is that a load generator must be able to tell the two apart from the response alone.
