//! Concern 2: the declared architecture matches the filesystem, both directions.
//!
//! Every Bounded Context named in contexts.md must have a folder, and every
//! folder must be named in contexts.md. Neither direction may have orphans.
//!
//! Nothing here is auto-fixable: reconciling this is /map-contexts' job, and
//! it sits behind an explicit human approval gate (DDD.md section 4).

use crate::model::{Concern, Finding, Severity};
use regex::Regex;
use std::collections::BTreeSet;
use std::path::Path;

pub fn run(root: &Path) -> Vec<Finding> {
    let mut findings = Vec::new();
    let bc_dir = root.join("specs").join("BoundedContexts");
    let map_file = bc_dir.join("contexts.md");

    if !map_file.is_file() {
        findings.push(Finding::new(
            Concern::Match,
            Severity::Failure,
            "context-map-missing",
            "specs/BoundedContexts/contexts.md not found.",
        ));
        return findings;
    }

    let text = std::fs::read_to_string(&map_file).unwrap_or_default();
    // Convention-based scan, matching the Python implementation: a context
    // name is any backtick-wrapped PascalCase token anywhere in the file.
    let name_re = Regex::new(r"`([A-Z][A-Za-z0-9]*)`").unwrap();
    let mapped: BTreeSet<String> = name_re
        .captures_iter(&text)
        .map(|c| c[1].to_string())
        .collect();

    if mapped.is_empty() {
        findings.push(Finding::new(
            Concern::Match,
            Severity::Failure,
            "context-map-empty",
            "no backtick-wrapped PascalCase Bounded Context names found in contexts.md.",
        ));
    }

    let pascal = Regex::new(r"^[A-Z][A-Za-z0-9]*$").unwrap();
    let mut actual: BTreeSet<String> = BTreeSet::new();
    if let Ok(entries) = std::fs::read_dir(&bc_dir) {
        for entry in entries.flatten() {
            if entry.path().is_dir() {
                let name = entry.file_name().to_string_lossy().to_string();
                if pascal.is_match(&name) {
                    actual.insert(name);
                }
            }
        }
    }

    for name in mapped.difference(&actual) {
        findings.push(
            Finding::new(
                Concern::Match,
                Severity::Failure,
                "context-folder-missing",
                format!("'{name}' is named in contexts.md but has no folder at specs/BoundedContexts/{name}/."),
            )
            .fix_hint("run /map-contexts to reconcile (additive, human-approved)"),
        );
    }
    for name in actual.difference(&mapped) {
        findings.push(
            Finding::new(
                Concern::Match,
                Severity::Failure,
                "context-unmapped",
                format!("specs/BoundedContexts/{name}/ exists but '{name}' is not named in contexts.md."),
            )
            .fix_hint("run /map-contexts to reconcile (additive, human-approved)"),
        );
    }

    if findings.is_empty() {
        findings.push(Finding::new(
            Concern::Match,
            Severity::Ok,
            "context-map-consistent",
            format!("{} Bounded Context(s) match between contexts.md and the filesystem.", actual.len()),
        ));
    }
    findings
}
