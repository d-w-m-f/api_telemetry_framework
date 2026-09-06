---
id: [META-CONTEXTS-01]
filename: contexts.md
version: 1.0.0
status: draft
domain_type: meta
---

# Context Map

<!--
  ACTION REQUIRED: One subsection per Bounded Context that exists under
  specs/BoundedContexts/. Every context named here MUST have a matching
  PascalCase folder there, and every folder there MUST be named here -
  validate-ddd.py checks both directions and fails on any orphan.

  Convention: wrap the Bounded Context name in backticks at least once,
  anywhere in its subsection (the heading is the natural place). This is
  how validate-ddd.py finds context names in free-form headings - it does
  not require an exact "## ContextName" heading.
-->

## `[ContextName]`

- **Focus**: [What this Bounded Context is responsible for.]
- **Complexity**: [Low/Moderate/High] — [why]
- **Volatility**: [Stable/Evolving/Frozen] — [why; note if rules are fixed by decree vs. discovered iteratively]
- **Typical Implementation**: [What kinds of components live here.]

<!-- Repeat the subsection above for each additional Bounded Context. -->

## How to Map New Functionality

<!--
  ACTION REQUIRED: A short decision rule a human or agent can follow to
  decide which existing Bounded Context a new piece of functionality
  belongs to, or when it warrants a new one (subject to DDD.md section 4 -
  new Bounded Contexts require explicit human approval).
-->

- If the functionality is about [X], it goes to `[ContextName]`.
- If it is about [Y], it goes to `[OtherContextName]`.
