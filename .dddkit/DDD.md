<!--
Sync Impact Report
Version: 1.3.0 -> 2.0.0 (MAJOR: a mandated filename in section 3 was redefined
incompatibly; any repository already compliant with 1.x becomes non-compliant.)
Modified principles:
  - "3. The SdSFC Pattern", item 3 -> the business-rule file mandated for
    `module_kind: folder` is renamed from `regra-de-negocio.md` to
    `business-rules.md`, aligning the framework's last Portuguese-named
    artifact with the English-going-forward convention. The `module_kind: file`
    rule (a markdown file sharing the module's file name) is unchanged.
Added sections: none
Removed sections: none
Propagated to: .dddkit/headers.yaml (doc_type key `regra-de-negocio` ->
  `business-rules`; contract `version: 1` -> `2`, a breaking schema change),
  .dddkit/scripts/validate-ddd.py (check 2), .dddkit/scripts/README.md,
  .dddkit/templates/business-rules-template.md (file renamed),
  .dddkit/templates/{repomap,tasks,plan}-template.md,
  .claude/skills/{implement,implement-progress,generate-tasks,
  discover-bounded-context}/SKILL.md.
Not propagated (deliberate): workflow.md and plan/ are historical records of
  decisions as they were made, and are not retro-edited.
Deferred TODOs: none
-->

<!--
Sync Impact Report
Version: 1.2.0 -> 1.3.0 (MINOR: new section added, no principle removed)
Modified principles: none
Added sections:
  - "5. Versioning Convention" -> formalizes the SemVer bump rules per document
    type (previously only defined for DDD.md/Constitution.md) and the rule for
    when a Sync Impact Report is required (MINOR/MAJOR bumps only, not PATCH).
Removed sections: none
Deferred TODOs: none
-->

<!--
Sync Impact Report
Version: 1.1.0 -> 1.2.0 (MINOR: structural rewrite, no principle removed)
Modified principles:
  - "1.1/1.2 Dirmap" -> canonical spec root changed from specs/DDD-Kit/BoundedContexts/
    to specs/BoundedContexts/ (no DDD-Kit wrapper), matching the tree already in use.
  - "3. SdSFC" -> rewritten around UUID-based resolution. domain.md no longer carries
    implemented_in; that responsibility moves to repomap.md (code_glob + module_kind).
    A committed, script-generated .dddkit/index.json is now the source of truth agents
    and scripts consult to resolve a module, instead of re-globbing implemented_in at
    read time.
Added sections: none
Removed sections: none
Deferred TODOs: none
-->

---
id: META-DDD-CONST-01
filename: DDD.md
version: 2.0.0
status: approved
domain_type: meta
---

# Domain Driven Design (DDD) — Constitution and General Guidance

This specification acts as the project's **Constitution**. It defines the unbreakable rules of strategic domain separation, directory structure, and the spec-driven development pattern used by DDD-Kit (SdSFC).

Any agent, LLM, or human developer **MUST** validate architectural changes against this document.

## 1. Core Directory Rules

The root of these specifications is `specs/`. Inside it live the ubiquitous documents (this file and `shared_language.md`, both under `.dddkit/`), and the `BoundedContexts/` directory, which is the entry point for every domain spec.

### 1.1 Dirmap

```text
specs/
└── BoundedContexts/           # Entry point for domain specs
    ├── ContextA/               # PascalCase for Bounded Contexts
    │   ├── module-one/         # kebab-case for Modules
    │   │   ├── domain.md
    │   │   ├── vocabulary.md
    │   │   └── repomap.md
    │   └── [logical-folder]/   # [bracketed] to group modules
    │       └── module-two/
    └── ContextB/

.dddkit/
├── DDD.md                     # THIS FILE (the Constitution)
├── headers.yaml               # Expected frontmatter per document type
├── shared_language.md         # Global ubiquitous language
├── index.json                 # Generated: uuid -> {spec_path, code_path} cache
├── templates/                 # Templates for AI-generated artifacts
├── scripts/                   # Deterministic code (scaffolding, validation, indexing)
└── integrations/              # Integration manifests (file hashes)
```

### 1.2 Naming Rules and Levels

- **Bounded Contexts:** Named in `PascalCase` (e.g. `LabExperiments`, `ReferenceDomain`). Sit directly under `BoundedContexts/`.
- **Modules:** Named in `kebab-case` (e.g. `catalog-service`, `order-processing`). A module represents one subdomain and contains `domain.md`, `vocabulary.md`, and `repomap.md`.
- **Logical Folders:** Wrapped in brackets (e.g. `[infrastructure]`, `[core]`). May exist **only** two or more levels below `BoundedContexts/`. They cannot contain domain markdown files directly — they only group modules.

## 2. Spec Markdown Structure

Every specification markdown in this repository follows:

```markdown
---
(Frontmatter fields as defined per document type in headers.yaml)
---
# Content
```

## 3. The SdSFC Pattern (Spec-driven Single-File Components) and Traceability

The heart of DDD-Kit is keeping high-level documentation (here, under `specs/`) in sync with the real implementation in the source tree. Three documents cooperate per module, each owning one concern:

- **`domain.md`** — the *what*: domain modeling (aggregates, entities, invariants, relationships to other contexts). It carries the module's `uuid`, generated once at scaffold time and never reassigned.
- **`vocabulary.md`** — the ubiquitous language local to the module.
- **`repomap.md`** — the *where*: it points at the real source-code location for this module and describes its shape. It shares the same `uuid` as its sibling `domain.md` (same module, different angle).

1. **The spec under `specs/` is not the code.** `domain.md` and `vocabulary.md` hold the design; `repomap.md` holds the mapping to the implementation.
2. **`repomap.md` owns the code pointer.** It declares:
   - `code_glob`: a wildcard pointing at where the module lives in the real codebase (e.g. `src/**/catalog/`).
   - `module_kind`: `folder` or `file` — whether the module is implemented as a directory or a single file.
3. **The business rule lives with the code.** Inside the directory resolved by `code_glob`, there MUST exist a business-rule markdown file: `business-rules.md` when `module_kind: folder`, or a markdown file sharing the module's file name when `module_kind: file`. This keeps the fine-grained detail (data flows, specific validations, edge cases) right next to the code a developer is reading.
4. **UUID resolution is the source of truth.** `.dddkit/index.json` is a committed, script-generated cache mapping every module's `uuid` to its current `spec_path` and `code_path` (resolved from `repomap.md`'s `code_glob`). Agents, scripts, and skills (most directly `discover-bounded-context`, which every other pipeline skill invokes to resolve a module) resolve a module through this index, not by re-globbing `code_glob` live or by trusting a hardcoded path. Moving a directory on disk is safe as long as the index is rebuilt afterwards — the `uuid` never changes.
5. **Deterministic validation.** `.dddkit/scripts/validate-ddd.py` walks the specs, verifies `.dddkit/index.json` is not stale relative to the real `domain.md`/`repomap.md` files, confirms every resolved `code_path` has its business-rule file, checks every `context-map.md` entry has a matching (and no orphaned) folder under `BoundedContexts/`, and confirms `module_kind` matches what is actually on disk. A failing validation breaks the pipeline (or blocks the commit).

