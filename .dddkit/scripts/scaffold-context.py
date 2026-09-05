#!/usr/bin/env python3
"""Scaffold a new DDD-Kit Bounded Context module (domain.md, vocabulary.md, repomap.md)."""

import argparse
import os
import re
import sys
import uuid

from _common import get_project_root


def render_template(content, replacements):
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content


def main():
    parser = argparse.ArgumentParser(description="Scaffold a DDD-Kit Bounded Context module")
    parser.add_argument("--context", required=True, help="Bounded Context name (PascalCase)")
    parser.add_argument("--module", required=True, help="Module name (kebab-case)")
    parser.add_argument("--logical-folder", default=None, help="Optional [logical-folder] to nest the module under (2+ levels only)")

    args = parser.parse_args()

    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", args.context):
        print(f"Error: --context '{args.context}' must be PascalCase (e.g. LabExperiments).")
        sys.exit(1)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.module):
        print(f"Error: --module '{args.module}' must be kebab-case (e.g. catalog-service).")
        sys.exit(1)

    root = get_project_root()
    kit_dir = root / ".dddkit"
    templates_dir = kit_dir / "templates"
    bounded_contexts_dir = root / "specs" / "BoundedContexts"

    context_dir = bounded_contexts_dir / args.context
    if args.logical_folder:
        context_dir = context_dir / f"[{args.logical_folder}]"
    module_dir = context_dir / args.module

    if module_dir.exists():
        print(f"Error: module '{args.module}' already exists under '{args.context}'.")
        sys.exit(1)

    os.makedirs(module_dir, exist_ok=True)

    module_uuid = str(uuid.uuid4())

    domain_tpl = templates_dir / "domain-template.md"
    vocab_tpl = templates_dir / "vocabulary-template.md"
    repomap_tpl = templates_dir / "repomap-template.md"

    target_domain = module_dir / "domain.md"
    target_vocab = module_dir / "vocabulary.md"
    target_repomap = module_dir / "repomap.md"

    try:
        domain_content = domain_tpl.read_text(encoding="utf-8")
        vocab_content = vocab_tpl.read_text(encoding="utf-8")
        repomap_content = repomap_tpl.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"Error: template file not found. Make sure {templates_dir} has domain-template.md, vocabulary-template.md, and repomap-template.md.")
        print(e)
        sys.exit(1)

    domain_content = render_template(domain_content, {
        "[GENERATED_UUID]": module_uuid,
        "[PASCAL_CASE_CONTEXT_NAME]": args.context,
        "[kebab-case-module-name]": args.module,
        "[MODULE_NAME]": args.module,
    })
    vocab_content = render_template(vocab_content, {
        "[SAME_UUID_AS_DOMAIN_MD]": module_uuid,
        "[MODULE_NAME]": args.module,
    })
    repomap_content = render_template(repomap_content, {
        "[SAME_UUID_AS_DOMAIN_MD]": module_uuid,
        "[MODULE_NAME]": args.module,
    })

    target_domain.write_text(domain_content, encoding="utf-8")
    target_vocab.write_text(vocab_content, encoding="utf-8")
    target_repomap.write_text(repomap_content, encoding="utf-8")

    print(f"Created module '{args.module}' under '{args.context}' at {module_dir.relative_to(root)}")
    print(f"  uuid: {module_uuid}")
    print(f"Now edit {target_domain.relative_to(root)}, {target_vocab.relative_to(root)}, and {target_repomap.relative_to(root)}")
    print("Run .dddkit/scripts/build-index.py afterwards to register this module in .dddkit/index.json")


if __name__ == "__main__":
    main()
