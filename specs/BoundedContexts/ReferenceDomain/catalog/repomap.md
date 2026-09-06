---
implements_uuid: e188f5df-2e2f-48c1-b127-c6887a5b5338
filename: repomap.md
version: 1.0.0
status: draft
module_kind: folder
code_glob: "services/reference-api/app/catalog/"
---

# Repomap: catalog

## Code Location

- **`code_glob`**: matches the file(s)/directory the module is implemented in. Resolved by `.dddkit/scripts/build-index.py` into `.dddkit/index.json`; consumers should read the index rather than re-resolving this glob themselves.
- **`module_kind`**:
  - `folder` — the module is a directory. The business-rule file MUST be named `business-rules.md` inside that directory.
  - `file` — the module is a single source file. The business-rule file MUST be a markdown file sharing that file's name (e.g. `catalog.py` -> `catalog.md`), placed alongside it.

## Structure Notes

`models.py` (SQLAlchemy `Product`, carrying the `CHECK (stock_quantity >= 0)` constraint), `schemas.py` (Pydantic shapes), `queries.py` (read functions, isolated so the read path is measurable on its own), `router.py` (FastAPI routes), `seed.py` (the deterministic fixture catalog), and `business-rules.md` (the SdSFC anchor).

## Business Rule File

- Path (once resolved): `services/reference-api/app/catalog/business-rules.md`
- `validate-ddd.py` fails the build if this file is missing at the resolved path, or if `module_kind` does not match what is actually on disk (a glob that resolves to a single file with `module_kind: folder`, or vice versa).
