# Project Context

This repo has two things going on at once — don't confuse them.

1. **`api_throughput_n_telemetry`** — the original project: an API benchmark/telemetry harness with a `LabExperiments` domain (measuring things) and a `ReferenceDomain` fixture (a frozen e-commerce domain APIs are benchmarked against). This is the actual product the framework below exists to help build.
2. **`dddkit`** — a Spec-Driven Development framework the owner is building from scratch (like GitHub Spec Kit, but DDD-flavored), designed and dogfooded inside this same repo. As of this session (2026-09-05), **dddkit's SDK is fully implemented** — this is what most of the recent work here is.

## dddkit: where to look

- **`.dddkit/DDD.md`** — the framework's constitution: directory rules, naming (`PascalCase` contexts, `kebab-case` modules), the SdSFC pattern (spec ↔ code traceability via UUID), and section 5's versioning/SemVer-bump convention. Read this first for anything structural.
- **`.dddkit/headers.yaml`** — the frontmatter contract for every document type dddkit produces.
- **`.dddkit/linter/`** — the Rust linter (`dddkit check`). Same three concerns as `validate-ddd.py` but uuid-first, with a `Pending`/`Fixable`/`Failure` severity ladder and `--fix`. `.dddkit/linter/README.md` documents every deliberate divergence between the two; keep that table current if you change either.
- **`.dddkit/scripts/`** — `validate-ddd.py` (5-check linter: index freshness, SdSFC, context-map↔folder correspondence, two integrity manifests), `build-index.py` (rebuilds `.dddkit/index.json`, the uuid→path cache), `generate-manifest.py --target {dddkit,claude}` (regenerates the sha256 integrity manifests), `scaffold-context.py` (creates a module skeleton).
- **`.dddkit/PIPELINE.md`** — what each skill does and the minimum/complete workflows they compose into. Read this before running the pipeline; `DDD.md` governs, `PIPELINE.md` explains.
- **`.claude/skills/`** — 11 dddkit skills, the full SDK: `interview` → `map-requirements` → `constitution` → `map-contexts` → `model-context` → `plan-context` → `generate-tasks` → `implement` → `implement-progress`, plus `checklist` and `discover-bounded-context` (on-demand/internal tools). The `speckit-*` skills and `.specify/` were deleted on 2026-09-06 — dddkit no longer needs Spec Kit as an infrastructure reference. Prose in a few skills still compares a design decision to `speckit-plan`/`speckit-tasks`; those are references to an external project, not to anything in this repo.
- **`plan/001_*.md` through `plan/013_*.md`** (repo root) — the full design record: one file per skill, each with Goal/Inputs/Outputs/Design-Decisions/Open-Questions, and every open question's eventual resolution appended as a "Status: Implemented" note at the top. This is the place to understand *why* something was built the way it was, not just what.
- **`.issues/`** — ideas raised but deliberately not implemented, one file per idea, each recording the original intent verbatim plus what is already true in the repo. Not a backlog.
- **`workflow.md`** (repo root, Portuguese) — the owner's original design brief that `plan/` was derived from. Historical source, not actively maintained.

## Before touching dddkit's structure

Run `python3 .dddkit/scripts/validate-ddd.py` first. It will tell you if specs are already out of sync with the codebase.

**Resolved 2026-09-05**: the `contexts.md` ↔ folders drift is gone — `ReferenceDomain/` was created, and the empty leftover `APIs/` and `Presentation/[backend|frontend]/` trees (never named in `contexts.md`, zero files, never tracked by git) were deleted. `validate-ddd.py` now passes all 5 checks.

**Open structural gap** (narrowed 2026-09-06): `specs/BoundedContexts/LabExperiments/` is still an empty directory, and git does not track empty directories — it exists on your working copy, so check 3 passes locally, but a fresh clone would not have it and would fail check 3. `ReferenceDomain/` is no longer affected: the dogfood run filled it with real files. Nothing in dddkit reconciles this yet — decide on a convention (a `.gitkeep`, or having `/map-contexts` drop a stub file per context) before anyone else clones this repo.

## What's genuinely done vs. not

- **Done**: all 11 skills exist, are frontmatter-valid, and are registered. Both integrity manifests pass. The UUID/index resolution mechanism works (verified with a scaffolded throwaway module in an earlier session).
- **Done 2026-09-06**: the pipeline has been run end-to-end on real content — `/interview` through `/implement` produced `specs/Brainstorm/`, `specs/Constitution.md`, the `ReferenceDomain` catalog and orders modules, and the FastAPI+Postgres service at `services/reference-api/` (33 tests). The findings that run produced are in `.issues/` and in this session's history; two were fixed (the `module-not-implemented` vs `module-anchor-missing` split, and `requirements.txt` being gitignored), the rest are open.
- **Not done**: `LabExperiments` has no modules — the benchmark harness the `ReferenceDomain` fixture exists to measure does not exist yet. There is no CI, no README, and no install path for dddkit into a fresh repo (see `.issues/003`).
- **Explicitly deferred** (don't invent an answer, ask the owner): "ground language" behavior (checking new terminology against `shared_language.md`/`vocabulary.md`) — the owner said they'll define this themselves.
- **Known open framework defects** (found by dogfooding, not yet fixed): `headers.yaml` is a contract nothing validates; the Sync Impact Report convention makes `parse_frontmatter` return `{}` for `DDD.md`/`shared_language.md`/`Constitution.md`, which becomes data-losing the first time a `domain.md` is MINOR-bumped; `constitution-template.md` and the `/constitution` skill disagree on where that report goes; and `validate-ddd.py` exits 1 on states its own pipeline documents as normal.

## Working conventions for this repo

- Write all new code, docs, and templates in **English** going forward, even though `DDD.md`/`workflow.md`/`shared_language.md` are in Portuguese (pre-existing, not being retranslated unless asked).
- Prefer extending the two manifest-generation/validation scripts over hand-editing `.dddkit/integrations/*.manifest.json` — they're generated, not authored.
- `.dddkit/integrations/` files never hash each other or themselves (their `installed_at` timestamp would make that self-referential and immediately stale) — keep that exclusion if you touch `generate-manifest.py`.
