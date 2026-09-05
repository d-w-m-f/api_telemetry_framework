# The dddkit linter (Rust)

The deterministic half of `DDD.md` §3 — and the only part of dddkit that does not
trust the agent. Everything else in the framework is prose instructions an LLM may
follow, follow partially, or narrate as done; this binary makes a *checkable* claim
about the repository instead.

It is a **referential-integrity checker over a distributed document graph, not a
reviewer**. It answers "is the structure intact?", never "is the content correct?"

## Build

```sh
cd .dddkit/linter && cargo build --release
# binary at .dddkit/linter/target/release/dddkit
```

Rust 1.98+, no system dependencies beyond a C linker. `target/` is gitignored and
excluded from the integrity manifest; `src/`, `Cargo.toml` and `Cargo.lock` are hashed
as framework source.

## Usage

```sh
dddkit check [--only graph|match|integrity]
             [--module <uuid|Context/module|module>]
             [--format text|json] [--fix] [--no-hint] [--verbose]
```

Unlike `validate-ddd.py`, root resolution is **cwd-relative**: the binary walks up from
the current directory looking for `.dddkit/`. The Python scripts resolve the root from
their own `__file__`, which is why they work from anywhere. An installed binary has no
such anchor.

| Exit | Meaning |
|---|---|
| 0 | No failures. Fixable and pending findings may still be reported. |
| 1 | At least one Failure. |
| 2 | Could not run (not in a dddkit project, unknown `--module`). |

## The three concerns

`--only` selects a concern, not a check number — numbering is an implementation detail
and is deliberately not public API.

| Concern | Protects | Replaces |
|---|---|---|
| `graph` | the spec-code graph resolves end to end | checks 1 + 2 |
| `match` | declared architecture == filesystem, both directions | check 3 |
| `integrity` | dddkit's own files match their recorded hashes | checks 4 + 5 |

## Severity ladder

See `.dddkit/shared_language.md` §5. The distinction the whole `--fix` design rests on:

- **Failure** — something that cannot be derived is missing or contradictory. Exit 1.
- **Fixable** — drift in *derived* data, always reconstructible from the uuid. Exit 0.
- **Pending** — the module simply hasn't reached this pipeline stage yet. Exit 0.
- **Ok** — shown only with `--verbose`.

## How a module is located

The uuid is the source of truth; `code_glob` is a hint.

1. **Hint** — if every module's `code_glob` still resolves to a single path whose anchor
   carries that module's uuid, the project is healthy and the whole-tree scan is skipped.
2. **Authority** — the moment any module fails its hint, the tree is scanned for Module
   Anchors (markdown carrying `implements_uuid`) and that scan becomes the sole authority.
   `specs/`, `.dddkit/`, `.git/` and gitignored paths are excluded — `vocabulary.md`,
   `repomap.md`, `plan.md`, `tasks.md` and `roadmap.md` all carry `implements_uuid`, so
   scanning `specs/` would make every module look duplicated.
3. **Shape** — `folder` modules are anchored by `business-rules.md`; `file` modules by a
   `<name>.md` sitting beside a `<name>.*` source file.

`--no-hint` forces step 2 and must produce **byte-identical** output. That equivalence is
the load-bearing test: correctness never rests on the hint.

## Deliberate divergences from `validate-ddd.py`

These are behaviour changes, not bugs:

| Situation | Python | Rust |
|---|---|---|
| Module directory moved, `code_glob` now stale | **error** ("matched nothing") | **Fixable** — the uuid is found and the glob is repaired |
| Module modelled but not yet planned/implemented | **error** (unresolved `code_glob`) | **Pending** — not a failure, or the linter would be unusable until every module is finished |
| `index.json` missing or stale | **error** | **Fixable** — it is a cache, always rebuildable |
| Code exists, `repomap.md` never finalized | not detected | **Fixable** — pointer backfilled from the anchor |

The first row is the reason the port exists: `workflow.md` asked for lookup "por uma
chave/ID/uuid, não por um PATH... se o user troca um dir de lugar, ainda dá pra achar",
and the Python implementation never searches for a uuid at all.

## What `--fix` will and will not touch

**Will**: `repomap.md`'s `module_kind`/`code_glob` frontmatter, and `.dddkit/index.json`.
Both are derived data, reconstructible from the uuid without a human decision.

**Will not**: source code, business-rule files (a generated stub would satisfy the check
while defeating its purpose), `contexts.md` or the context folders (that reconciliation is
`/map-contexts`' job, behind a human approval gate), and **the integrity manifests** —
regenerating a manifest to silence a hash mismatch defeats the entire tamper check. Confirm
the change was intentional, then run `generate-manifest.py` explicitly.

## Known limitations

- Frontmatter parsing is a deliberate port of `_common.parse_frontmatter`'s flat
  `key: value` leniency, not a real YAML parse. Malformed frontmatter fails silently
  (empty fields) rather than raising. Tightening this is a separate, announced change.
- Nothing validates frontmatter against `headers.yaml`, which exists to be exactly that
  schema. The most obvious missing check.
- The `match` concern still scans for backtick-wrapped PascalCase tokens anywhere in
  `contexts.md`. A context description mentioning `` `Postgres` `` would invent a phantom
  Bounded Context. Tightening it is a `DDD.md` convention change, not just an
  implementation choice.
- `index`, `manifest` and `scaffold` are not yet ported; the Python scripts remain the
  way to run those.
- Not wired into any git hook or CI. Exit codes make it ready to be; nothing does it yet.
