//! Concern 3: dddkit's own files still match their recorded sha256 hashes.
//!
//! Unlike the other two concerns this protects the *framework*, not the user's
//! domain. A hash mismatch is deliberately NOT auto-fixable: regenerating a
//! manifest to silence it defeats the entire tamper check. Confirm the change
//! was intentional, then run generate-manifest.py explicitly.

use crate::model::{Concern, Finding, Severity};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::path::Path;

#[derive(Deserialize)]
struct Manifest {
    #[serde(default)]
    files: BTreeMap<String, String>,
}

pub fn run(root: &Path) -> Vec<Finding> {
    let mut findings = Vec::new();
    for name in ["dddkit.manifest.json", "claude.manifest.json"] {
        check_one(root, name, &mut findings);
    }
    findings
}

fn check_one(root: &Path, name: &str, findings: &mut Vec<Finding>) {
    let path = root.join(".dddkit").join("integrations").join(name);
    let target = name.split('.').next().unwrap_or("dddkit");

    let text = match std::fs::read_to_string(&path) {
        Ok(t) => t,
        Err(_) => {
            findings.push(
                Finding::new(
                    Concern::Integrity,
                    Severity::Failure,
                    "manifest-missing",
                    format!(".dddkit/integrations/{name} not found."),
                )
                .fix_hint(format!("python3 .dddkit/scripts/generate-manifest.py --target {target}")),
            );
            return;
        }
    };

    let manifest: Manifest = match serde_json::from_str(&text) {
        Ok(m) => m,
        Err(e) => {
            findings.push(Finding::new(
                Concern::Integrity,
                Severity::Failure,
                "manifest-unreadable",
                format!("could not parse .dddkit/integrations/{name}: {e}"),
            ));
            return;
        }
    };

    if manifest.files.is_empty() {
        findings.push(Finding::new(
            Concern::Integrity,
            Severity::Pending,
            "manifest-empty",
            format!("{name} lists no files."),
        ));
        return;
    }

    let mut bad = 0usize;
    for (rel_path, expected) in &manifest.files {
        let file = root.join(rel_path);
        let bytes = match std::fs::read(&file) {
            Ok(b) => b,
            Err(_) => {
                bad += 1;
                findings.push(
                    Finding::new(
                        Concern::Integrity,
                        Severity::Failure,
                        "manifest-file-missing",
                        format!("{name} lists '{rel_path}' but it no longer exists."),
                    )
                    .path(rel_path.clone()),
                );
                continue;
            }
        };
        let actual = format!("{:x}", Sha256::digest(&bytes));
        if &actual != expected {
            bad += 1;
            findings.push(
                Finding::new(
                    Concern::Integrity,
                    Severity::Failure,
                    "manifest-hash-mismatch",
                    format!("'{rel_path}' does not match the hash recorded in {name}."),
                )
                .path(rel_path.clone())
                .fix_hint(format!(
                    "if the change was intentional: python3 .dddkit/scripts/generate-manifest.py --target {target}"
                )),
            );
        }
    }

    if bad == 0 {
        findings.push(Finding::new(
            Concern::Integrity,
            Severity::Ok,
            "manifest-intact",
            format!("{}: {} file(s) match.", name, manifest.files.len()),
        ));
    }
}
