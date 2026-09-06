---
implements_uuid: 55aa03b8-dc2a-4bfb-9dba-16b3d4ce2ee3
filename: repomap.md
version: 1.0.0
status: draft
module_kind: folder
code_glob: "services/reference-api/app/orders/"
---

# Repomap: orders

## Code Location

- **`code_glob`**: matches the file(s)/directory the module is implemented in. Resolved by `.dddkit/scripts/build-index.py` into `.dddkit/index.json`; consumers should read the index rather than re-resolving this glob themselves.
- **`module_kind`**:
  - `folder` — the module is a directory. The business-rule file MUST be named `business-rules.md` inside that directory.
  - `file` — the module is a single source file. The business-rule file MUST be a markdown file sharing that file's name (e.g. `catalog.py` -> `catalog.md`), placed alongside it.

## Structure Notes

`models.py` (SQLAlchemy `Order` and `OrderLine`), `schemas.py` (placement request and order response), `placement.py` (the single transactional function holding the conditional UPDATE and the all-or-nothing guarantee), `router.py` (FastAPI routes), and `business-rules.md` (the SdSFC anchor).

## Business Rule File

- Path (once resolved): `services/reference-api/app/orders/business-rules.md`
- `validate-ddd.py` fails the build if this file is missing at the resolved path, or if `module_kind` does not match what is actually on disk (a glob that resolves to a single file with `module_kind: folder`, or vice versa).
