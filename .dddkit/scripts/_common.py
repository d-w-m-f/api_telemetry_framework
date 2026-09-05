"""Shared helpers for DDD-Kit's own scripts (scaffold, build-index, validate, manifest).

Not a public API - just factored out so the same project-root resolution and
frontmatter parsing logic isn't duplicated (and drifted) across scripts.
"""

from pathlib import Path


def get_project_root():
    """Every script here lives at .dddkit/scripts/<name>.py -> repo root is 3 parents up."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent.parent


def parse_frontmatter(filepath):
    """Parse a simple `key: value` YAML frontmatter block into a dict of strings.

    Deliberately not a full YAML parser (no external dependency): DDD-Kit
    frontmatter is flat key: value pairs, one per line, optionally quoted.
    """
    text = Path(filepath).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]

    fields = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
    return fields


def find_module_dirs(specs_dir):
    """Yield each module directory under specs/BoundedContexts that has a domain.md."""
    for domain_file in sorted(specs_dir.glob("BoundedContexts/**/domain.md")):
        yield domain_file.parent
