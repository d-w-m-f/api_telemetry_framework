//! Core types shared by every check.
//!
//! The severity ladder is the linter's central distinction (see
//! `.dddkit/shared_language.md` section 5, "Achado Corrigível vs. Falha"):
//! a Failure is the absence of something that cannot be derived, while a
//! Fixable finding is drift in derived data that is always reconstructible
//! from the source of truth (the module's uuid).

use serde::Serialize;
use std::path::PathBuf;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Severity {
    /// Nothing to report.
    Ok,
    /// Not a problem: the module simply hasn't reached this pipeline stage yet.
    Pending,
    /// Derived data drifted. Reconstructible without a human decision (`--fix`).
    Fixable,
    /// Something that cannot be derived is missing or contradictory. Exit 1.
    Failure,
}

impl Severity {
    pub fn label(self) -> &'static str {
        match self {
            Severity::Ok => "OK",
            Severity::Pending => "PENDING",
            Severity::Fixable => "FIXABLE",
            Severity::Failure => "FAILURE",
        }
    }
}

/// The three concerns the linter enforces. These, not the five historical
/// check numbers, are the public surface (`--only`): check numbering is an
/// implementation detail and shouldn't be API.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Concern {
    /// The spec-code graph resolves end to end.
    Graph,
    /// Declared architecture matches the filesystem, both directions.
    Match,
    /// dddkit's own files still match their recorded hashes.
    Integrity,
}

impl Concern {
    pub fn label(self) -> &'static str {
        match self {
            Concern::Graph => "spec-code graph",
            Concern::Match => "architectural match",
            Concern::Integrity => "framework integrity",
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct Finding {
    pub concern: Concern,
    pub severity: Severity,
    /// Stable machine-readable code, safe to match on from a skill or CI.
    pub code: &'static str,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub module: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub uuid: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fix_hint: Option<String>,
    /// Set when `--fix` actually repaired this finding in this run.
    pub fixed: bool,
}

impl Finding {
    pub fn new(concern: Concern, severity: Severity, code: &'static str, message: impl Into<String>) -> Self {
        Finding {
            concern,
            severity,
            code,
            message: message.into(),
            module: None,
            uuid: None,
            path: None,
            fix_hint: None,
            fixed: false,
        }
    }

    pub fn module(mut self, m: &SpecModule) -> Self {
        self.module = Some(m.reference());
        self.uuid = Some(m.uuid.clone());
        self
    }

    pub fn path(mut self, p: impl Into<String>) -> Self {
        self.path = Some(p.into());
        self
    }

    pub fn fix_hint(mut self, h: impl Into<String>) -> Self {
        self.fix_hint = Some(h.into());
        self
    }
}

/// A module as declared on the spec side (one `domain.md` + its siblings).
#[derive(Debug, Clone)]
pub struct SpecModule {
    /// The source of truth for this module's identity. Never reassigned.
    pub uuid: String,
    pub bounded_context: String,
    pub module: String,
    pub spec_dir: PathBuf,
    pub rel_spec_dir: String,
    /// `None` when still an unresolved template placeholder.
    pub module_kind: Option<String>,
    /// `None` when still an unresolved template placeholder. A hint, never authority.
    pub code_glob: Option<String>,
}

impl SpecModule {
    pub fn reference(&self) -> String {
        format!("{}/{}", self.bounded_context, self.module)
    }
}

/// A module's presence on the code side: the markdown file carrying its
/// `implements_uuid`. Finding the anchor *is* finding the module.
#[derive(Debug, Clone)]
pub struct Anchor {
    pub path: PathBuf,
    pub rel_path: String,
}
