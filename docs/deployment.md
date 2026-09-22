# Deployment Plan (Kubernetes + ArgoCD)

This is the implementation plan for `deployment/` (currently an empty scaffold — just `.keep`) and for
continuous delivery via ArgoCD. Nothing here is wired up yet. Read alongside
[`docs/architecture.md`](architecture.md) (today's local-only design) and [`docs/ci.md`](ci.md) (what feeds
images into this pipeline).

## Decisions this plan is built on

- **Scope**: Kubernetes hosts the always-on control plane only — **backend**, **web**, and
  **telemetry_consumer**. The main PostgreSQL database and RabbitMQ are assumed to run **outside** the
  cluster (see "External dependencies" below) — no StatefulSets in `deployment/`.
- **Sandbox execution**: redesigned to run as a Kubernetes Job — but *only* when `ENVIRONMENT=prod`. When
  `ENVIRONMENT=local`, the consumer's behavior is byte-for-byte what it is today (shells out to
  `docker compose up` against a sandbox's own `docker-compose.yml`); nothing about local dev changes. See
  "Sandbox execution in Kubernetes" below — this is the biggest single piece of new design in this plan.
- **Manifest tooling**: [Kustomize](https://kustomize.io) — plain YAML plus overlays, no templating
  language, consistent with this repo's general preference for explicit wiring over abstraction layers
  (see e.g. `.claude/rules/gingonic.md` §3, `springboot.md` §1 on constructor injection over DI containers).
- **Registry**: GHCR, per `docs/ci.md` — every image reference in these manifests is
  `ghcr.io/<owner>/<repo>-<service>:sha-<short-sha>`, never `:latest`.
- **Cluster target**: intentionally undecided (could be a VPS running k3s, a managed cloud cluster, or a
  local kind/minikube cluster for now). This plan is written against the plain Kubernetes API and calls out
  the handful of spots that need a concrete value once a target is chosen (marked **⚠ cluster-specific**
  below) — an ingress class name, and nothing else, since there's no StorageClass to pick (no PVCs) and no
  cloud-specific LoadBalancer annotations assumed.
- **Image promotion**: CI commits the new image tag straight into `deployment/overlays/prod/` (see
  `docs/ci.md`'s "GitOps hand-off"); ArgoCD watches that path and syncs automatically. There is no separate
  staging environment yet — `local` (Procfile/docker-compose, per the root README) and `prod` (this doc) are
  the only two, matching the `ENVIRONMENT=local|prod` policy in the root `CLAUDE.md`.
- **Secrets**: [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) — secrets are encrypted
  client-side with `kubeseal` into a `SealedSecret` resource that's safe to commit; the in-cluster controller
  decrypts it into an ordinary `Secret`. No external vault dependency, which matters given the cluster target
  is still open.

## Cluster prerequisites

Whatever the eventual cluster is, it needs, before ArgoCD ever syncs this repo:

1. **Kubernetes ≥ 1.29** — native sidecar containers (`restartPolicy: Always` on an `initContainer`, GA in
   1.29) are how the sandbox Job design below sequences `sandbox-db` → `sandbox-seed` → `sandbox-api` →
   `load_n_telemetry` without needing a separate orchestration sidecar/operator.
2. The **Sealed Secrets controller** installed (`kubeseal` + the in-cluster controller).
3. **ArgoCD** installed, with access to this GitHub repo.
4. An **Ingress controller** of the operator's choice (nginx, Traefik, ...) — **⚠ cluster-specific**: the
   `ingressClassName` in `deployment/overlays/prod/ingress.yaml` is a placeholder until one is chosen.

## `deployment/` layout

```text
deployment/
  base/
    namespace.yaml            # the "api-throughput-n-telemetry" namespace
    backend/
      deployment.yaml
      service.yaml
      kustomization.yaml
    web/
      deployment.yaml
      service.yaml
      kustomization.yaml
    telemetry-consumer/
      deployment.yaml
      serviceaccount.yaml      # bound by the Role below when ENVIRONMENT=prod
      role.yaml                # create/get/list/watch/delete on jobs, pods; get on pods/log
      rolebinding.yaml
      kustomization.yaml
    kustomization.yaml         # aggregates the three services + namespace
  overlays/
    prod/
      kustomization.yaml       # `resources: [../../base]` + `images:` (edited by CI) + patches
      configmap-env.yaml       # non-secret env vars: ENVIRONMENT=prod, APP_VARIANT, DB_DRIVER, hosts/ports
      secrets/
        backend-db-credentials.sealedsecret.yaml
        consumer-db-credentials.sealedsecret.yaml
        rabbitmq-credentials.sealedsecret.yaml
      ingress.yaml              # routes to web + backend Services
  argocd/
    application.yaml            # the ArgoCD Application CR (see below)
```

One `kustomization.yaml` per service under `base/`, aggregated by `base/kustomization.yaml`, patched by
`overlays/prod/kustomization.yaml` — the standard Kustomize base/overlay split, sized for exactly the two
environments this repo actually has.

## Per-service manifests

**backend** and **web**: a `Deployment` (1 replica to start — nothing here needs HA yet) + a `ClusterIP`
`Service`, reading their existing `.env.prod` keys (see `docs/services.md`) from `configmap-env.yaml` (plain
values like `PORT`, `RABBITMQ_HOST`) and from the Sealed Secrets (credentials) via `envFrom`/`env.valueFrom`
— the same variable names either way, so no application code changes for either service; only *where* the
values come from changes between local `.env.prod` and a real deploy.

**telemetry_consumer**: a `Deployment` too (still just 1 replica — per `docs/architecture.md`, only one
consumer is meant to run at a time for the MVP), plus the `ServiceAccount`/`Role`/`RoleBinding` needed for
its `ENVIRONMENT=prod` behavior (below). Unlike backend/web it needs in-cluster RBAC, not just config.

## External dependencies

Main PostgreSQL and RabbitMQ are **not** deployed by anything in `deployment/` — they're assumed to already
exist somewhere reachable from the cluster (a managed database service, a VM, whatever the eventual cluster
target implies), and are referenced purely through the connection-string values in the Sealed Secrets above.
This keeps `deployment/` free of StatefulSets entirely, per the resolved decision, but it does mean
provisioning those two things is explicitly **out of scope** of this plan — flagged as a gap, not solved
here.

## Sandbox execution in Kubernetes

This is the part that doesn't exist today in any form and needs new code, not just new YAML — flagged up
front so it's not mistaken for a pure ops task.

### Why this is needed at all

`src/telemetry_consumer/src/infra/sandbox_runner.py` currently shells out to
`docker compose -f <file> up --build --abort-on-container-exit --exit-code-from load_n_telemetry`. That
assumes a Docker daemon is reachable from wherever the consumer runs. Inside a normal Kubernetes pod, it
isn't — and mounting the host's Docker socket into a pod to make it reachable is a well-known
security anti-pattern (equivalent to giving that pod root on the node), so this plan doesn't do that.

### The fix: an `ENVIRONMENT`-gated `SandboxRunner`

Same factory pattern this repo already uses everywhere else (`fastapi.md` §2, `gingonic.md` §2,
`springboot.md` §3) — one interface, two implementations, selected once at startup:

- `DockerComposeSandboxRunner` — today's `SandboxRunner`, unchanged, used when `ENVIRONMENT=local`.
- `KubernetesJobSandboxRunner` — new, used when `ENVIRONMENT=prod`. Instead of `subprocess.run(["docker",
  "compose", ...])`, it shells out to `kubectl apply -f -` with a rendered Job manifest, then
  `kubectl wait --for=condition=complete-or-failed job/<run-id> --timeout=...`, then reads the exit code off
  the Job's status (and `kubectl logs` for diagnostics on failure). Deliberately kept at the same
  "subprocess + CLI tool" level of abstraction as the Docker Compose path today, rather than pulling in the
  official `kubernetes` Python client — smaller dependency footprint, same mental model to maintain.

`business/service.py`'s `SANDBOX_COMPOSE_FILES` dict gets a sibling, `SANDBOX_K8S_JOB_TEMPLATES`, mapping the
same `(language, framework)` keys to a Job manifest template instead of a compose file path — e.g.
`src/sandbox/api/src/python/k8s-job.yaml`, co-located with that stack's `docker-compose.yml` the same way
that file already is, rather than living under `deployment/` (which is for the always-on plane, not sandbox
definitions). `TelemetryTestService._resolve_compose_path` picks whichever dict applies based on
`ENVIRONMENT`.

### Mapping the 3 layers onto one Job

Docker Compose's `--abort-on-container-exit --exit-code-from load_n_telemetry` semantics — the other two
containers get torn down the moment `load_n_telemetry` exits, and *its* exit code is what matters — maps
directly onto native sidecar containers:

| docker-compose service | Job manifest role                                             |
|-------------------------|----------------------------------------------------------------|
| `sandbox-db`            | `initContainer` with `restartPolicy: Always` (native sidecar), readiness = `pg_isready` |
| `sandbox-seed`          | plain `initContainer` (runs once, must exit 0 before the next one starts) |
| `sandbox-api`           | `initContainer` with `restartPolicy: Always` (native sidecar), readiness = the existing `/health` check |
| `load_n_telemetry`      | the Job's one real (non-sidecar) container                     |

Native sidecars start in order and each must pass its readiness check before the next `initContainer` in the
list runs — so `sandbox-seed` only runs once `sandbox-db` is actually ready, and `load_n_telemetry` only
starts once `sandbox-api` is healthy, exactly mirroring the `depends_on: condition: service_healthy` chain
in today's `docker-compose.yml`. When `load_n_telemetry` (the only non-sidecar container) exits, Kubernetes
terminates the sidecars automatically and the Job's success/failure is `load_n_telemetry`'s exit code alone
— the same signal the consumer already branches on today (`exit_code == 0` → `mark_completed`, else
`_fail` + `DLQ`).

`RUN_ID` and `MAIN_DB_DSN` are injected into the `load_n_telemetry` container's `env` exactly as they are
into today's compose service; `ttlSecondsAfterFinished` is set on the Job spec so completed sandbox Jobs
garbage-collect themselves, mirroring the `docker compose down --volumes` call in `sandbox_runner.py`'s
`finally` block.

### RBAC and image tags

The consumer's `ServiceAccount` (declared under `base/telemetry-consumer/`) is bound to a `Role` scoped to
its own namespace granting `create`/`get`/`list`/`watch`/`delete` on `jobs` and `pods`, and `get` on
`pods/log` — nothing cluster-scoped, nothing outside its own namespace.

The sandbox images (`sandbox-python-fastapi-async`, `load_n_telemetry` — see `docs/ci.md`) are built and
tagged by CI the same way the control-plane images are. Their tags reach the Job template through an env var
on the consumer's own `Deployment` (e.g. `SANDBOX_IMAGE_TAG`), which is itself bumped by the same
CI-commits-back-to-git flow described in `docs/ci.md` — so a sandbox image update is still an ordinary GitOps
commit, even though what it configures is a dynamically-created Job rather than a steady-state resource
ArgoCD directly manages.

### What this explicitly does not cover yet

Only the Python + `fastapi_async` combination has a Job template, matching the one compose file that exists
today. `go`/`java`/`typescript` sandbox variants get a `k8s-job.yaml` the same way they'll eventually get a
`docker-compose.yml`, once those implementations exist (see `docs/current_state.md`) — not before.

## ArgoCD (continuous delivery)

One `Application` (not an app-of-apps — three services doesn't warrant that pattern yet; revisit if this
grows past half a dozen), defined in `deployment/argocd/application.yaml`:

- `source.path`: `deployment/overlays/prod`
- `syncPolicy.automated`: `{ prune: true, selfHeal: true }` — a drift in the live cluster gets reverted back
  to what's in git, and resources removed from the overlay get pruned, without a manual `argocd sync`.
- No staging `Application` yet, per the resolved decision above — adding one later is a new
  `overlays/staging/` directory plus a second `Application` pointing at it, not a redesign.

**The hand-off from CI**: `docs/ci.md`'s last job commits a new image tag into
`deployment/overlays/prod/kustomization.yaml` and pushes to `master`. ArgoCD's git polling (or a webhook, if
configured) picks that commit up and reconciles — that commit *is* the deploy. There's no ArgoCD Image
Updater controller and no manual `kubectl apply` step; the only human-in-the-loop point is the PR that got
merged to produce the commit CI is reacting to.

**Secrets workflow**: authoring or rotating a credential means running `kubeseal` locally against the
target cluster's public key to produce a new `*.sealedsecret.yaml`, committing that file, and letting ArgoCD
sync it like anything else — the plaintext value never touches git, only the sealed ciphertext does.

## Open follow-ups

- Choose the actual cluster target — resolves the **⚠ cluster-specific** ingress-class placeholder.
- Provision the external main PostgreSQL and RabbitMQ this plan assumes already exist.
- Implement `KubernetesJobSandboxRunner` and `src/sandbox/api/src/python/k8s-job.yaml` — currently design
  only, no code.
- Add `go`/`java`/`typescript` sandbox Job templates once those sandbox implementations exist.
- Revisit an app-of-apps ArgoCD structure and/or a `staging` overlay if the service count or environment
  count grows.
