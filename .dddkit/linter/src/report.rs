//! Output. Text for humans, JSON for skills, hooks and CI.
//!
//! The JSON shape is the contract `/implement` gates on, so `code` values are
//! stable identifiers rather than prose.

use crate::model::{Concern, Finding, Severity};
use serde::Serialize;

#[derive(Serialize)]
pub struct Summary {
    pub failure: usize,
    pub fixable: usize,
    pub pending: usize,
    pub ok: usize,
    pub fixed: usize,
}

#[derive(Serialize)]
pub struct Report<'a> {
    pub schema: u32,
    pub root: String,
    pub summary: Summary,
    pub passed: bool,
    pub findings: &'a [Finding],
}

pub fn summarize(findings: &[Finding]) -> Summary {
    let mut s = Summary { failure: 0, fixable: 0, pending: 0, ok: 0, fixed: 0 };
    for f in findings {
        if f.fixed {
            s.fixed += 1;
        }
        match f.severity {
            Severity::Failure => s.failure += 1,
            // A fixable finding that was actually repaired is no longer outstanding.
            Severity::Fixable => {
                if !f.fixed {
                    s.fixable += 1
                }
            }
            Severity::Pending => s.pending += 1,
            Severity::Ok => s.ok += 1,
        }
    }
    s
}

pub fn print_text(findings: &[Finding], summary: &Summary, verbose: bool) {
    println!("=== dddkit check ===");

    for concern in [Concern::Graph, Concern::Match, Concern::Integrity] {
        let group: Vec<&Finding> = findings.iter().filter(|f| f.concern == concern).collect();
        if group.is_empty() {
            continue;
        }
        println!("\n--- {} ---", concern.label());
        let mut shown = 0;
        for f in &group {
            if f.severity == Severity::Ok && !verbose {
                continue;
            }
            shown += 1;
            let mark = if f.fixed { "FIXED" } else { f.severity.label() };
            println!("{:<8} {:<24} {}", mark, f.code, f.message);
            if let Some(hint) = &f.fix_hint {
                if !f.fixed {
                    println!("{:<8} {:<24} -> {}", "", "", hint);
                }
            }
        }
        if shown == 0 {
            println!("clean ({} check(s) passed)", group.len());
        }
    }

    println!(
        "\nSummary: {} failure(s), {} fixable, {} pending, {} fixed this run.",
        summary.failure, summary.fixable, summary.pending, summary.fixed
    );
    if summary.failure > 0 {
        println!("FAILED");
    } else if summary.fixable > 0 {
        println!("PASSED (with {} fixable finding(s) -- rerun with --fix)", summary.fixable);
    } else {
        println!("PASSED");
    }
}
