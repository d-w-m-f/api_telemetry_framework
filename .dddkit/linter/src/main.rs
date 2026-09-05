//! dddkit -- deterministic structural linter for DDD-Kit.
//!
//! The linter is the only part of dddkit that does not trust the agent.
//! Everything else in the framework is prose instructions an LLM may follow,
//! follow partially, or narrate as done; this binary makes a checkable claim
//! about the repository instead.
//!
//! It enforces three concerns and nothing else:
//!   graph      -- the spec-code graph resolves end to end
//!   match      -- declared architecture matches the filesystem, both ways
//!   integrity  -- dddkit's own files match their recorded hashes
//!
//! It is a referential-integrity checker, never a reviewer: it answers "is the
//! structure intact?", not "is the content correct?".

mod checks;
mod fixer;
mod frontmatter;
mod model;
mod project;
mod report;

use clap::{Parser, Subcommand, ValueEnum};
use model::{Concern, Severity, SpecModule};

#[derive(Parser)]
#[command(name = "dddkit", version, about = "Deterministic structural linter for DDD-Kit projects")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Validate the project's structural integrity.
    Check(CheckArgs),
}

#[derive(clap::Args)]
struct CheckArgs {
    /// Restrict to one concern instead of all three.
    #[arg(long, value_enum)]
    only: Option<ConcernArg>,

    /// Scope the spec-code graph check to one module (uuid, "Context/module", or a bare module name).
    #[arg(long)]
    module: Option<String>,

    #[arg(long, value_enum, default_value_t = Format::Text)]
    format: Format,

    /// Repair derived data (stale code_glob, stale index.json). Never touches
    /// authored content, contexts.md, or the integrity manifests.
    #[arg(long)]
    fix: bool,

    /// Skip the code_glob fast path and resolve every module by uuid scan.
    /// Verdicts must be identical either way.
    #[arg(long)]
    no_hint: bool,

    /// Also print checks that passed.
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Copy, Clone, PartialEq, Eq, ValueEnum)]
enum ConcernArg {
    Graph,
    Match,
    Integrity,
}

#[derive(Copy, Clone, PartialEq, Eq, ValueEnum)]
enum Format {
    Text,
    Json,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Command::Check(args) => std::process::exit(run_check(args)),
    }
}

fn run_check(args: CheckArgs) -> i32 {
    let root = match project::find_root() {
        Ok(r) => r,
        Err(e) => {
            eprintln!("error: {e}");
            return 2;
        }
    };

    let want = |c: Concern| match args.only {
        None => true,
        Some(ConcernArg::Graph) => c == Concern::Graph,
        Some(ConcernArg::Match) => c == Concern::Match,
        Some(ConcernArg::Integrity) => c == Concern::Integrity,
    };

    let mut findings = Vec::new();

    if want(Concern::Graph) {
        let all_modules = project::spec_modules(&root);
        let scoped = args.module.is_some();
        let modules: Vec<SpecModule> = match &args.module {
            None => all_modules,
            Some(reference) => {
                let matched: Vec<SpecModule> = all_modules
                    .into_iter()
                    .filter(|m| matches_reference(m, reference))
                    .collect();
                if matched.is_empty() {
                    eprintln!("error: no module matching '{reference}'");
                    return 2;
                }
                matched
            }
        };

        let opts = checks::graph::Options { no_hint: args.no_hint, fix: args.fix };
        findings.extend(checks::graph::run(&root, &modules, &opts, scoped));

        if modules.is_empty() {
            findings.push(model::Finding::new(
                Concern::Graph,
                Severity::Pending,
                "no-modules",
                "no domain.md found under specs/BoundedContexts/. Nothing to check yet.",
            ));
        }
    }

    if want(Concern::Match) {
        findings.extend(checks::architecture::run(&root));
    }

    if want(Concern::Integrity) {
        findings.extend(checks::integrity::run(&root));
    }

    let summary = report::summarize(&findings);
    let passed = summary.failure == 0;

    match args.format {
        Format::Text => report::print_text(&findings, &summary, args.verbose),
        Format::Json => {
            let r = report::Report {
                schema: 1,
                root: root.to_string_lossy().to_string(),
                summary,
                passed,
                findings: &findings,
            };
            match serde_json::to_string_pretty(&r) {
                Ok(s) => println!("{s}"),
                Err(e) => {
                    eprintln!("error: could not serialize report: {e}");
                    return 2;
                }
            }
        }
    }

    if passed {
        0
    } else {
        1
    }
}

/// Accepts a uuid, a "Context/module" pair, or a bare module name.
fn matches_reference(m: &SpecModule, reference: &str) -> bool {
    if m.uuid == reference {
        return true;
    }
    match reference.split_once('/') {
        Some((ctx, module)) => m.bounded_context == ctx && m.module == module,
        None => m.module == reference,
    }
}
