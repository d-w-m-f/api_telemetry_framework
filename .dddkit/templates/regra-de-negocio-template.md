---
implements_uuid: [SAME_UUID_AS_DOMAIN_MD_AND_REPOMAP_MD]
version: 1.0.0
status: draft
---

# Business Rules: [MODULE_NAME]

<!--
  ACTION REQUIRED: This file lives NEXT TO THE CODE it documents (see the
  location this module's repomap.md resolves to), not under specs/. It is
  the fine-grained counterpart to domain.md - data flows, validations, and
  edge cases that are too implementation-specific for the spec layer but
  too important to leave undocumented.
-->

## Rules

<!--
  ACTION REQUIRED: One entry per rule. Each rule must be specific enough
  that "is this satisfied?" has an objective yes/no answer against the
  code sitting right next to this file.
-->

- **[RULE-001]**: [Precise statement of the rule, e.g. "Stock decrement is rejected if it would bring quantity below zero."]
- **[RULE-002]**: [Rule statement]

## Data Flow

[Describe how data moves through this module for its main operation(s) - inputs, transformations, outputs, side effects.]

## Validations

- [Field/input]: [validation rule and what happens on failure]

## Edge Cases

- **Given** [state], **When** [action], **Then** [expected outcome].

## Notes

- Keep this file in sync when the code changes; `validate-ddd.py` only checks that it *exists*, not that its content matches the code — that review is on the humans/agent making the change.
