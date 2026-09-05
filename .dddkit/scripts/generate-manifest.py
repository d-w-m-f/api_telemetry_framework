#!/usr/bin/env python3
"""Regenerate a DDD-Kit integration manifest with real sha256 hashes.

--target dddkit (default): hashes everything under .dddkit/ into
  .dddkit/integrations/dddkit.manifest.json.
--target claude: hashes the dddkit-owned skill files under .claude/skills/
  (any skill folder NOT prefixed "speckit-", which is out of scope - that's
  GitHub Spec Kit's own integration) into
  .dddkit/integrations/claude.manifest.json.

Same shape as .specify/integrations/speckit.manifest.json: lets
validate-ddd.py (and, later, a reinstall/upgrade flow) detect drift between
the files an integration shipped and what is actually on disk.
"""

import argparse
import datetime
import hashlib
import json

from _common import get_project_root

EXCLUDED_NAMES = {"NOTE.md", "index.json", "__pycache__"}
# "target" is the Rust linter's build output: regenerated artifacts, not
# framework source. Its src/ and Cargo.toml/Cargo.lock are hashed as normal.
EXCLUDED_DIR_NAMES = {"__pycache__", "target"}


def sha256_of(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def collect_dddkit_files(root):
    kit_dir = root / ".dddkit"
    files = {}
    for path in sorted(kit_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in EXCLUDED_NAMES:
            continue
        rel_parts = path.relative_to(kit_dir).parts
        if rel_parts[0] == "integrations":
            # Manifests never track other manifests (or themselves) - their
            # installed_at timestamp changes on every regen, which would make
            # dddkit.manifest.json go stale the instant claude.manifest.json
            # is regenerated, and vice versa. Same convention speckit uses:
            # .specify/integrations/speckit.manifest.json doesn't list itself.
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in rel_parts[:-1]):
            continue
        files[str(path.relative_to(root))] = sha256_of(path)
    return files


def collect_claude_files(root):
    skills_dir = root / ".claude" / "skills"
    files = {}
    if not skills_dir.is_dir():
        return files
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("speckit-"):
            continue
        for path in sorted(skill_dir.rglob("*")):
            if path.is_file():
                files[str(path.relative_to(root))] = sha256_of(path)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["dddkit", "claude"], default="dddkit")
    args = parser.parse_args()

    root = get_project_root()
    manifest_path = root / ".dddkit" / "integrations" / f"{args.target}.manifest.json"

    if args.target == "dddkit":
        files = collect_dddkit_files(root)
    else:
        files = collect_claude_files(root)

    manifest = {
        "integration": args.target,
        "version": "1.0.0",
        "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files": files,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest with {len(files)} file(s) to {manifest_path.relative_to(root)}")


if __name__ == "__main__":
    main()
