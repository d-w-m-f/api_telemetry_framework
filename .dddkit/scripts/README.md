# The DDD-Kit Linter (`validate-ddd.py`)

## What it is

A single Python 3 script, `.dddkit/scripts/validate-ddd.py`, no third-party dependencies (stdlib only: `hashlib`, `json`, `re`, `sys`, `pathlib`). It is the deterministic-validation half of DDD.md section 3 — the part that checks specs and code haven't drifted apart, rather than trusting the agent to have kept them in sync. It is Python by design choice, not by default: a Rust port was considered but deliberately deferred until the validation rules themselves stop changing (see `plan/009_implement.md`).

## CLI interface

There isn't much of one — that's accurate, not an omission:

```sh
python3 .dddkit/scripts/validate-ddd.py
```

- **No flags, no arguments.** Every run performs all 5 checks against the whole repo. There is no `--only <check>`, no way to scope to a single Bounded Context or module, and no `--json`/machine-readable output mode.
- **Works from any working directory.** Root resolution (`_common.get_project_root()`) is `__file__`-relative — three `.parent` calls up from the script's own location — never dependent on `cwd`. You can run it with a relative or absolute path from anywhere and it still finds the same repo root.
- **Exit code**: `0` if every check passes, `1` if any check reported at least one error. This makes it usable as-is in a pre-commit hook or CI step (`&& ` it, or check `$?`) — but nothing currently wires it in automatically. There is no git hook and no CI workflow in this repo yet; it's a manual, on-demand run.
- **Output**: plain text to stdout only, one `=== N. <check name> ===` header per check, then `OK:` / `ERROR:` / `WARNING:` lines. A trailing `Validation PASSED.` or `Validation FAILED with N error(s).` summary line.

## How it works: the 5 checks

Each check is its own function in `validate-ddd.py`, all called unconditionally from `main()`; their error counts are summed for the final exit code.

### 1. Index freshness (`.dddkit/index.json`)

For every module (a directory under `specs/BoundedContexts/**` containing a `domain.md`), reads the module's `uuid` from `domain.md`'s frontmatter and confirms:
- `.dddkit/index.json` exists at all (else: immediate error, "run `build-index.py`").
- That `uuid` has an entry in the index.
- The entry's `spec_path` matches the module's actual current directory.

Then, separately, flags any `index.json` entry whose `uuid` no longer corresponds to any real `domain.md` (an orphaned entry — e.g. left behind after a module was moved or deleted without rebuilding the index).

**Fix**: `python3 .dddkit/scripts/build-index.py`.

### 2. SdSFC — business-rule file next to the code

For every module, reads its `repomap.md` frontmatter (`code_glob`, `module_kind`) and:
- Errors if `repomap.md` is missing, or its `code_glob`/`module_kind` are still unresolved template placeholders.
- Resolves `code_glob` against the repo root (`root.glob(code_glob)`) — errors if it matches zero paths or more than one (it must resolve to exactly one).
- Errors if the resolved path's actual type (file vs. directory) doesn't match the declared `module_kind`.
- Checks for the business-rule file at that location: `business-rules.md` inside the resolved directory for `module_kind: folder`, or a same-named `.md` file next to it for `module_kind: file`.

**Fix**: run `/plan-context` if `code_glob`/`module_kind` aren't finalized yet; otherwise write the missing business-rule file (this is what `/implement` does automatically as it writes code).

### 3. `context-map.md` ↔ `BoundedContexts/` folders

Extracts every backtick-wrapped, PascalCase Bounded Context name (`` `LikeThis` ``) found anywhere in `specs/BoundedContexts/contexts.md`, and separately lists every `PascalCase`-named folder directly under `specs/BoundedContexts/`. Reports both directions of mismatch: a name with no folder, and a folder with no name. This is a plain-text regex scan (`` `([A-Z][A-Za-z0-9]*)` ``), not a structured parse — the convention it relies on is "wrap the name in backticks somewhere in that context's section," not a specific heading format.

**Fix**: run `/map-contexts` — it now knows how to propose exactly this kind of reconciliation (additive only, human-approved).

### 4 & 5. Manifest integrity (`dddkit.manifest.json`, `claude.manifest.json`)

Same check, run twice against the two manifests under `.dddkit/integrations/`. For every `path: sha256` entry in the manifest: confirm the file still exists, recompute its sha256, and compare. Reports a missing file or a hash mismatch as an error; an empty `files` list as a warning (not an error).

- `dddkit.manifest.json` covers everything under `.dddkit/` (templates, scripts, `DDD.md`, `headers.yaml`, `shared_language.md`), **except** `.dddkit/integrations/` itself — the two manifests deliberately never hash each other or themselves, since their own `installed_at` timestamp changes on every regeneration, which would make each go stale the instant the other is rebuilt.
- `claude.manifest.json` covers every file under `.claude/skills/<name>/` for skill folders **not** prefixed `speckit-` (that prefix belongs to GitHub Spec Kit, a separate integration, out of scope here).

**Fix**: `python3 .dddkit/scripts/generate-manifest.py --target dddkit` or `--target claude`, whichever manifest failed — but only after confirming the underlying file change was intentional, not corruption.

## Companion scripts

The linter only detects drift; these are what you run to fix what it finds.

| Script | Purpose | CLI |
|---|---|---|
| `build-index.py` | Rebuilds `.dddkit/index.json` from every module's `domain.md`/`repomap.md` | No arguments |
| `generate-manifest.py` | Regenerates one integrity manifest with real sha256 hashes | `--target dddkit\|claude` (default `dddkit`) |
| `scaffold-context.py` | Creates a new module's `domain.md`/`vocabulary.md`/`repomap.md` skeleton with a fresh uuid | `--context <PascalCase>`, `--module <kebab-case>`, optional `--logical-folder <name>` |

All three share the same zero-config, `__file__`-relative root resolution as the linter (`_common.get_project_root()`).

## Known limitations

- No way to run a single check or scope validation to one module/context — always the whole repo, all 5 checks.
- No machine-readable output (no `--json`) — anything consuming its result today has to parse the exit code and/or grep stdout.
- Not wired into any git hook or CI pipeline in this repo — running it is currently the caller's responsibility (several skills, like `/implement`, run it explicitly as their own final step).
- Frontmatter is read via a deliberately minimal flat `key: value` scanner (`_common.parse_frontmatter`), not a real YAML parser — this is fine because DDD-Kit frontmatter is never nested, but it means a malformed or nested frontmatter block fails silently (returns `{}` / missing fields) rather than raising a parse error.