## 4. On Conflicts and AI Behavior

- The LLM is forbidden from inferring the creation of new Bounded Contexts without going through the architecture flow and explicit human approval.
- Any spec change that conflicts with this Constitution must be surfaced to the human, explaining the terms of the conflict. The Constitution has final authority.

## 5. Versioning Convention

Every document type in `headers.yaml` carries a `version` field. A bare number is not enough — this section fixes *when* to bump which part, extending the rule `Constitution.md` and this file already follow (see `.claude/skills/constitution/SKILL.md`) to every other versioned document:

| Doc type | MAJOR | MINOR | PATCH |
|---|---|---|---|
| `domain.md` | Invariant or aggregate removed/redefined in a breaking way | New aggregate, entity, or invariant added | Wording/clarification only |
| `vocabulary.md` | A term's definition changes in a way that invalidates prior usage | New term added | Wording/clarification only |
| `repomap.md` | `code_glob` or `module_kind` changes after the module has real code (moved/reshaped) | — (rare; most changes here are structural) | Description/notes wording |
| `context-map.md` | A Bounded Context is removed or merged | A Bounded Context is added | Wording/focus description changes |
| `interview.md` / `requirements.md` | — (these only ever grow) | A new round/requirement is added | A prior entry is reworded, not replaced |
| `Constitution.md` / `DDD.md` | Principle removed/redefined incompatibly | Principle added or materially expanded | Wording/clarification only |

A document's **first creation** (going from a template skeleton to its initial real content — e.g. `repomap.md`'s `code_glob` being filled in by `/plan-context` for the first time) is completing v1.0.0, not a bump. Bumps apply to *amending* a document that already has real content.

**Sync Impact Report threshold**: prepend a Sync Impact Report (version change, modified/added/removed content, deferred TODOs — see the one at the top of this file) for every MINOR or MAJOR bump. Skip it for PATCH-only changes, to avoid noise on pure wording fixes. New reports are prepended above older ones — never delete a prior report when adding a new one.
