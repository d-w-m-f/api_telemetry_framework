---
filename: Constitution.md
version: [CONSTITUTION_VERSION]
status: draft
ratified: [RATIFICATION_DATE]
last_amended: [LAST_AMENDED_DATE]
---

<!--
  Sync Impact Report (prepend on every amendment, above this comment closes):
  Version: [OLD_VERSION] -> [NEW_VERSION]
  Modified principles: [list, or "none"]
  Added sections: [list, or "none"]
  Removed sections: [list, or "none"]
  Deferred TODOs: [list, or "none"]
-->

# [PROJECT_NAME] Constitution

This is the project's own engineering constitution — distinct from `.dddkit/DDD.md`, which governs how DDD modeling itself is done and is not edited through this document. Amended exclusively through `/constitution` after the first draft.

## Core Principles

<!--
  ACTION REQUIRED: Replace with the project's actual principles. DDD
  projects commonly need principles in these areas (use, adapt, or drop
  each as appropriate — this is a starting menu, not a fixed list):
    - Domain Integrity (e.g. "Bounded Context boundaries are never crossed
      by direct dependency; cross-context communication only through the
      patterns declared in each domain.md's relationships section")
    - Testing Philosophy (e.g. TDD mandatory, integration-test coverage
      requirements for cross-context contracts)
    - Technology Constraints (approved languages/frameworks/storage)
    - Data & Privacy (retention, PII handling)
    - Performance & SLAs (latency/throughput targets)
    - Review & Workflow (what gates a merge, who approves architectural
      changes beyond what DDD.md section 4 already requires)
-->

### [PRINCIPLE_1_NAME]

[PRINCIPLE_1_DESCRIPTION]

### [PRINCIPLE_2_NAME]

[PRINCIPLE_2_DESCRIPTION]

## Governance

<!--
  ACTION REQUIRED: amendment procedure, versioning policy (MAJOR = backward
  incompatible principle removal/redefinition, MINOR = new principle or
  materially expanded guidance, PATCH = wording/clarification only), and
  compliance review expectations.
-->

[GOVERNANCE_RULES]

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
