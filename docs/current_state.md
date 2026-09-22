# Current State

## Built and working

The MVP end-to-end path (see [`spec/bootstrap.md`](../spec/bootstrap.md)) is implemented and builds/tests
green locally:

- Main backend (Spring Boot)
- Frontend (Angular)
- Telemetry consumer (Python)
- Sandbox API: Python + `fastapi_async`
- `load_n_telemetry` (Go)

The coding rules in `.claude/rules/` are all populated: `python.md`, `fastapi.md`, `angular.md`,
`typescript.md`, `go.md`, `gingonic.md`, `java.md`, `springboot.md`, `writing_sandbox_apis.md`.

Runtime/package-manager versions are pinned once, repo-wide, in the root [`mise.toml`](../mise.toml)
(`mise trust && mise install`), and the local host processes (infra, backend, telemetry consumer, frontend)
start/stop together via the root [`Procfile`](../Procfile) (`overmind start`) — see the root
[`README.md`](../README.md#local).

## Still stub/empty

- The Go/GinGonic, Java/SpringBoot, and TypeScript sandbox API implementations — only Python's is built.
- `deployment/`.

## Not yet verified

The MVP's actual `docker compose up` end-to-end run has **not** been exercised in this environment — there
is no Docker daemon available here, so that run (see `spec/bootstrap.md`'s "End-to-end verification"
section) is the first thing to do in an environment that has one.

Everything else — `mvn test`, `go test`/`go build`, `ng build`/`ng lint`/`ng test`, importing the Python
modules — has been run and passes.