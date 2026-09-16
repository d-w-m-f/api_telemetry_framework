# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a monorepo for an API throughput and telemetry benchmarking framework. It compares HTTP/DB stack
implementations (language, framework, test type, load profile) by running standardized load tests against
disposable "sandbox" environments and collecting telemetry.

**Current state:** early scaffold. Most directories are placeholders (`.keep` files, no code yet). What
actually exists today: this file's directives, `spec/bootstrap.md` (MVP scope and open questions), the
sandbox reference-domain DB schema and seed data (`src/sandbox/api/db/`), and the coding rules in
`.claude/rules/` (`python.md`, `fastapi.md`, `angular.md`, `typescript.md`, `go.md`, `gingonic.md`,
`java.md`, `springboot.md`, and `writing_sandbox_apis.md` — all populated). There is no build/lint/test
tooling wired up yet; do not assume commands like `npm test`, `poetry install`, `go build`, or `mvn package`
work until the corresponding app scaffold is actually populated.

## Directory structure

```text
.claude/
  rules/                # Per-language / per-framework coding rules, read before writing code in that stack
.claudeignore/           # Planning/scratch notes excluded from reads by .claude/settings.json deny rules
deployment/              # Deployment configuration (empty scaffold)
docker/
  docker-compose.yml     # Local infra: RabbitMQ + PostgreSQL (currently a stub)
docs/                    # Project documentation (empty scaffold)
spec/
  bootstrap.md           # MVP scope, open questions, and load-testing methodology notes
src/
  backend/               # Main ("normal") backend — Spring Boot (empty scaffold)
  maindb/                # Main database (PostgreSQL) migrations/config (empty scaffold)
  web/                   # Frontend — Angular (empty scaffold)
  sandbox/
    api/                 # Sandbox applications under test, one implementation per language/framework
      db/
        migrations/      # Sandbox DB schema (reference domain: categories, products, customers, orders)
        queries/postgres/# Named SQL queries used by sandbox API implementations
        seed/            # Dataset seeding: generate.py, profiles.yaml (tiny/small/large profiles)
      src/
        go/              # GinGonic sandbox API implementation
        java/            # Java sandbox API implementation
        python/          # FastAPI sandbox API implementation (business/persistence/presentation layers)
        typescript/      # TypeScript sandbox API implementation
    load_n_telemetry/    # Go request/telemetry container: seeds/warms, fires load, collects telemetry (empty scaffold)
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

See `General_Architecture.png` for the full diagram. Summary:

- **Frontend** (Angular) talks to the **main backend** (Spring Boot) in a standard client-server model, and
  displays exhibition data served by it.
- The main backend connects to the **main database** (PostgreSQL).
- The frontend also generates telemetry-test payloads, which the main backend enqueues onto a **RabbitMQ**
  broker for async processing in a sandbox environment. Two direct exchanges are used:
  - `TelemetryTest` — receives telemetry test tasks.
  - `DLQ` — aggregates tasks that fail or cannot be processed.
- RabbitMQ and the worker must both guarantee **at-least-once processing**. To prevent double-processing, a
  row is written at enqueue time with a serial id, the JSON event, and a status; the status is a boolean
  `is_completed` that is only flipped on completion (`false` covers everything else: waiting, DLQ, retry,
  processing, etc.).
- A single **Python consumer** listens on the `TelemetryTest` queue (only one consumer for now) and is
  responsible for:
  - Spinning up the correct sandbox environment for the event payload, without bloating its own image with
    dependencies for every other language/stack in the monorepo (spinning strategy still an open problem —
    see `spec/bootstrap.md`).
  - Monitoring and collecting telemetry during the run.
  - Persisting temporal and general run state to the main database during and after collection.
  - On error, persisting the error to the main database and enqueueing a task to the `DLQ` exchange.
- Each **sandbox environment** has three layers:
  1. **Database layer** (`sandbox database`) — the DB engine under load. PostgreSQL only for now.
  2. **API/Application layer** (`sandbox application`) — the microservice(s) being tested and measured, one
     implementation per language/framework under `src/sandbox/api/src/`.
  3. **Request/Telemetry container** (`src/sandbox/load_n_telemetry/`) — written in Go with as few
     dependencies as possible; seeds/warms the sandbox database, fires requests, collects telemetry, and
     returns data to the consumer.

### Test/comparison criteria

1. Language: Python, Java, Go, ...
2. HTTP client: FastAPI, GinGonic
   2.1 Specific client implementations: FastAPI async, FastAPI sync, GinGonic w/ channels
3. Test category: Read or Write
4. Test type: Sequential read, complex joins read, bulk write
   4.1 Test configurations: category size (small, medium, big, extreme), environment resources, repetitions, etc.
5. Load type
6. DB engine (PostgreSQL only for now, but it will become a knob)

## Writing Sandbox APIs

Sandbox APIs live under `src/sandbox/api/src/<language>/`, one directory per language — a language directory
can hold multiple HTTP-client variants (e.g. FastAPI async/sync) selected by a factory at the entrypoint
rather than split into separate directories. Before writing one, read the rules for both the language and
the HTTP framework in `.claude/rules/` (e.g. a Python/FastAPI sandbox API needs `fastapi.md` and
`python.md`). See `.claude/rules/writing_sandbox_apis.md`.