//! Concern 1: the spec-code graph resolves end to end.
//!
//! The uuid is the source of truth. `code_glob` is a hint tried first because
//! it is fast, but a module is located by finding its anchor -- the markdown
//! file carrying its `implements_uuid` -- anywhere in the project. A glob that
//! disagrees with where the uuid actually is is the thing that is wrong.

use crate::fixer;
use crate::model::{Anchor, Concern, Finding, Severity, SpecModule};
use crate::project;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexEntry {
    #[serde(default)]
    pub bounded_context: String,
    #[serde(default)]
    pub module: String,
    #[serde(default)]
    pub spec_path: String,
    #[serde(default)]
    pub code_path: Option<String>,
    #[serde(default)]
    pub module_kind: Option<String>,
}

pub struct Options {
    pub no_hint: bool,
    pub fix: bool,
}

/// Where a module actually lives, once resolved.
struct Resolved {
    code_path: PathBuf,
    kind: String,
}

/// How a module's anchor was located.
///
/// The glob hint is a genuine optimization, not decoration: if every module's
/// glob still resolves to a path whose anchor carries the right uuid, the
/// project is healthy and the whole-tree scan is skipped entirely. The moment
/// any module fails its hint, the scan runs and becomes the sole authority --
/// correctness never rests on the hint.
struct Resolution {
    scanned: Option<HashMap<String, Vec<Anchor>>>,
    hints: HashMap<String, Anchor>,
}

impl Resolution {
    fn lookup(&self, uuid: &str) -> &[Anchor] {
        match &self.scanned {
            Some(map) => map.get(uuid).map(Vec::as_slice).unwrap_or(&[]),
            None => match self.hints.get(uuid) {
                Some(a) => std::slice::from_ref(a),
                None => &[],
            },
        }
    }
}

/// Phase 1: does this module's glob still land on its own anchor?
fn try_hint(root: &Path, m: &SpecModule) -> Option<Anchor> {
    let kind = m.module_kind.as_deref()?;
    let glob = m.code_glob.as_deref()?;
    let matches = project::resolve_glob(root, glob);
    if matches.len() != 1 {
        return None;
    }
    let target = &matches[0];
    let anchor_path = match kind {
        "folder" if target.is_dir() => target.join("business-rules.md"),
        "file" if target.is_file() => target.with_extension("md"),
        _ => return None,
    };
    let text = std::fs::read_to_string(&anchor_path).ok()?;
    let fields = crate::frontmatter::parse(&text);
    if crate::frontmatter::resolved(&fields, "implements_uuid")? != m.uuid {
        return None;
    }
    Some(Anchor { rel_path: project::rel(root, &anchor_path), path: anchor_path })
}

fn resolve(root: &Path, modules: &[SpecModule], opts: &Options) -> Resolution {
    let mut hints = HashMap::new();
    let mut needs_scan = opts.no_hint;

    if !opts.no_hint {
        for m in modules {
            if m.uuid.is_empty() || crate::frontmatter::is_placeholder(&m.uuid) {
                continue;
            }
            match try_hint(root, m) {
                Some(a) => {
                    hints.insert(m.uuid.clone(), a);
                }
                // An unplanned module also lands here: we cannot tell whether
                // it has code without looking, so the scan is required.
                None => needs_scan = true,
            }
        }
    }

    Resolution {
        scanned: if needs_scan { Some(project::scan_anchors(root)) } else { None },
        hints,
    }
}

pub fn run(root: &Path, modules: &[SpecModule], opts: &Options, scoped: bool) -> Vec<Finding> {
    let mut findings = Vec::new();
    let mut resolutions: HashMap<String, Resolved> = HashMap::new();
    let resolution = resolve(root, modules, opts);

    for m in modules {
        check_module(root, m, &resolution, opts, &mut findings, &mut resolutions);
    }

    // The index is a cache, not the source of truth, so every disagreement it
    // shows is Fixable by definition -- it is always rebuildable by scanning
    // for uuids. Skipped when scoped to a single module: a partial view of the
    // modules cannot judge whole-index freshness.
    if !scoped {
        check_index(root, modules, &resolutions, opts, &mut findings);
    }

    findings
}

