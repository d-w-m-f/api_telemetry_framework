# Project Context

This repo has two things going on at once — don't confuse them.

1. **`api_throughput_n_telemetry`** — the original project: an API benchmark/telemetry harness with a `LabExperiments` domain (measuring things) and a `ReferenceDomain` fixture (a frozen e-commerce domain APIs are benchmarked against). This is the actual product the framework below exists to help build.
2. **`dddkit`** — a Spec-Driven Development framework the owner is building from scratch (like GitHub Spec Kit, but DDD-flavored), designed and dogfooded inside this same repo. As of this session (2026-09-05), **dddkit's SDK is fully implemented** — this is what most of the recent work here is.

## dddkit: where to look

- **`.dddkit/DDD.md`** — the framework's constitution: directory rules, naming (`PascalCase` contexts, `kebab-case` modules), the SdSFC pattern (spec ↔ code traceability via UUID), and section 5's versioning/SemVer-bump convention. Read this first for anything structural.
- **`.dddkit/headers.yaml`** — the frontmatter contract for every document type dddkit produces.
- **`.dddkit/scripts/`** — `validate-ddd.py` (5-check linter: index freshness, SdSFC, context-map↔folder correspondence, two integrity manifests), `build-index.py` (rebuilds `.dddkit/index.json`, the uuid→path cache), `generate-manifest.py --target {dddkit,claude}` (regenerates the sha256 integrity manifests), `scaffold-context.py` (creates a module skeleton).
- **`.claude/skills/`** — 11 dddkit skills, the full SDK: `interview` → `map-requirements` → `constitution` → `map-contexts` → `model-context` → `plan-context` → `generate-tasks` → `implement` → `implement-progress`, plus `checklist` and `discover-bounded-context` (on-demand/internal tools). The `speckit-*` skills alongside them are GitHub Spec Kit — kept only as an infrastructure reference dddkit's own patterns were modeled on (manifests, templates, index), **not** part of the product being built.
- **`plan/001_*.md` through `plan/012_*.md`** (repo root) — the full design record: one file per skill, each with Goal/Inputs/Outputs/Design-Decisions/Open-Questions, and every open question's eventual resolution appended as a "Status: Implemented" note at the top. This is the place to understand *why* something was built the way it was, not just what.
- **`workflow.md`** (repo root, Portuguese) — the owner's original design brief that `plan/` was derived from. Historical source, not actively maintained.

## Before touching dddkit's structure

Run `python3 .dddkit/scripts/validate-ddd.py` first. It will tell you if specs are already out of sync with the codebase.

**Resolved 2026-09-05**: the `contexts.md` ↔ folders drift is gone — `ReferenceDomain/` was created, and the empty leftover `APIs/` and `Presentation/[backend|frontend]/` trees (never named in `contexts.md`, zero files, never tracked by git) were deleted. `validate-ddd.py` now passes all 5 checks.

**Open structural gap**: `specs/BoundedContexts/LabExperiments/` and `ReferenceDomain/` are empty directories, and git does not track empty directories. They exist on your working copy, so check 3 passes locally, but a fresh clone has neither folder and would fail check 3 with two errors. Nothing in dddkit reconciles that yet — decide on a convention (a `.gitkeep`, or having `/map-contexts` drop a stub file per context) before anyone else clones this repo.

## What's genuinely done vs. not

- **Done**: all 11 skills exist, are frontmatter-valid, and are registered. Both integrity manifests pass. The UUID/index resolution mechanism works (verified with a scaffolded throwaway module in an earlier session).
- **Not done**: nobody has run the pipeline end-to-end on real content yet. "Status: Implemented" in `plan/` means the skill was written and its design questions resolved — not that it's been battle-tested against a real `/interview` → `/implement` run. Expect rough edges the first time someone actually uses it for real.
- **Explicitly deferred** (don't invent an answer, ask the owner): "ground language" behavior (checking new terminology against `shared_language.md`/`vocabulary.md`) — the owner said they'll define this themselves. A Rust port of `validate-ddd.py` — intentionally staying Python until the validation rules stop changing.

## Working conventions for this repo

- Write all new code, docs, and templates in **English** going forward, even though `DDD.md`/`workflow.md`/`shared_language.md` are in Portuguese (pre-existing, not being retranslated unless asked).
- Prefer extending the two manifest-generation/validation scripts over hand-editing `.dddkit/integrations/*.manifest.json` — they're generated, not authored.
- `.dddkit/integrations/` files never hash each other or themselves (their `installed_at` timestamp would make that self-referential and immediately stale) — keep that exclusion if you touch `generate-manifest.py`.
