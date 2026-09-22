# GinGonic Rules

These rules apply to the Go sandbox API implementation under `src/sandbox/api/src/go/` (see
`writing_sandbox_apis.md`). Also read `go.md` for base Go conventions.

## 1. Layered architecture

```text
cmd/
  main.go            # Entrypoint: reads APP_VARIANT, calls the matching builder, runs the server

internal/
  handler/            # Gin handler functions + route registration
  service/             # Business rules, transport-agnostic (no Gin imports)
  repository/           # Postgres data access (no Gin imports)
  model/                 # Domain types shared by service/repository
  factory/                 # One builder per HTTP-client variant (see §2)
```

`service/`, `repository/`, and `model/` must never import `gin` — they stay usable regardless of which
variant is selected. Only `handler/`, `factory/`, and `cmd/main.go` know about Gin.

## 2. One module, two variants, chosen by a factory

Per CLAUDE.md's test criteria, this sandbox API implements two comparison variants, both living in this same
module (not split into separate top-level directories, mirroring the pattern in `fastapi.md` §2):

- **`gin`** — a straightforward Gin handler that calls into `service/` directly and writes the response.
- **`gin_channels`** — the same routes, but request handling is offloaded to a fixed-size worker-pool of
  goroutines communicating over channels (handler sends a job on a channel, a worker picks it up, calls
  `service/`, and sends the result back on a response channel/`chan` future). This variant exists to measure
  the throughput/latency effect of that concurrency pattern against the plain handler.

`cmd/main.go` reads an `APP_VARIANT` environment variable (`gin` or `gin_channels`) and calls the matching
builder in `internal/factory/`. Both variants share `internal/service/`, `internal/repository/`, and
`internal/model/` entirely — only `internal/handler/` (and, for `gin_channels`, the worker-pool wiring)
differs. This is orthogonal to `ENVIRONMENT` (`local`/`prod`), same as in the Python sandbox API.

## 3. Dependency injection

Use plain constructor functions (`NewHandler(svc service.Service) *Handler`,
`NewService(repo repository.Repository) *Service`) wired up explicitly in `internal/factory/`. Don't reach
for a DI framework/container — Go's idiomatic approach is explicit wiring at the composition root
(`cmd/main.go` via the factory), not reflection-based injection.

## 4. Request/response contracts

Define explicit request/response structs in `internal/model/` (or a `internal/handler/dto` subpackage if a
shape is truly handler-only) with `json` struct tags, and validate incoming payloads explicitly in the
handler before calling into `service/`. Since correctness is validated through telemetry flux integration
rather than unit tests (§5), these structs are the contract — keep them precise and don't let a handler
accept/return an untyped `map[string]interface{}`.

## 5. Correctness is validated by telemetry, not unit tests

Don't treat unit test writing or test coverage as a metric for evaluating functional development. The
correctness of the contracts should be evaluated by telemetry flux integration.

## 6. No built-in observability instrumentation

Same rule as `fastapi.md` §6, for the same reason: don't bundle OpenTelemetry (or other) auto-instrumentation
into this sandbox API by default. Telemetry is collected externally by
`src/sandbox/load_n_telemetry/`. Baking in instrumentation would add a cross-language variable to the
throughput comparison and foreclose the observability-cost experiment in `spec/bootstrap.md`. Add
instrumentation only as an explicit, env-var-gated option for a specific experiment that needs it.
