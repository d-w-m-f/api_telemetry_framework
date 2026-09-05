#!/usr/bin/env python3
"""DDD-Kit SdSFC + structure linter.

Checks (see DDD.md section 3-4 and workflow.md's linter memorandum):
  1. .dddkit/index.json is not stale relative to the real domain.md/repomap.md files.
  2. Every module's business-rule file exists at the location repomap.md points at,
     and module_kind matches what is actually on disk.
  3. Every context-map.md entry has a matching folder under BoundedContexts/, and
     every such folder is named in context-map.md (no orphans either direction).
  4. Every file listed in .dddkit/integrations/dddkit.manifest.json still matches
     its recorded sha256 hash.
  5. Same as (4), for .dddkit/integrations/claude.manifest.json (the dddkit-owned
     skill files under .claude/skills/).
"""

import hashlib
import json
import re
import sys

from _common import get_project_root, parse_frontmatter, find_module_dirs

CONTEXT_NAME_RE = re.compile(r"`([A-Z][A-Za-z0-9]*)`")


def sha256_of(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def check_index_freshness(root, specs_dir):
    print("\n=== 1. Index freshness (.dddkit/index.json) ===")
    index_path = root / ".dddkit" / "index.json"
    errors = 0

    if not index_path.is_file():
        print("ERROR: .dddkit/index.json does not exist. Run .dddkit/scripts/build-index.py.")
        return 1

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not parse .dddkit/index.json: {exc}")
        return 1

    seen_uuids = set()
    for module_dir in find_module_dirs(specs_dir):
        rel_module_dir = str(module_dir.relative_to(root))
        domain_fields = parse_frontmatter(module_dir / "domain.md")
        module_uuid = domain_fields.get("uuid")

        if not module_uuid or module_uuid.startswith("["):
            print(f"ERROR: {rel_module_dir}/domain.md has no resolved 'uuid'.")
            errors += 1
            continue

        seen_uuids.add(module_uuid)
        entry = index.get(module_uuid)
        if entry is None:
            print(f"ERROR: {rel_module_dir} (uuid {module_uuid}) is missing from index.json. Rebuild the index.")
            errors += 1
        elif entry.get("spec_path") != rel_module_dir:
            print(f"ERROR: index.json has stale spec_path for uuid {module_uuid}: "
                  f"indexed '{entry.get('spec_path')}', actual '{rel_module_dir}'. Rebuild the index.")
            errors += 1
        else:
            print(f"OK: {rel_module_dir} indexed correctly.")

    for indexed_uuid in index:
        if indexed_uuid not in seen_uuids:
            print(f"ERROR: index.json has an orphaned entry for uuid {indexed_uuid} "
                  f"(spec_path '{index[indexed_uuid].get('spec_path')}') with no matching domain.md. Rebuild the index.")
            errors += 1

    return errors


def check_sdsfc(root, specs_dir):
    print("\n=== 2. SdSFC (business-rule file next to the code) ===")
    module_dirs = list(find_module_dirs(specs_dir))
    if not module_dirs:
        print("No domain.md files found under specs/BoundedContexts/. Nothing to check.")
        return 0

    errors = 0
    for module_dir in module_dirs:
        rel_module_dir = module_dir.relative_to(root)
        repomap_file = module_dir / "repomap.md"
        print(f"Checking: {rel_module_dir}")

        if not repomap_file.is_file():
            print(f"   ERROR: missing repomap.md (required to locate the code for this module).")
            errors += 1
            continue

        fields = parse_frontmatter(repomap_file)
        code_glob = fields.get("code_glob")
        module_kind = fields.get("module_kind")

        if not code_glob or code_glob.startswith("["):
            print(f"   ERROR: repomap.md has no resolved 'code_glob'.")
            errors += 1
            continue
        if module_kind not in ("folder", "file"):
            print(f"   ERROR: repomap.md 'module_kind' must be 'folder' or 'file', got '{module_kind}'.")
            errors += 1
            continue

        matches = [p for p in root.glob(code_glob) if p.exists()]
        if not matches:
            print(f"   ERROR: code_glob '{code_glob}' matched nothing in the source tree.")
            errors += 1
            continue
        if len(matches) > 1:
            print(f"   ERROR: code_glob '{code_glob}' matched {len(matches)} paths; it must resolve to exactly one.")
            errors += 1
            continue

        code_path = matches[0]
        actual_kind = "folder" if code_path.is_dir() else "file"
        if actual_kind != module_kind:
            print(f"   ERROR: repomap.md says module_kind '{module_kind}' but '{code_path}' is a {actual_kind}.")
            errors += 1
            continue

        if module_kind == "folder":
            rule_file = code_path / "business-rules.md"
        else:
            rule_file = code_path.with_suffix(".md")

        if rule_file.exists():
            print(f"   OK: {rule_file.relative_to(root)} found.")
        else:
            print(f"   ERROR: expected business-rule file not found at {rule_file.relative_to(root)}.")
            errors += 1

    return errors


def check_context_map(root, specs_dir):
    print("\n=== 3. context-map.md <-> BoundedContexts/ folders ===")
    context_map_file = specs_dir / "BoundedContexts" / "contexts.md"
    bounded_contexts_dir = specs_dir / "BoundedContexts"
    errors = 0

    if not context_map_file.is_file():
        print(f"ERROR: {context_map_file.relative_to(root)} not found.")
        return 1

    mapped_names = set(CONTEXT_NAME_RE.findall(context_map_file.read_text(encoding="utf-8")))
    if not mapped_names:
        print(f"ERROR: no backtick-wrapped PascalCase Bounded Context names found in {context_map_file.relative_to(root)}.")
        errors += 1

    actual_names = {
        p.name for p in bounded_contexts_dir.iterdir()
        if p.is_dir() and re.fullmatch(r"[A-Z][A-Za-z0-9]*", p.name)
    }

    for name in sorted(mapped_names - actual_names):
        print(f"ERROR: '{name}' is named in contexts.md but has no folder at specs/BoundedContexts/{name}/.")
        errors += 1
    for name in sorted(actual_names - mapped_names):
        print(f"ERROR: specs/BoundedContexts/{name}/ exists but '{name}' is not named in contexts.md.")
        errors += 1

    if not errors:
        print(f"OK: {len(actual_names)} Bounded Context(s) match between contexts.md and the filesystem.")

    return errors


def check_manifest(root, manifest_name, section_label):
    print(f"\n=== {section_label} ===")
    manifest_path = root / ".dddkit" / "integrations" / manifest_name
    errors = 0

    if not manifest_path.is_file():
        print(f"ERROR: {manifest_path.relative_to(root)} not found. Run .dddkit/scripts/generate-manifest.py --target {manifest_name.split('.')[0]}.")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not parse {manifest_path.relative_to(root)}: {exc}")
        return 1

    files = manifest.get("files", {})
    if not files:
        print("WARNING: manifest has no files listed.")

    for rel_path, expected_hash in files.items():
        path = root / rel_path
        if not path.is_file():
            print(f"ERROR: manifest lists '{rel_path}' but it no longer exists.")
            errors += 1
            continue
        actual_hash = sha256_of(path)
        if actual_hash != expected_hash:
            print(f"ERROR: '{rel_path}' hash mismatch (manifest is stale or the file was modified without regenerating it).")
            errors += 1
        else:
            print(f"OK: {rel_path}")

    return errors


def main():
    print("=== DDD-Kit Linter ===")
    root = get_project_root()
    specs_dir = root / "specs"

    total_errors = 0
    total_errors += check_index_freshness(root, specs_dir)
    total_errors += check_sdsfc(root, specs_dir)
    total_errors += check_context_map(root, specs_dir)
    total_errors += check_manifest(root, "dddkit.manifest.json", "4. dddkit.manifest.json integrity")
    total_errors += check_manifest(root, "claude.manifest.json", "5. claude.manifest.json integrity")

    if total_errors:
        print(f"\nValidation FAILED with {total_errors} error(s).")
        sys.exit(1)
    else:
        print("\nValidation PASSED. Specs are in sync with the codebase.")
        sys.exit(0)


if __name__ == "__main__":
    main()
