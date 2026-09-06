//! Locating things: the project root, the spec-side modules, and the
//! code-side anchors.
//!
//! Root discovery differs from the Python scripts by necessity. They resolve
//! the root `__file__`-relative (three parents up from
//! `.dddkit/scripts/<name>.py`), which is why they work from any cwd. An
//! installed binary has no such anchor, so it walks up from the current
//! directory looking for `.dddkit/`.

use crate::frontmatter;
use crate::model::{Anchor, SpecModule};
use ignore::WalkBuilder;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

pub fn find_root() -> Result<PathBuf, String> {
    let mut dir = std::env::current_dir().map_err(|e| format!("cannot read current directory: {e}"))?;
    loop {
        if dir.join(".dddkit").is_dir() {
            return Ok(dir);
        }
        if !dir.pop() {
            return Err(
                "not inside a dddkit project: no .dddkit/ directory in this directory or any parent"
                    .to_string(),
            );
        }
    }
}

pub fn rel(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
}

/// Every module declared on the spec side: a directory under
/// `specs/BoundedContexts/` containing a `domain.md`.
///
/// Walked with gitignore filtering disabled: specs are the framework's own
/// tree and are read regardless of how the project's .gitignore is set up.
pub fn spec_modules(root: &Path) -> Vec<SpecModule> {
    let bc_dir = root.join("specs").join("BoundedContexts");
    let mut modules = Vec::new();
    if !bc_dir.is_dir() {
        return modules;
    }

    for entry in WalkBuilder::new(&bc_dir).standard_filters(false).build().flatten() {
        if entry.file_name() != "domain.md" || !entry.path().is_file() {
            continue;
        }
        let domain_path = entry.path();
        let spec_dir = match domain_path.parent() {
            Some(p) => p.to_path_buf(),
            None => continue,
        };
        let text = std::fs::read_to_string(domain_path).unwrap_or_default();
        let fields = frontmatter::parse(&text);

        let uuid = fields.get("uuid").cloned().unwrap_or_default();
        let bounded_context = fields.get("bounded_context").cloned().unwrap_or_default();
        let module = fields.get("module").cloned().unwrap_or_default();

        // repomap.md is the only file allowed to carry a code pointer.
        let repomap_path = spec_dir.join("repomap.md");
        let (module_kind, code_glob) = if repomap_path.is_file() {
            let rtext = std::fs::read_to_string(&repomap_path).unwrap_or_default();
            let rfields = frontmatter::parse(&rtext);
            (
                frontmatter::resolved(&rfields, "module_kind").map(str::to_string),
                frontmatter::resolved(&rfields, "code_glob").map(str::to_string),
            )
        } else {
            (None, None)
        };

        modules.push(SpecModule {
            uuid,
            bounded_context,
            module,
            rel_spec_dir: rel(root, &spec_dir),
            spec_dir,
            module_kind,
            code_glob,
        });
    }

    modules.sort_by(|a, b| a.rel_spec_dir.cmp(&b.rel_spec_dir));
    modules
}

/// Scan the code side of the project for Module Anchors: markdown files
/// carrying an `implements_uuid`.
///
/// `specs/` MUST be excluded. vocabulary.md, repomap.md, plan.md, tasks.md and
/// roadmap.md all carry `implements_uuid`; including specs/ would match five
/// spec files per module and make every module look duplicated.
pub fn scan_anchors(root: &Path) -> HashMap<String, Vec<Anchor>> {
    let mut anchors: HashMap<String, Vec<Anchor>> = HashMap::new();

    let walker = WalkBuilder::new(root)
        .hidden(false)
        .git_ignore(true)
        .git_global(false)
        .filter_entry(|entry| {
            let name = entry.file_name().to_string_lossy();
            // Never descend into the spec side, the framework's own directory,
            // or version control internals.
            !matches!(name.as_ref(), "specs" | ".dddkit" | ".git")
        })
        .build();

    for entry in walker.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("md") || !path.is_file() {
            continue;
        }
        let text = match std::fs::read_to_string(path) {
            Ok(t) => t,
            Err(_) => continue,
        };
        let fields = frontmatter::parse(&text);
        if let Some(uuid) = frontmatter::resolved(&fields, "implements_uuid") {
            anchors.entry(uuid.to_string()).or_default().push(Anchor {
                rel_path: rel(root, path),
                path: path.to_path_buf(),
            });
        }
    }

    for list in anchors.values_mut() {
        list.sort_by(|a, b| a.rel_path.cmp(&b.rel_path));
    }
    anchors
}

/// Resolve a `code_glob` hint against the project root.
///
/// This is Phase 1 only — a fast guess. Correctness never depends on it, so a
/// semantics difference between Python's `pathlib.glob` and Rust's `glob`
/// crate degrades to a slower Phase 2 rather than a wrong verdict. The
/// trailing slash Python 3.13+ uses to mean "directories only" is simply
/// trimmed here.
pub fn resolve_glob(root: &Path, pattern: &str) -> Vec<PathBuf> {
    let trimmed = pattern.trim_end_matches('/');
    let full = root.join(trimmed);
    match glob::glob(&full.to_string_lossy()) {
        Ok(paths) => paths.flatten().filter(|p| p.exists()).collect(),
        Err(_) => Vec::new(),
    }
}
