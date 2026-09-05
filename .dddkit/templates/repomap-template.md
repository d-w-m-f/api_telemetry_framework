---
implements_uuid: [SAME_UUID_AS_DOMAIN_MD]
filename: repomap.md
version: 1.0.0
status: draft
module_kind: [folder|file]
code_glob: "[e.g. src/**/catalog/]"
---

# Repomap: [MODULE_NAME]

<!--
  ACTION REQUIRED: This file answers WHERE the module documented in the
  sibling domain.md actually lives in the source tree, and HOW it is
  shaped. It is the only file allowed to point at real code paths - do not
  add a code pointer to domain.md or vocabulary.md.
-->

## Code Location

- **`code_glob`**: matches the file(s)/directory the module is implemented in. Resolved by `.dddkit/scripts/build-index.py` into `.dddkit/index.json`; consumers should read the index rather than re-resolving this glob themselves.
- **`module_kind`**:
  - `folder` — the module is a directory. The business-rule file MUST be named `business-rules.md` inside that directory.
  - `file` — the module is a single source file. The business-rule file MUST be a markdown file sharing that file's name (e.g. `catalog.py` -> `catalog.md`), placed alongside it.

## Structure Notes

<!--
  ACTION REQUIRED: Briefly describe the internal layout a reader should
  expect once they resolve code_glob - e.g. "handlers/, repository/,
  service.py" for a folder module, or "a single class with no
  sub-structure" for a file module. This is guidance for humans and agents
  navigating the code, not a second source of truth for module_kind.
-->

[Short description of the internal layout.]

## Business Rule File

- Path (once resolved): `[code_glob resolution]/business-rules.md` or `[code_glob resolution]/[module-file-name].md`
- `validate-ddd.py` fails the build if this file is missing at the resolved path, or if `module_kind` does not match what is actually on disk (a glob that resolves to a single file with `module_kind: folder`, or vice versa).
