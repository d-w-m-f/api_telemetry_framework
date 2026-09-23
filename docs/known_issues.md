# Known Issues

Gaps between what's built today and a production-grade application, found by reading the actual code (not
speculation) during a review session on 2026-09-22. Scope is deliberately everything *except* deployment —
that's `docs/deployment.md`'s job. Nothing here is fixed yet; this is the backlog to work from later.

Priority is about "how much does this actually bite," not effort to fix.

## Bugs (verified in code, not hypothetical)

### CORS isn't configured — the browser-based "how to run locally" path is likely broken

**Priority: Critical**

`src/web/.env`'s `NG_APP_API_BASE_URL=http://localhost:8080` means the Angular app (`:4200`) calls the
backend (`:8080`) cross-origin, directly from the browser. There's no `CorsConfigurationSource` or
`@CrossOrigin` anywhere in `src/backend`, and no `proxy.conf.json` wired into `src/web/angular.json` either.
A real browser (unlike `curl`) blocks that request per CORS policy — meaning the README's "open
`localhost:4200`, submit a test" step has probably never actually worked. It fails quietly, too:
`run-test.component.ts`'s error handler shows "Failed to submit the test. Is the backend running?", which is
misleading — the backend would be running, CORS is what's blocking it.

**Fix shape**: either a `WebMvcConfigurer` CORS mapping on the backend (allow `http://localhost:4200` in
`local`, the real frontend origin in `prod`), or an Angular dev-server proxy config — not both, pick one.

### No timeout on the sandbox subprocess

**Priority: Critical**

`src/telemetry_consumer/src/infra/sandbox_runner.py`'s `subprocess.run([...], check=False)` has no
`timeout=`. Since there's exactly one consumer and it blocks for the sandbox's full lifetime by design (see
`docs/architecture.md`), a single hung sandbox container wedges the *entire pipeline* indefinitely — no
alert, no recovery, nothing else gets processed until someone notices and intervenes by hand.

**Fix shape**: a `timeout=` on the `subprocess.run` call, with the timeout duration itself probably becoming
a payload field (bulk-write tests legitimately take longer than a 100-row read).

### An exception (as opposed to a nonzero exit code) never reaches the DLQ

**Priority: High**

`business/service.py`'s `handle()` only calls `_fail()` (which persists the error and publishes to `DLQ`)
when `exit_code != 0`. If something *raises* instead — `docker` missing from `PATH`, a DB connection error, a
malformed message body — `infra/rabbitmq.py`'s consume callback catches it, `nack`s with `requeue=True`, and
RabbitMQ redelivers immediately. There's no retry limit and no backoff, so a genuinely broken ("poison")
message spins at full speed forever instead of eventually landing in `DLQ` like a sandbox failure does.

**Fix shape**: a bounded retry count (tracked via message headers or a small counter table) that, once
exceeded, routes to `DLQ` the same way a nonzero exit code does today — plus a backoff delay between
attempts, since RabbitMQ's `x-dead-letter-exchange` + a TTL queue is the usual way to get delayed requeue
without polling.

## Testing gaps

### `telemetry_consumer` has zero test coverage

**Priority: High**

Per `.claude/rules/python.md` §4, this component is explicitly *not* covered by the sandbox APIs' "no unit
test" exemption — it's infrastructure, and it holds the most interesting logic in the repo (the redelivery
guard, DLQ handling, sandbox orchestration). None of it has a test today; `docs/current_state.md` only
claims "importing the Python modules... has been run and passes," which isn't a test suite.

### The MVP has never actually run end-to-end

**Priority: High**

`docs/current_state.md`: the real `docker compose up` pipeline (submit → enqueue → consume → sandbox →
result) has never been exercised, because this dev environment has no Docker daemon. Everything "passing"
today is per-component (`mvn test`, `go test`, `ng test`, importing Python modules) — the thing the project
exists to do has not been verified as a whole even once.

## API hardening

### No authentication or authorization

**Priority: Medium** (depends entirely on whether this ever runs anywhere but localhost)

`POST /api/telemetry-tests` and `GET /api/telemetry-tests/{runId}` are wide open. Fine for a solo local
tool; not fine the moment this is reachable beyond localhost, since each submission spins a real sandbox.

### No rate limiting

**Priority: Medium**

Nothing stops flooding the queue with submissions — each one is a real Docker Compose spin-up, so this is
also a resource-exhaustion vector, not just an API-hygiene concern.

### No OpenAPI spec for the backend's own API

**Priority: Low**

Inconsistent with the sandbox side, which already documents its contract formally in `spec/contracts/`. The
backend's own public API has no equivalent — worth adding (e.g. springdoc-openapi) for the same reason the
sandbox contracts exist: a written-down contract instead of "read the controller."

## Operability of the control plane

Distinct from the sandbox's deliberate "no built-in OTel by default" policy (`fastapi.md`/`gingonic.md`/
`springboot.md` §6) — that's a considered decision about the thing under test, not about the app that
operates it.

### No health/readiness endpoint

**Priority: Medium** (becomes High once `docs/deployment.md` is implemented)

`spring-boot-starter-actuator` isn't a dependency at all — there's nothing for a load balancer or a
Kubernetes liveness/readiness probe to hit.

### No correlation ID tying a request to its downstream trail

**Priority: Medium**

A browser request → backend log line → RabbitMQ message → consumer log line → sandbox run currently share
only a UUID a human has to grep for by hand across three processes' plain-text logs. For a tool whose whole
point is "what happened on run X," this comes up constantly.

### No metrics on the pipeline itself

**Priority: Low**

Queue depth, time-in-queue, DLQ size, sandbox run duration — none of this is exposed anywhere today. Useful
operational signal, not urgent at current scale (one consumer, manual usage).

## Data lifecycle

### No migration framework

**Priority: Low** (deliberate MVP choice, not an oversight)

Plain numbered SQL files (`src/maindb/migrations/`) with no tracking table or rollback mechanism — a
documented, intentional simplification (`spec/bootstrap.md`). Worth revisiting with a real tool
(Flyway/Liquibase) once schema changes get more frequent or ever need to run against a live database with
real data in it.

### No retention/archival policy

**Priority: Low**

`telemetry_runs`/`telemetry_results` only ever grow. Not urgent at current volume; worth having an answer
before this runs unattended for months.

### The enqueue-then-persist ordering has one uncovered crash window

**Priority: Low**

`TelemetryTestService.submit()` already handles the case where the RabbitMQ publish call itself throws (it
marks the run as failed instead of leaving it pending forever). It does **not** handle a process crash
*between* the DB commit and the publish attempt — that leaves a run stuck "pending" with no error recorded
and no message ever sent. A full fix is a transactional outbox pattern; given this app's stakes, a periodic
reconciliation job that finds and re-flags stuck-pending runs is probably the right amount of effort, not
the full pattern.

## Named architectural limit (not a bug)

### The design assumes exactly one consumer

**Priority: Informational**

`docs/architecture.md` explicitly assumes a single consumer instance — reasonable for the MVP, but it means
"production-grade" here currently means "a hardened single instance," not "horizontally scalable." The
`is_completed` flag guards against RabbitMQ redelivering the *same* message twice; it does not arbitrate two
*different* consumer replicas racing on it. Scaling to N consumers later needs real coordination, not just
turning up a replica count — worth keeping `replicas: 1` an enforced constraint (e.g. in the eventual K8s
Deployment) rather than something that quietly gets bumped up without anyone revisiting this assumption.
