# API Telemetry Framework

This is a monorepo of a framework that aims to execute and compare load tests in different RESTful API implementations.

## How to run

### Local

Prerequisites: Docker + Docker Compose, Java 21 + Maven, Node.js (Angular 19), Python 3.14 + Poetry.

1. Every service already ships a working `.env.local` (`docker/`, `src/backend/`, `src/telemetry_consumer/`,
   `src/web/`) — no edits needed to get the local stack running. `.env` is the versioned template each
   `.env.local`/`.env.prod` is derived from; see the root [`CLAUDE.md`](CLAUDE.md#environment-configuration).

2. Start the shared local infra (RabbitMQ + main PostgreSQL):

   ```bash
   docker compose --env-file docker/.env.local -f docker/docker-compose.yml up -d
   ```

3. Run the main backend (reads `src/backend/.env.local`):

   ```bash
   cd src/backend
   set -a && source .env.local && set +a
   mvn spring-boot:run
   ```

4. Run the telemetry consumer (reads `src/telemetry_consumer/.env.local`):

   ```bash
   cd src/telemetry_consumer
   poetry install
   set -a && source .env.local && set +a
   poetry run python src/main.py
   ```

   Docker must be available to this process — it shells out to `docker compose` to spin up a sandbox
   whenever it picks up a task (see `docs/architecture.md`).

5. Run the frontend:

   ```bash
   cd src/web
   npm install
   npm start
   ```

   Open `http://localhost:4200`.

6. Submit a telemetry test, either from the frontend or directly against the backend:

   ```bash
   curl -X POST http://localhost:8080/api/telemetry-tests \
     -H "Content-Type: application/json" \
     -d '{"language": "python", "framework": "fastapi_async", "testCategory": "read", "testType": "simple_read"}'
   ```

   Poll `GET http://localhost:8080/api/telemetry-tests/{runId}` (or refresh the frontend) until
   `completed` is `true`. The consumer (step 4) picks the task up, builds, and runs the sandbox for you —
   no extra manual `docker compose` call needed here.

Only the `python` + `fastapi_async` combination is wired end-to-end today (see
[`docs/current_state.md`](docs/current_state.md)).

### Prod

Not defined yet.

## Documentation

Start with the root [`CLAUDE.md`](CLAUDE.md) for the repository layout, environment-configuration policy,
and language/framework coding rules (`.claude/rules/`). Further documentation lives under `docs/`:

- [`docs/architecture.md`](docs/architecture.md) — how the pieces fit together: frontend, backend, RabbitMQ,
  the telemetry consumer, and the 3-layer sandbox.
- [`docs/business.md`](docs/business.md) — the core domain: what's being compared (language, HTTP client,
  test type, load type, DB engine) and why.
- [`docs/services.md`](docs/services.md) — one section per service (backend, sandbox, telemetry_consumer,
  web): stack, dependencies, and environment variables.
- [`docs/current_state.md`](docs/current_state.md) — what's actually built and working right now, versus
  what's still stubbed out.

Design rationale, MVP scope, and open experiment ideas live in [`spec/bootstrap.md`](spec/bootstrap.md);
cross-language sandbox API contracts live under [`spec/contracts/`](spec/contracts/).

## Contributors

<a href="#" target="_blank"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-%23181717.svg?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="#" target="_blank"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white"></a>

**Dérick William de Moraes Frias**