fn check_module(
    root: &Path,
    m: &SpecModule,
    resolution: &Resolution,
    opts: &Options,
    findings: &mut Vec<Finding>,
    resolutions: &mut HashMap<String, Resolved>,
) {
    if m.uuid.is_empty() || crate::frontmatter::is_placeholder(&m.uuid) {
        findings.push(
            Finding::new(
                Concern::Graph,
                Severity::Failure,
                "domain-uuid-missing",
                format!("{}/domain.md has no resolved 'uuid'.", m.rel_spec_dir),
            )
            .path(format!("{}/domain.md", m.rel_spec_dir)),
        );
        return;
    }

    if !m.spec_dir.join("repomap.md").is_file() {
        findings.push(
            Finding::new(
                Concern::Graph,
                Severity::Failure,
                "repomap-missing",
                format!(
                    "{} has domain.md but no repomap.md; the module has no declared shape.",
                    m.rel_spec_dir
                ),
            )
            .module(m)
            .path(m.rel_spec_dir.clone()),
        );
        return;
    }

    let found = resolution.lookup(&m.uuid);
    if found.len() > 1 {
        let paths: Vec<&str> = found.iter().map(|a| a.rel_path.as_str()).collect();
        findings.push(
            Finding::new(
                Concern::Graph,
                Severity::Failure,
                "uuid-duplicated",
                format!(
                    "uuid {} is claimed by {} anchors: {}. A uuid identifies exactly one module.",
                    m.uuid,
                    found.len(),
                    paths.join(", ")
                ),
            )
            .module(m),
        );
        return;
    }
    let anchor = found.first();

    let planned = m.module_kind.is_some() && m.code_glob.is_some();

    match (planned, anchor) {
        // Modelled but not yet planned or implemented. Normal early in the
        // pipeline -- not a failure, or the linter would be unusable until
        // every module is finished.
        (false, None) => findings.push(
            Finding::new(
                Concern::Graph,
                Severity::Pending,
                "module-not-implemented",
                format!(
                    "{} has no finalized repomap.md pointer and no code yet. Run /plan-context, then /implement.",
                    m.reference()
                ),
            )
            .module(m),
        ),

        // Code exists but repomap.md was never finalized. The pointer is
        // derivable from the anchor, so this is drift in derived data.
        (false, Some(a)) => {
            let kind = kind_from_anchor(a);
            let code_path = match code_path_for(a, &kind) {
                Some(p) => p,
                None => {
                    findings.push(shape_failure(m, a, &kind));
                    return;
                }
            };
            let rel_code = project::rel(root, &code_path);
            let mut f = Finding::new(
                Concern::Graph,
                Severity::Fixable,
                "repomap-unfinalized",
                format!(
                    "{} is implemented at {} but repomap.md still has placeholder module_kind/code_glob.",
                    m.reference(),
                    rel_code
                ),
            )
            .module(m)
            .path(rel_code.clone())
            .fix_hint(format!("set module_kind: {kind}, code_glob: {rel_code}"));

            if opts.fix {
                match fixer::set_repomap_pointer(&m.spec_dir, &kind, &rel_code) {
                    Ok(()) => f.fixed = true,
                    Err(e) => f.message = format!("{} (fix failed: {})", f.message, e),
                }
            }
            findings.push(f);
            resolutions.insert(m.uuid.clone(), Resolved { code_path, kind });
        }

        // The plan says code lives somewhere; the uuid is nowhere in the
        // project. This is the real failure: the module is lost.
        (true, None) => findings.push(
            Finding::new(
                Concern::Graph,
                Severity::Failure,
                "module-not-found",
                format!(
                    "{} declares code at '{}' but no anchor carrying uuid {} exists anywhere in the project.",
                    m.reference(),
                    m.code_glob.as_deref().unwrap_or("?"),
                    m.uuid
                ),
            )
            .module(m)
            .fix_hint("write the module's code and its business-rule file, or run /implement"),
        ),

        (true, Some(a)) => {
            let declared_kind = m.module_kind.clone().unwrap_or_default();
            if declared_kind != "folder" && declared_kind != "file" {
                findings.push(
                    Finding::new(
                        Concern::Graph,
                        Severity::Failure,
                        "module-kind-invalid",
                        format!(
                            "{}: repomap.md module_kind must be 'folder' or 'file', got '{}'.",
                            m.reference(),
                            declared_kind
                        ),
                    )
                    .module(m),
                );
                return;
            }

            // Shape: does the anchor match the declared module_kind?
            let actual_kind = kind_from_anchor(a);
            if actual_kind != declared_kind {
                findings.push(shape_failure(m, a, &declared_kind));
                return;
            }
            let code_path = match code_path_for(a, &declared_kind) {
                Some(p) => p,
                None => {
                    findings.push(shape_failure(m, a, &declared_kind));
                    return;
                }
            };
            let rel_code = project::rel(root, &code_path);

            // Phase 1 was only ever a hint; check whether it still agrees.
            // Compare the declared glob against where the uuid actually is.
            // Done identically whether or not the hint was used for lookup, so
            // --no-hint produces the same verdicts, only more slowly.
            let matches = project::resolve_glob(root, m.code_glob.as_deref().unwrap_or(""));
            let hint_agrees = matches.len() == 1 && matches[0] == code_path;

            if !hint_agrees {
                let glob = m.code_glob.as_deref().unwrap_or("");
                let mut f = Finding::new(
                    Concern::Graph,
                    Severity::Fixable,
                    "glob-stale",
                    format!(
                        "{}: code_glob '{}' no longer points at the module. The uuid resolves to {}.",
                        m.reference(),
                        glob,
                        rel_code
                    ),
                )
                .module(m)
                .path(rel_code.clone())
                .fix_hint(format!("set code_glob: {rel_code}"));

                if opts.fix {
                    match fixer::set_repomap_pointer(&m.spec_dir, &declared_kind, &rel_code) {
                        Ok(()) => f.fixed = true,
                        Err(e) => f.message = format!("{} (fix failed: {})", f.message, e),
                    }
                }
                findings.push(f);
            }

            if hint_agrees {
                findings.push(
                    Finding::new(
                        Concern::Graph,
                        Severity::Ok,
                        "module-resolved",
                        format!("{} resolves to {}.", m.reference(), rel_code),
                    )
                    .module(m)
                    .path(rel_code.clone()),
                );
            }

            resolutions.insert(
                m.uuid.clone(),
                Resolved { code_path, kind: declared_kind },
            );
        }
    }
}

