---
uuid: [GENERATED_UUID]
filename: domain.md
version: 1.0.0
status: draft
bounded_context: [PASCAL_CASE_CONTEXT_NAME]
module: [kebab-case-module-name]
---

# Domain: [MODULE_NAME]

<!--
  ACTION REQUIRED: This file describes WHAT the module is about, in domain
  terms only. It never contains a code pointer - that lives in the sibling
  repomap.md (code_glob + module_kind). Do not add implementation details
  (frameworks, storage engines, endpoints) here.
-->

## Overview

[One paragraph: what this module is responsible for, and why it exists as its own module rather than being folded into a neighboring one.]

## Aggregates & Entities

<!--
  ACTION REQUIRED: List each Aggregate Root, its Entities, and its Value
  Objects. One subsection per Aggregate.
-->

### [Aggregate Name]

- **Root Entity**: [Name] — [what it represents]
- **Entities**: [Entity1], [Entity2] — [relationship to the root]
- **Value Objects**: [ValueObject1] — [what it captures]

## Invariants

<!--
  ACTION REQUIRED: Rules that must always hold true for this domain,
  independent of any specific use case. These are business rules the
  domain itself enforces, not validation on a single field.
-->

- [INV-001]: [Invariant statement, e.g. "An Order cannot be shipped before payment is confirmed."]
- [INV-002]: [Invariant statement]

## Relationships to Other Bounded Contexts

<!--
  ACTION REQUIRED: For each relationship, name the other Bounded Context and
  the DDD relationship pattern (Shared Kernel, Customer-Supplier,
  Conformist, Anticorruption Layer, Open Host Service, Published Language).
-->

- **[OtherContext]** — [relationship pattern]: [what is exchanged or shared, and why]

## Open Questions

<!--
  Use this marker for anything that blocks modeling this module further.
  Keep it to the questions that actually change scope or structure - not
  every implementation detail needs one. Resolve and remove before status
  moves past "review".
-->

- [NEEDS CLARIFICATION: specific question]
