## Architecture

The project architecture is such:

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
- The main backend mints a UUID for each telemetry test at enqueue time and writes it, alongside the
  payload, into a `telemetry_runs` row (`is_completed = false`). That same UUID is carried unchanged through
  the whole pipeline — the AMQP message body, the sandbox env vars, the `telemetry_results` row — which is
  what makes `is_completed` a valid guard against RabbitMQ redelivering the same message twice: a second
  delivery references the same row and can see the flag already flipped.
- A single **Python consumer** listens on the `TelemetryTest` queue (only one consumer for now) and is
  responsible for:
  - Spinning up the correct sandbox environment for the event payload via that stack's own docker-compose
    file (`docker compose -f <file> up`), without bloating its own image with dependencies for every other
    language/stack in the monorepo. The consumer blocks for the sandbox's full lifetime — its own liveness
    during that call is the monitoring mechanism, not a separate polling loop.
  - Before spin-up: checking `telemetry_runs.is_completed` for the message's UUID (redelivery guard), then
    inserting a pending `telemetry_results` row keyed by that same UUID and injecting it plus main-DB
    connection info into the sandbox via env vars.
  - On success, `load_n_telemetry` (inside the sandbox) writes the finished results directly into that main-DB
    row itself — the consumer does not need to relay results on the happy path, it just flips
    `telemetry_runs.is_completed = true`.
  - On error (sandbox exits non-zero, times out, or otherwise never completes), the consumer detects this
    from the process exit, persists the failure state to the main database itself (since a dead container
    can't report its own failure), and enqueues a task to the `DLQ` exchange.
  - See `spec/bootstrap.md`'s "MVP decisions" section for the full resolution of this design.
- Each **sandbox environment** has three layers:
  1. **Database layer** (`sandbox database`) — the DB engine under load. PostgreSQL only for now.
  2. **API/Application layer** (`sandbox application`) — the microservice(s) being tested and measured, one
     implementation per language/framework under `src/sandbox/api/src/`.
  3. **Request/Telemetry container** (`src/sandbox/load_n_telemetry/`) — written in Go with as few
     dependencies as possible; seeds/warms the sandbox database, fires requests, collects telemetry, and
     returns data to the consumer.