/// `business-rules.md` anchors a folder module; any other filename anchors a
/// file module (`catalog.py` is documented by `catalog.md`).
fn kind_from_anchor(a: &Anchor) -> String {
    let name = a.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
    if name == "business-rules.md" {
        "folder".to_string()
    } else {
        "file".to_string()
    }
}

/// The code location a resolved anchor implies.
fn code_path_for(a: &Anchor, kind: &str) -> Option<PathBuf> {
    let parent = a.path.parent()?;
    match kind {
        "folder" => Some(parent.to_path_buf()),
        "file" => {
            // A file module's anchor sits beside the source file it documents.
            let stem = a.path.file_stem()?.to_str()?;
            let mut candidates: Vec<PathBuf> = std::fs::read_dir(parent)
                .ok()?
                .flatten()
                .map(|e| e.path())
                .filter(|p| {
                    p.is_file()
                        && p.file_stem().and_then(|s| s.to_str()) == Some(stem)
                        && p.extension().and_then(|e| e.to_str()) != Some("md")
                })
                .collect();
            candidates.sort();
            candidates.into_iter().next()
        }
        _ => None,
    }
}

fn shape_failure(m: &SpecModule, a: &Anchor, declared: &str) -> Finding {
    let detail = if declared == "file" {
        format!(
            "no source file sits beside {} for a 'file' module (expected a sibling sharing its name)",
            a.rel_path
        )
    } else {
        format!(
            "module_kind is '{}' but the anchor is {} (a 'folder' module is anchored by business-rules.md)",
            declared, a.rel_path
        )
    };
    Finding::new(
        Concern::Graph,
        Severity::Failure,
        "shape-mismatch",
        format!("{}: {}.", m.reference(), detail),
    )
    .module(m)
    .path(a.rel_path.clone())
}

