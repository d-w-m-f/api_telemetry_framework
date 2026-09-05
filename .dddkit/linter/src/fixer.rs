//! Repairs, applied only under `--fix`.
//!
//! Everything here rewrites *derived* data that is reconstructible from the
//! source of truth. Authored content (code, business-rule files), and
//! approval-gated structure (contexts.md, the context folders) are never
//! touched -- a generated stub would satisfy a check while defeating its
//! purpose. Manifests are deliberately excluded too; see checks/integrity.rs.

use crate::checks::graph::IndexEntry;
use std::collections::BTreeMap;
use std::path::Path;

/// Rewrite a module's `module_kind` / `code_glob` in repomap.md's frontmatter.
///
/// Only lines inside the frontmatter block are considered, so a `code_glob:`
/// mentioned in the document body is never rewritten by accident.
pub fn set_repomap_pointer(spec_dir: &Path, kind: &str, code_path: &str) -> Result<(), String> {
    let path = spec_dir.join("repomap.md");
    let text = std::fs::read_to_string(&path).map_err(|e| format!("read {}: {e}", path.display()))?;

    if !text.starts_with("---") {
        return Err("repomap.md has no frontmatter block".to_string());
    }
    let end = text[3..]
        .find("\n---")
        .map(|i| 3 + i)
        .ok_or("repomap.md frontmatter block is not terminated")?;

    let (block, rest) = text.split_at(end);
    let mut out = String::with_capacity(text.len() + 32);
    let mut saw_kind = false;
    let mut saw_glob = false;

    for (i, line) in block.lines().enumerate() {
        if i > 0 {
            out.push('\n');
        }
        let trimmed = line.trim_start();
        if trimmed.starts_with("module_kind:") {
            out.push_str(&format!("module_kind: {kind}"));
            saw_kind = true;
        } else if trimmed.starts_with("code_glob:") {
            out.push_str(&format!("code_glob: \"{code_path}\""));
            saw_glob = true;
        } else {
            out.push_str(line);
        }
    }
    if !saw_kind {
        out.push_str(&format!("\nmodule_kind: {kind}"));
    }
    if !saw_glob {
        out.push_str(&format!("\ncode_glob: \"{code_path}\""));
    }
    out.push_str(rest);

    std::fs::write(&path, out).map_err(|e| format!("write {}: {e}", path.display()))
}

/// Rewrite `.dddkit/index.json`, matching build-index.py's output byte for
/// byte: 2-space indent, keys sorted, trailing newline.
pub fn write_index(path: &Path, entries: Vec<(String, IndexEntry)>) -> Result<(), String> {
    let map: BTreeMap<String, IndexEntry> = entries.into_iter().collect();
    let mut json = serde_json::to_string_pretty(&map).map_err(|e| e.to_string())?;
    json.push('\n');
    std::fs::write(path, json).map_err(|e| format!("write {}: {e}", path.display()))
}
