# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a monorepo for an API throughput and telemetry benchmarking framework. It compares HTTP/DB stack
implementations (language, framework, test type, load profile) by running standardized load tests against
disposable "sandbox" environments and collecting telemetry.

## Current state

See docs/current_state.md

## Directory structure

```text
.claude/
  rules/                # Per-language / per-framework coding rules, read before writing code in that stack
.claudeignore/           # Planning/scratch notes excluded from reads by .claude/settings.json deny rules
mise.toml                # Pins every language runtime/package manager in the repo -- `mise trust && mise install`
Procfile                 # Local process list (infra, backend, telemetry_consumer, web) -- run via `overmind start`
deployment/              # K8s/Kustomize + ArgoCD config (empty scaffold; planned in docs/deployment.md)
docker/
  docker-compose.yml     # Local infra: RabbitMQ + main PostgreSQL, on the shared `telemetry-net` network
docs/                    # Project documentation: architecture, business domain, services, current state
spec/
  bootstrap.md           # MVP scope, resolved decisions, and load-testing methodology notes
  contracts/             # OpenAPI specs, one per test type — the cross-language sandbox API contract
src/
  backend/               # Main ("normal") backend — Spring Boot: POST/GET /api/telemetry-tests
  maindb/
    migrations/          # Plain numbered SQL: telemetry_runs, telemetry_results (no migration framework)
  telemetry_consumer/    # The single Python consumer described in Architecture below
  web/                   # Frontend — Angular: one page, submit + poll + render (see angular.md)
  sandbox/
    api/                 # Sandbox applications under test, one implementation per language/framework
      db/
        migrations/      # Sandbox DB schema (reference domain: categories, products, customers, orders)
        queries/postgres/# Named SQL queries used by sandbox API implementations
        seed/            # Dataset seeding: generate.py, profiles.yaml (tiny/small/large profiles)
      src/
        go/              # GinGonic sandbox API implementation (empty scaffold)
        java/            # Java sandbox API implementation (empty scaffold)
        python/          # FastAPI sandbox API (fastapi_async variant) + docker-compose.yml for this stack
        typescript/      # TypeScript sandbox API implementation (empty scaffold)
    load_n_telemetry/    # Go request/telemetry container: waits for the API, fires the read workload,
                         # writes results directly into telemetry_results (see spec/bootstrap.md)
General_Architecture.png # Reference architecture diagram
```

## Environment configuration

For every "sensible product" in this monorepo — anything whose behavior differs by environment (e.g. the
main frontend and main backend) — use local env var injection:

- Provide `.env`, `.env.local`, and `.env.prod` templates.
- Select behavior via an `ENVIRONMENT` env var with value `'local'` or `'prod'`.

## Language policy

All code, comments, and communication in this repository must be in English.

## Architecture

See documentation at docs/architecture.md


## Writing Sandbox APIs

Sandbox APIs live under `src/sandbox/api/src/<language>/`, one directory per language — a language directory
can hold multiple HTTP-client variants (e.g. FastAPI async/sync) selected by a factory at the entrypoint
rather than split into separate directories. Before writing one, read the rules for both the language and
the HTTP framework in `.claude/rules/` (e.g. a Python/FastAPI sandbox API needs `fastapi.md` and
`python.md`). See `.claude/rules/writing_sandbox_apis.md`.

`src/sandbox/api/src/python/` (the `fastapi_async` variant) is the reference implementation for this
pattern — including its own `docker-compose.yml` (the 3-layer sandbox: `sandbox-db`, `sandbox-seed`,
`sandbox-api`, `load_n_telemetry`) and the DB-driver factory pattern documented in `fastapi.md` §2.1. Use it
as the template when adding the next language/framework.