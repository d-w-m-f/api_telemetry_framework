# CI Plan (GitHub Actions)

This is the implementation plan for continuous integration. Nothing here is wired up yet — no
`.github/workflows/` exists in the repo today. This doc is what to build against.

## Decisions this plan assumes

Resolved while planning this alongside [`docs/deployment.md`](deployment.md):

- **Registry**: [GitHub Container Registry](https://ghcr.io) (`ghcr.io/<owner>/<repo>-<service>`). Free for
  this repo, authenticates with the workflow's own `GITHUB_TOKEN` — no extra secret to provision.
- **Toolchain provisioning**: [`jdx/mise-action@v4`](https://github.com/jdx/mise-action) reads the root
  [`mise.toml`](../mise.toml) directly, so CI installs the exact same Java/Maven/Node/Python/Poetry/Go
  versions a contributor gets locally with `mise install` — one file stays the single source of truth for
  versions, instead of duplicating version numbers into workflow YAML.
- **Monorepo scoping**: one workflow file per buildable component, each gated by a `paths:` trigger filter,
  rather than one giant workflow with an internal path-filter step. A change to `src/web/**` doesn't need to
  wait on `src/backend/**`'s pipeline, and each workflow stays small enough to read top to bottom.
- **Lint gates are blocking**, not advisory — `.claude/rules/go.md`, `java.md`, and `typescript.md` all treat
  their respective linters/formatters as non-negotiable conventions, not style suggestions, so CI enforces
  that rather than just reporting it.
- **Sandbox APIs are not gated by unit test coverage** — per `.claude/rules/writing_sandbox_apis.md` and the
  language-specific rule files, sandbox API correctness is validated by telemetry flux integration, not unit
  tests. CI honors that by giving the Python sandbox a *real* end-to-end smoke run instead of a coverage
  requirement (see "Python sandbox" below) — this is the same philosophy the rules already state, just
  applied to CI rather than skipped by it.

## Triggers

Every workflow below runs on:

- `pull_request` targeting `master`, filtered to its own `paths:`.
- `push` to `master`, filtered to the same `paths:` — this is also what triggers that component's
  build-and-push-image job (see "Image build & push").

## Per-component pipelines

### Backend (`src/backend/**`, `src/maindb/**`)

```yaml
- jdx/mise-action@v4                    # installs java (temurin-21) + maven from mise.toml
- mvn -B verify                          # compiles, runs unit + @DataJpaTest/@WebMvcTest suites
```

`mvn verify` needs no live Postgres or RabbitMQ: `@DataJpaTest` uses the embedded H2 dependency already in
`pom.xml` against `src/test/resources/application.yml` (`ddl-auto: create-drop`), and AMQP tests use
`spring-rabbit-test`. A formatting gate (`google-java-format`, per `.claude/rules/java.md` §2) isn't wired
into `pom.xml` yet — add a plugin (e.g. `fmt-maven-plugin`) bound to a `mvn fmt:check` goal before adding
that check here; until then this pipeline only compiles and tests.

Triggers on `src/maindb/**` too, since a migration change can break `ddl-auto: validate` against the real
schema even when H2-backed tests stay green — `mvn verify` alone won't catch that; flagged as a known gap
(closing it needs a real Postgres service container running the actual migrations, which is more than this
plan's default backend job does).

### Frontend (`src/web/**`)

```yaml
- jdx/mise-action@v4                    # installs node from mise.toml
- npm ci
- npm run lint                           # ng lint (angular-eslint) -- already in package.json
- npm run format:check                   # prettier --check -- already in package.json
- ng test --no-watch --no-progress --browsers=ChromeHeadless
- npm run build                          # production build, catches AOT/type errors tests don't
```

All four npm scripts already exist in `src/web/package.json` — this pipeline is close to a direct translation
of what's already there, plus the `--browsers=ChromeHeadless` override Karma needs to run without a display.

### Telemetry consumer (`src/telemetry_consumer/**`)

```yaml
- jdx/mise-action@v4                    # installs python 3.14 + poetry from mise.toml
- poetry install
- poetry run python -m pytest            # once a real test suite exists (see note below)
```

Per `.claude/rules/python.md` §4, this component is **not** exempt from normal testing practice — it's
infrastructure, not a sandbox API. But there's no `tests/` directory yet
(`docs/current_state.md` only claims "importing the Python modules... has been run and passes"). This plan
assumes a real `pytest` suite lands before this gate goes in; until then, substitute a smoke step
(`poetry run python -m compileall src`) so the pipeline exists and isn't silently a no-op.

### Python sandbox API (`src/sandbox/api/src/python/**`, `src/sandbox/api/db/**`)

```yaml
- jdx/mise-action@v4                    # installs python 3.14 + poetry from mise.toml
- poetry install
- poetry run python -c "import src.app"  # import smoke check -- catches wiring/syntax errors fast
- docker compose -f src/sandbox/api/src/python/docker-compose.yml \
    -f src/sandbox/api/src/python/docker-compose.ci.yml \
    up --build --abort-on-container-exit --exit-code-from load_n_telemetry
```

The real gate is the last step: it boots the actual 3-layer sandbox (`sandbox-db`, `sandbox-seed`,
`sandbox-api`, `load_n_telemetry`) exactly like production does, and fails the build if `load_n_telemetry`
exits non-zero — i.e. the contract in `spec/contracts/simple_read.openapi.yaml` actually holds end to end.
This *is* "telemetry flux integration," just run as a CI gate instead of only by hand.

A new `docker-compose.ci.yml` override (referenced above, not yet created) is needed because production's
`MAIN_DB_DSN` points at a long-lived external `maindb` reachable over the shared `telemetry-net` network
(see `docker/docker-compose.yml`) — a network that doesn't exist in a bare CI runner. The override instead
adds a throwaway `maindb` service (a plain `postgres:17-alpine` with `src/maindb/migrations/` mounted as
`docker-entrypoint-initdb.d`, no `telemetry-net` involved) on the compose project's own default network, and
sets `RUN_ID`/`MAIN_DB_DSN` to point at it. This sidesteps the cross-project network entirely, since CI
doesn't need one long-lived maindb serving many runs the way production does.

### `load_n_telemetry` (`src/sandbox/load_n_telemetry/**`)

```yaml
- jdx/mise-action@v4                    # installs go 1.25 from mise.toml
- go build ./...
- go vet ./...
- golangci-lint run                      # via golangci/golangci-lint-action
- go test ./...                          # loadgen_test.go, stats_test.go already exist
```

Per `.claude/rules/go.md`, this component follows normal Go testing practice (it's infrastructure, not a
sandbox API under test) — which the existing `internal/service/*_test.go` files already reflect.

### Not covered yet

`src/sandbox/api/src/go/`, `src/sandbox/api/src/java/`, and `src/sandbox/api/src/typescript/` are empty
scaffolds (their `Dockerfile`s are present but 0 bytes) — per `docs/current_state.md`. Add a pipeline for
each, mirroring the Python sandbox's pattern above (build + telemetry-flux smoke run, no coverage gate),
once that implementation actually exists. Don't pre-build a pipeline against an empty directory.

## Image build & push

On `push` to `master` only (not on PRs), each component that has a `Dockerfile` and is part of the
always-on control plane — **backend**, **web**, **telemetry_consumer** — plus the sandbox images needed by
the Kubernetes Job design in `docs/deployment.md` — **python sandbox API** and **`load_n_telemetry`** — gets
built and pushed to GHCR, tagged with the short commit SHA (`ghcr.io/<owner>/<repo>-backend:sha-<short-sha>`).
No `:latest` tag — the deploy step in `docs/deployment.md` always pins an explicit SHA tag, so there's
never ambiguity about which commit is actually running.

This only runs after that component's own build/lint/test job (above) has passed — image push is a
downstream job with a `needs:` dependency, not a parallel one.

## The GitOps hand-off

After a successful image push, one more job runs `kustomize edit set image <service>=ghcr.io/.../<service>:sha-<short-sha>`
inside `deployment/overlays/prod/`, commits, and pushes that change back to `master` using the workflow's own
`GITHUB_TOKEN` (needs `permissions: contents: write`; a token-authored push doesn't re-trigger `on: push`
workflows, so this doesn't loop). ArgoCD, watching `deployment/overlays/prod/`, picks up that commit and
syncs — see [`docs/deployment.md`](deployment.md#argocd-continuous-delivery) for the ArgoCD side of this
hand-off, and for why the sandbox images (built above) are propagated the same way even though they
configure a dynamically-created Job rather than a steady-state Deployment.

## Open follow-ups

- Add `fmt-maven-plugin` (or equivalent) to `src/backend/pom.xml` so the backend pipeline can gate on
  `google-java-format`, per `.claude/rules/java.md` §2.
- Write a real `pytest` suite for `src/telemetry_consumer/` (per `.claude/rules/python.md` §4) — the CI job
  above is written against that suite existing, not around its absence.
- Add a migration-drift check for `src/maindb/migrations/` (a real Postgres service container running
  `ddl-auto: validate` against them) rather than relying on H2's `create-drop` catching it.
- Branch protection: once these workflows exist, require them as passing checks before merge to `master`.
