#!/usr/bin/env python3
"""Rebuild .dddkit/index.json: uuid -> {bounded_context, module, spec_path, code_path} for every module."""

import json
import sys

from _common import get_project_root, parse_frontmatter, find_module_dirs


def main():
    root = get_project_root()
    specs_dir = root / "specs"
    index_path = root / ".dddkit" / "index.json"

    index = {}
    errors = 0

    for module_dir in find_module_dirs(specs_dir):
        domain_file = module_dir / "domain.md"
        repomap_file = module_dir / "repomap.md"
        rel_module_dir = module_dir.relative_to(root)

        domain_fields = parse_frontmatter(domain_file)
        module_uuid = domain_fields.get("uuid")

        if not module_uuid or module_uuid.startswith("["):
            print(f"ERROR: {rel_module_dir}/domain.md has no resolved 'uuid' in its frontmatter.")
            errors += 1
            continue

        if module_uuid in index:
            print(f"ERROR: duplicate uuid '{module_uuid}' in {rel_module_dir}/domain.md (already used by {index[module_uuid]['spec_path']}).")
            errors += 1
            continue

        code_glob = None
        module_kind = None
        if repomap_file.is_file():
            repomap_fields = parse_frontmatter(repomap_file)
            code_glob = repomap_fields.get("code_glob")
            module_kind = repomap_fields.get("module_kind")
            if code_glob and code_glob.startswith("["):
                code_glob = None
            if module_kind and module_kind.startswith("["):
                module_kind = None
        else:
            print(f"WARNING: {rel_module_dir} has domain.md but no repomap.md; code_path left unresolved.")

        code_path = None
        if code_glob:
            matches = [p for p in root.glob(code_glob) if p.exists()]
            if len(matches) == 1:
                code_path = str(matches[0].relative_to(root))
            elif len(matches) == 0:
                print(f"WARNING: {rel_module_dir}/repomap.md code_glob '{code_glob}' matched nothing.")
            else:
                print(f"WARNING: {rel_module_dir}/repomap.md code_glob '{code_glob}' matched {len(matches)} paths; leaving code_path unresolved.")

        index[module_uuid] = {
            "bounded_context": domain_fields.get("bounded_context", ""),
            "module": domain_fields.get("module", ""),
            "spec_path": str(rel_module_dir),
            "code_path": code_path,
            "module_kind": module_kind,
        }

    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(index)} module(s) to {index_path.relative_to(root)}")

    if errors:
        print(f"\n{errors} error(s) encountered while building the index.")
        sys.exit(1)


if __name__ == "__main__":
    main()
