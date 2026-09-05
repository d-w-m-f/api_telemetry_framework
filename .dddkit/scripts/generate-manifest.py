#!/usr/bin/env python3
"""Regenerate .dddkit/integrations/dddkit.manifest.json with real sha256 hashes.

Same shape as .specify/integrations/speckit.manifest.json: lets validate-ddd.py
(and, later, a reinstall/upgrade flow) detect drift between the files DDD-Kit
shipped and what is actually on disk.
"""

import datetime
import hashlib
import json

from _common import get_project_root

EXCLUDED_NAMES = {"NOTE.md", "index.json", "__pycache__"}
EXCLUDED_DIR_NAMES = {"__pycache__"}


def sha256_of(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main():
    root = get_project_root()
    kit_dir = root / ".dddkit"
    manifest_path = kit_dir / "integrations" / "dddkit.manifest.json"

    files = {}
    for path in sorted(kit_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in EXCLUDED_NAMES:
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.relative_to(kit_dir).parts[:-1]):
            continue
        if path == manifest_path:
            continue
        rel = str(path.relative_to(root))
        files[rel] = sha256_of(path)

    manifest = {
        "integration": "dddkit",
        "version": "1.0.0",
        "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files": files,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest with {len(files)} file(s) to {manifest_path.relative_to(root)}")


if __name__ == "__main__":
    main()
