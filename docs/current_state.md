# How is the application going

**Current state:** the MVP e2e path (see `spec/bootstrap.md`) is implemented and builds/tests green locally:
main backend (Spring Boot), frontend (Angular), telemetry consumer (Python), Python+`fastapi_async` sandbox
API, and `load_n_telemetry` (Go). The coding rules in `.claude/rules/` are all populated
(`python.md`, `fastapi.md`, `angular.md`, `typescript.md`, `go.md`, `gingonic.md`, `java.md`, `springboot.md`,
`writing_sandbox_apis.md`). Still stub/empty: the Go/GinGonic, Java/SpringBoot, and TypeScript sandbox API
implementations (only Python's is built), and `deployment/`/`docs/`. The MVP's actual `docker compose up`
end-to-end run has **not** been exercised in this environment — there is no Docker daemon available here, so
that run (see spec/bootstrap.md's "End-to-end verification") is the first thing to do in an environment that
has one. Everything else (`mvn test`, `go test`/`go build`, `ng build`/`ng lint`/`ng test`, importing the
Python modules) has been run and passes.