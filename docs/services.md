# Services Documentation

There are 4 services in this monorepo:

| Name                | Where                       | Key responsibilities                                                                                       |
|---------------------|------------------------------|-------------------------------------------------------------------------------------------------------------|
| **backend**         | `src/backend/`               | Accepts telemetry-test submissions, mints the run UUID, enqueues onto RabbitMQ, and exposes run status.     |
| **sandbox**         | `src/sandbox/`                | The disposable, per-run environment under test: one API implementation per language/framework, the shared sandbox DB schema, and the Go request/telemetry container that drives load and writes results. |
| **telemetry_consumer** | `src/telemetry_consumer/` | The single consumer that listens on the `TelemetryTest` queue, spins up the right sandbox's `docker-compose`, and reconciles success/failure back into the main DB. |
| **web**             | `src/web/`                   | Angular frontend: submit a test, poll its status, render the finished result.                                |

## Backend

The main, "normal" backend. A standard Spring Boot REST service — it's the only part of the pipeline the
frontend talks to directly. It owns the `telemetry_runs`/`telemetry_results` tables in the main PostgreSQL
database and is responsible for enqueueing telemetry-test tasks onto RabbitMQ (see
[`docs/architecture.md`](architecture.md) for the at-least-once/`is_completed` guarantee this involves).

### Stack

- **Java 21**, built with **Maven**.
- **Spring Boot 4.1.1**: `spring-boot-starter-web`, `spring-boot-starter-data-jpa`,
  `spring-boot-starter-amqp`, `spring-boot-starter-validation`.
- **PostgreSQL JDBC driver** (runtime).
- Test stack: `spring-boot-starter-test`, `spring-boot-starter-webmvc-test`,
  `spring-boot-starter-data-jpa-test`, `spring-rabbit-test`, `h2` (in-memory DB for repository tests).

### .env

| Variable            | Description                                        |
|---------------------|------------------------------------------------------|
| `ENVIRONMENT`       | `local` or `prod` — selects environment-specific behavior. |
| `MAINDB_HOST`       | Main PostgreSQL host.                                |
| `MAINDB_PORT`       | Main PostgreSQL port.                                |
| `MAINDB_NAME`       | Main PostgreSQL database name.                       |
| `MAINDB_USER`       | Main PostgreSQL user.                                |
| `MAINDB_PASSWORD`   | Main PostgreSQL password.                            |
| `RABBITMQ_HOST`     | RabbitMQ broker host.                                |
| `RABBITMQ_PORT`     | RabbitMQ broker port.                                |
| `RABBITMQ_USER`     | RabbitMQ broker user.                                |
| `RABBITMQ_PASSWORD` | RabbitMQ broker password.                            |
| `PORT`              | HTTP port the backend listens on (default `8080`).   |

## Sandbox

Not a single deployable service but a disposable, per-run environment: for every telemetry test, the
consumer brings up one implementation's own `docker-compose.yml` and tears it down afterwards. Each sandbox
has three layers — a Postgres database (schema and seed data under `src/sandbox/api/db/`), the API
implementation under test (one directory per language under `src/sandbox/api/src/<language>/`, see
[`CLAUDE.md`](../CLAUDE.md#writing-sandbox-apis)), and `load_n_telemetry`, which fires the workload and
writes results. Only `python` (`fastapi_async` variant) is implemented today; `go`, `java`, and
`typescript` are empty scaffolds (see [`docs/current_state.md`](current_state.md)).

### Stack

- **Sandbox database**: PostgreSQL, schema/seed shared by every language implementation
  (`src/sandbox/api/db/migrations/`, `src/sandbox/api/db/seed/`).
- **Sandbox API** (`python` / `fastapi_async`, the only implemented variant): Python 3.14, Poetry,
  FastAPI, Uvicorn, `asyncpg`. See [`.claude/rules/fastapi.md`](../.claude/rules/fastapi.md) and
  [`.claude/rules/python.md`](../.claude/rules/python.md) for its layering and conventions.
- **`load_n_telemetry`**: Go 1.25, standard library only plus a Postgres client (`pgx`) — no HTTP framework,
  no unit-under-test dependencies, by design (see [`.claude/rules/go.md`](../.claude/rules/go.md)).

### .env

Each sandbox API implementation carries its own `.env`/`.env.local`/`.env.prod` (per the root
[`CLAUDE.md`](../CLAUDE.md#environment-configuration) policy). Today that's just `python`:

| Variable       | Description                                                                 |
|----------------|-------------------------------------------------------------------------------|
| `ENVIRONMENT`  | `local` or `prod`.                                                            |
| `DATABASE_URL` | Sandbox Postgres connection string.                                          |
| `DB_DRIVER`    | Selects the persistence-layer implementation (`asyncpg` today; see `fastapi.md` §2.1). |
| `APP_VARIANT`  | Selects the HTTP-client variant via the factory (`fastapi_async` today; see `fastapi.md` §2). |
| `PORT`         | HTTP port the sandbox API listens on (default `8000`).                       |

`load_n_telemetry` isn't configured through a `.env` file — its sandbox `docker-compose.yml` injects
`SANDBOX_API_URL`, `MAIN_DB_DSN`, `RUN_ID`, `LIMIT`, and `REPETITIONS` directly, with `MAIN_DB_DSN` and
`RUN_ID` coming from the telemetry consumer at spin-up time (see
[`docs/architecture.md`](architecture.md)).

## Telemetry_consumer

The single Python worker described in the root `CLAUDE.md`'s Architecture section. It listens on the
`TelemetryTest` RabbitMQ queue, guards against redelivery via `telemetry_runs.is_completed`, shells out to
the target sandbox's `docker-compose`, and reconciles the outcome (success flips `is_completed`; failure
persists the error and publishes to the `DLQ` exchange).

### Stack

- **Python 3.14**, managed with **Poetry** (`package-mode = false`).
- `pika` — RabbitMQ client.
- `psycopg[binary]` — main PostgreSQL client.
- Layout: `business/` (orchestration), `infra/` (RabbitMQ + sandbox process control), `persistence/`
  (main-DB access).

### .env

| Variable               | Description                                                                                       |
|------------------------|-----------------------------------------------------------------------------------------------------|
| `ENVIRONMENT`          | `local` or `prod`.                                                                                  |
| `DATABASE_URL`         | How the consumer itself (a host process) reaches the main DB.                                      |
| `SANDBOX_MAIN_DB_DSN`  | What gets injected into sandbox containers so `load_n_telemetry` can reach the same main DB over the shared `telemetry-net` docker network — same database, different hostname. |
| `RABBITMQ_URL`         | RabbitMQ connection string.                                                                          |

## Web

The frontend. A single Angular page: pick a test, submit it, poll its status, and render the finished
`telemetry_results` row once complete. No charts yet — see `spec/bootstrap.md`'s MVP scope.

### Stack

- **Angular 19** (standalone components + Signals, no `NgModule`s — see
  [`.claude/rules/angular.md`](../.claude/rules/angular.md)), **Angular Material**, **Angular CDK**, RxJS.
- **npm** as the package manager.
- **`@ngx-env/builder`** loads `.env`/`.env.local`/`.env.prod` at build time (see `angular.md` §4) instead of
  Angular's traditional `environment.ts` file-replacement mechanism.
- ESLint (`@typescript-eslint`, `angular-eslint`) + Prettier for linting/formatting.

### .env

| Variable               | Description                                                     |
|------------------------|---------------------------------------------------------------------|
| `NG_APP_API_BASE_URL`  | Base URL of the main backend the frontend calls (default `http://localhost:8080`). |
