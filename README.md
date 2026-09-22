# API Telemetry Framework

This is a monorepo of a framework that aims to execute and compare load tests in different RESTful API implementations.

**Runtime orchestration**

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![mise](https://img.shields.io/badge/mise-111111.svg?style=for-the-badge)
![Overmind](https://img.shields.io/badge/overmind-b0413e.svg?style=for-the-badge)

**Languages & frameworks**

![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/SpringBoot-%236DB33F.svg?style=for-the-badge&logo=springboot&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=for-the-badge&logo=go&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-%23DD0031.svg?style=for-the-badge&logo=angular&logoColor=white)

**Data & messaging**

![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/Rabbitmq-%23FF6600.svg?style=for-the-badge&logo=rabbitmq&logoColor=white)

**Package managers**

![Maven](https://img.shields.io/badge/apachemaven-%23C71A36.svg?style=for-the-badge&logo=apachemaven&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8C)
![npm](https://img.shields.io/badge/NPM-%23CB3837.svg?style=for-the-badge&logo=npm&logoColor=white)

## How to run

### Local

Prerequisites: [Docker](https://docs.docker.com/get-docker/) + Docker Compose,
[mise](https://mise.jdx.dev/) (runtime version manager), and
[overmind](https://github.com/DarthSim/overmind) (process manager — needs `tmux`). Every language
runtime/package manager itself (Java, Maven, Node, Python, Poetry, Go) is pinned in [`mise.toml`](mise.toml)
and provisioned by mise — no need to install any of them yourself.

1. Trust and install the pinned toolchain (one-time, or whenever `mise.toml` changes):

   ```bash
   mise trust && mise install
   ```

2. First-time setup for the two apps that need an explicit install step (Maven resolves its own
   dependencies on first run, so the backend needs nothing here):

   ```bash
   (cd src/telemetry_consumer && poetry install)
   (cd src/web && npm install)
   ```

3. Every service already ships a working `.env.local` (`docker/`, `src/backend/`, `src/telemetry_consumer/`,
   `src/web/`) — no edits needed to get the local stack running. `.env` is the versioned template each
   `.env.local`/`.env.prod` is derived from; see the root [`CLAUDE.md`](CLAUDE.md#environment-configuration).

4. Start everything — local infra (RabbitMQ + main PostgreSQL), the backend, the telemetry consumer, and
   the frontend — with a single command, per the root [`Procfile`](Procfile):

   ```bash
   overmind start
   ```

   The backend and consumer each wait for infra's ports to open before connecting, so start order isn't a
   concern. Open `http://localhost:4200`. Stop everything with `Ctrl-C`, or `overmind stop`/`overmind kill`
   from another shell.

5. Submit a telemetry test, either from the frontend or directly against the backend:

   ```bash
   curl -X POST http://localhost:8080/api/telemetry-tests \
     -H "Content-Type: application/json" \
     -d '{"language": "python", "framework": "fastapi_async", "testCategory": "read", "testType": "simple_read"}'
   ```

   Poll `GET http://localhost:8080/api/telemetry-tests/{runId}` (or refresh the frontend) until
   `completed` is `true`. The consumer picks the task up, builds, and runs the sandbox for you — Docker
   must be available to it, since it shells out to `docker compose` (see `docs/architecture.md`).

Only the `python` + `fastapi_async` combination is wired end-to-end today (see
[`docs/current_state.md`](docs/current_state.md)). To work on a single process on its own (e.g. iterating
on the frontend without the rest of the stack), run `overmind connect web` to attach to its pane, or just
run that process's own command directly, as shown inside [`Procfile`](Procfile).

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
- [`docs/ci.md`](docs/ci.md) — the GitHub Actions CI plan (planned, not yet wired up).
- [`docs/deployment.md`](docs/deployment.md) — the Kubernetes + ArgoCD deployment plan for `deployment/`
  (planned, not yet wired up).

Design rationale, MVP scope, and open experiment ideas live in [`spec/bootstrap.md`](spec/bootstrap.md);
cross-language sandbox API contracts live under [`spec/contracts/`](spec/contracts/).

## Contributors

<a href="#" target="_blank"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-%23181717.svg?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="#" target="_blank"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white"></a>

**Dérick William de Moraes Frias**