fn check_index(
    root: &Path,
    modules: &[SpecModule],
    resolutions: &HashMap<String, Resolved>,
    opts: &Options,
    findings: &mut Vec<Finding>,
) {
    let index_path = root.join(".dddkit").join("index.json");
    let mut stale = false;

    let index: HashMap<String, IndexEntry> = if index_path.is_file() {
        match std::fs::read_to_string(&index_path)
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
        {
            Some(i) => i,
            None => {
                stale = true;
                findings.push(Finding::new(
                    Concern::Graph,
                    Severity::Fixable,
                    "index-unreadable",
                    ".dddkit/index.json could not be parsed. It is a cache and is always rebuildable.",
                ));
                HashMap::new()
            }
        }
    } else {
        stale = true;
        findings.push(Finding::new(
            Concern::Graph,
            Severity::Fixable,
            "index-missing",
            ".dddkit/index.json does not exist. It is a cache and is always rebuildable.",
        ));
        HashMap::new()
    };

    for m in modules {
        if m.uuid.is_empty() || crate::frontmatter::is_placeholder(&m.uuid) {
            continue;
        }
        match index.get(&m.uuid) {
            None => {
                stale = true;
                findings.push(
                    Finding::new(
                        Concern::Graph,
                        Severity::Fixable,
                        "index-missing-entry",
                        format!("{} (uuid {}) is not in index.json.", m.rel_spec_dir, m.uuid),
                    )
                    .module(m),
                );
            }
            Some(entry) => {
                if entry.spec_path != m.rel_spec_dir {
                    stale = true;
                    findings.push(
                        Finding::new(
                            Concern::Graph,
                            Severity::Fixable,
                            "index-stale-spec-path",
                            format!(
                                "index.json records spec_path '{}' for uuid {}, but it is at '{}'.",
                                entry.spec_path, m.uuid, m.rel_spec_dir
                            ),
                        )
                        .module(m),
                    );
                }
                let resolved_code = resolutions.get(&m.uuid).map(|r| project::rel(root, &r.code_path));
                if entry.code_path != resolved_code {
                    stale = true;
                    findings.push(
                        Finding::new(
                            Concern::Graph,
                            Severity::Fixable,
                            "index-stale-code-path",
                            format!(
                                "index.json records code_path {:?} for uuid {}, but the uuid resolves to {:?}.",
                                entry.code_path, m.uuid, resolved_code
                            ),
                        )
                        .module(m),
                    );
                }
            }
        }
    }

    let known: std::collections::HashSet<&str> = modules.iter().map(|m| m.uuid.as_str()).collect();
    for uuid in index.keys() {
        if !known.contains(uuid.as_str()) {
            stale = true;
            findings.push(Finding::new(
                Concern::Graph,
                Severity::Fixable,
                "index-orphan",
                format!("index.json has an entry for uuid {uuid} with no matching domain.md."),
            ));
        }
    }

    if stale && opts.fix {
        let entries: Vec<(String, IndexEntry)> = modules
            .iter()
            .filter(|m| !m.uuid.is_empty() && !crate::frontmatter::is_placeholder(&m.uuid))
            .map(|m| {
                let r = resolutions.get(&m.uuid);
                (
                    m.uuid.clone(),
                    IndexEntry {
                        bounded_context: m.bounded_context.clone(),
                        module: m.module.clone(),
                        spec_path: m.rel_spec_dir.clone(),
                        code_path: r.map(|r| project::rel(root, &r.code_path)),
                        module_kind: r.map(|r| r.kind.clone()),
                    },
                )
            })
            .collect();
        match fixer::write_index(&index_path, entries) {
            Ok(()) => {
                for f in findings.iter_mut() {
                    if f.code.starts_with("index-") {
                        f.fixed = true;
                    }
                }
            }
            Err(e) => findings.push(Finding::new(
                Concern::Graph,
                Severity::Failure,
                "index-write-failed",
                format!("could not rebuild .dddkit/index.json: {e}"),
            )),
        }
    }
}
