# Go Rules

Base language rules for all Go code in this repository: the Gin sandbox API
(`src/sandbox/api/src/go/`, also read `gingonic.md`) and the request/telemetry container
(`src/sandbox/load_n_telemetry/`). `load_n_telemetry` follows this file only — per the root `CLAUDE.md`, it
is written "with as few dependencies as possible," so it must **not** pull in Gin or any other HTTP router
framework; use the standard library (`net/http`, `encoding/json`, etc.) there.

## 1. Version

Pin Go **1.25** in `go.mod` (`go 1.25`) for every Go module in this repo. Bump it deliberately, project-wide,
not per-module.

## 2. Formatting and linting

- `gofmt` and `goimports` are non-negotiable — every file must be formatted with them (import groups:
  stdlib, then third-party, then local, each group blank-line separated — `goimports` does this
  automatically).
- Run `golangci-lint` (default/sane rule set) on every Go module. Treat its findings as real issues to fix,
  not noise to suppress — don't blanket-disable linters via `//nolint` without a reason comment.

## 3. Project layout

Standard Go layout, per module:

```text
cmd/
  main.go          # Entrypoint
internal/
  handler/          # HTTP handlers (only in modules that expose HTTP, e.g. the Gin sandbox API)
  service/           # Business logic, transport-agnostic
  repository/         # Data access (Postgres)
  model/               # Domain types
```

Only export (capitalize) identifiers that are actually used from outside the package. Keep `internal/`
packages internal — that's what the directory name is for.

## 4. Error handling

- Wrap errors with context using `fmt.Errorf("...: %w", err)` so the chain stays inspectable.
- Use `errors.Is` / `errors.As` to check/unwrap errors, never string-match on `err.Error()`.
- Define sentinel errors (`var ErrNotFound = errors.New("...")`) or typed error structs for error cases a
  caller actually needs to branch on; don't invent one for every possible failure.

## 5. Context propagation

Every function that does I/O (HTTP handlers, service calls, repository/DB calls) takes `ctx context.Context`
as its **first** parameter and propagates it all the way down to the driver call (e.g. `pgxpool` /
`database/sql` calls take `ctx`). Don't store a `Context` on a struct; pass it explicitly. This is required
infrastructure for the cancellation-propagation experiment described in `spec/bootstrap.md` — if `ctx` isn't
threaded all the way to Postgres, a client timeout can't actually cancel the in-flight query.

## 6. Naming

- `camelCase` for unexported identifiers, `PascalCase` for exported ones — standard Go convention, not
  `snake_case`.
- Package names: short, lowercase, no underscores (`repository`, not `data_access`).
- Interfaces named for what they do (`Repository`, `Notifier`), not prefixed with `I`.

## 7. Correctness for sandbox usage

When Go code is a sandbox API (i.e. under `src/sandbox/api/src/go/`): don't treat unit test writing or test
coverage as a metric for evaluating functional development — contract correctness is validated through
telemetry flux integration instead (see `writing_sandbox_apis.md`). This does **not** apply to
`load_n_telemetry`, which is infrastructure, not a sandbox API under test — normal testing practice applies
to it.
