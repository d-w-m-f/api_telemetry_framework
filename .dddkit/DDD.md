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
version: 1.2.0
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
3. **The business rule lives with the code.** Inside the directory resolved by `code_glob`, there MUST exist a business-rule markdown file: `regra-de-negocio.md` when `module_kind: folder`, or a markdown file sharing the module's file name when `module_kind: file`. This keeps the fine-grained detail (data flows, specific validations, edge cases) right next to the code a developer is reading.
4. **UUID resolution is the source of truth.** `.dddkit/index.json` is a committed, script-generated cache mapping every module's `uuid` to its current `spec_path` and `code_path` (resolved from `repomap.md`'s `code_glob`). Agents, scripts, and future skills (e.g. `discover-bounded-context`) resolve a module through this index, not by re-globbing `code_glob` live or by trusting a hardcoded path. Moving a directory on disk is safe as long as the index is rebuilt afterwards — the `uuid` never changes.
5. **Deterministic validation.** `.dddkit/scripts/validate-ddd.py` walks the specs, verifies `.dddkit/index.json` is not stale relative to the real `domain.md`/`repomap.md` files, confirms every resolved `code_path` has its business-rule file, checks every `context-map.md` entry has a matching (and no orphaned) folder under `BoundedContexts/`, and confirms `module_kind` matches what is actually on disk. A failing validation breaks the pipeline (or blocks the commit).

## 4. On Conflicts and AI Behavior

- The LLM is forbidden from inferring the creation of new Bounded Contexts without going through the architecture flow and explicit human approval.
- Any spec change that conflicts with this Constitution must be surfaced to the human, explaining the terms of the conflict. The Constitution has final authority.
