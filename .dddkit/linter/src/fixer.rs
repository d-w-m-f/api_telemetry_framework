//! Repairs, applied only under `--fix`.
//!
//! Everything here rewrites *derived* data that is reconstructible from the
//! source of truth. Authored content and approval-gated structure
//! (contexts.md, the context folders) are never touched -- a generated stub
//! would satisfy a check while defeating its purpose. Manifests are
//! deliberately excluded too; see checks/integrity.rs.
//!
//! A business-rule file sits on both sides of that line: its body is authored
//! and never touched here, while its identity frontmatter (bounded_context,
//! module, module_kind) is a copy of the spec side and therefore derived. Only
//! the frontmatter block is ever rewritten.

use crate::checks::graph::IndexEntry;
use std::collections::BTreeMap;
use std::path::Path;

/// Rewrite a module's `module_kind` / `code_glob` in repomap.md's frontmatter.
pub fn set_repomap_pointer(spec_dir: &Path, kind: &str, code_path: &str) -> Result<(), String> {
    set_frontmatter(
        &spec_dir.join("repomap.md"),
        &[
            ("module_kind", kind.to_string()),
            ("code_glob", format!("\"{code_path}\"")),
        ],
    )
}

/// Rewrite the identity fields a Module Anchor restates from the spec side.
///
/// The anchor's body -- the business rules a human wrote -- is never touched:
/// `set_frontmatter` only ever edits inside the frontmatter block.
pub fn set_anchor_identity(
    anchor_path: &Path,
    bounded_context: &str,
    module: &str,
    kind: &str,
) -> Result<(), String> {
    set_frontmatter(
        anchor_path,
        &[
            ("bounded_context", bounded_context.to_string()),
            ("module", module.to_string()),
            ("module_kind", kind.to_string()),
        ],
    )
}

/// Set `key: value` for each pair, inside the frontmatter block only.
///
/// A key already present is rewritten in place, preserving field order; a key
/// that is absent is appended to the end of the block. Restricting the rewrite
/// to the block is what makes this safe on files with authored bodies: a
/// `module:` written in a prose paragraph is never mistaken for a field.
fn set_frontmatter(path: &Path, pairs: &[(&str, String)]) -> Result<(), String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("read {}: {e}", path.display()))?;

    if !text.starts_with("---") {
        return Err(format!("{} has no frontmatter block", path.display()));
    }
    let end = text[3..]
        .find("\n---")
        .map(|i| 3 + i)
        .ok_or_else(|| format!("{}'s frontmatter block is not terminated", path.display()))?;

    let (block, rest) = text.split_at(end);
    let mut out = String::with_capacity(text.len() + 64);
    let mut seen = vec![false; pairs.len()];

    for (i, line) in block.lines().enumerate() {
        if i > 0 {
            out.push('\n');
        }
        let trimmed = line.trim_start();
        match pairs
            .iter()
            .position(|(k, _)| trimmed.starts_with(&format!("{k}:")))
        {
            Some(idx) => {
                out.push_str(&format!("{}: {}", pairs[idx].0, pairs[idx].1));
                seen[idx] = true;
            }
            None => out.push_str(line),
        }
    }
    for (idx, (key, value)) in pairs.iter().enumerate() {
        if !seen[idx] {
            out.push_str(&format!("\n{key}: {value}"));
        }
    }
    out.push_str(rest);

    std::fs::write(path, out).map_err(|e| format!("write {}: {e}", path.display()))
}

/// Rewrite `.dddkit/index.json`, matching build-index.py's output byte for
/// byte: 2-space indent, keys sorted, trailing newline.
pub fn write_index(path: &Path, entries: Vec<(String, IndexEntry)>) -> Result<(), String> {
    let map: BTreeMap<String, IndexEntry> = entries.into_iter().collect();
    let mut json = serde_json::to_string_pretty(&map).map_err(|e| e.to_string())?;
    json.push('\n');
    std::fs::write(path, json).map_err(|e| format!("write {}: {e}", path.display()))
}
