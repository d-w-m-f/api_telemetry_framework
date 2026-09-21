# FastAPI Rules

These rules apply to Python sandbox API implementations under `src/sandbox/api/src/python/` (see
`writing_sandbox_apis.md`). Also read `python.md` for base Python conventions.

## 1. Layered architecture

```text
src/
  business/
    services/          # Business rules, orchestrates repositories, framework-agnostic

  persistence/
    models/             # ORMs/connectors to the database layer
    repositories/        # Functions/classes that access the database layer

  presentation/
    routes/              # Route handler modules (APIRouter definitions)
    schemas/             # Pydantic data validation schemas
    factory/              # One builder module per HTTP-client variant (see §2)

  app.py                # Aggregates routers into a single APIRouter/app
  main.py               # Entrypoint: reads APP_VARIANT, calls the matching factory builder, exposes `app`
```

`business/` and `persistence/` must stay framework-agnostic — they never import FastAPI/Starlette types.
Only `presentation/` and `main.py` know which HTTP client is in use.

## 2. One app, many HTTP-client variants, chosen by a factory

A single language gets **one** sandbox API directory (e.g. `src/sandbox/api/src/python/`), even when it
implements multiple HTTP-client variants for comparison (e.g. `fastapi_async`, `fastapi_sync`, a future
Starlette variant). Do not fork a separate top-level directory per variant — this maximizes code reuse and
minimizes maintenance overhead across variants that mostly differ in one dimension.

- `main.py` is the single entrypoint. It reads an `APP_VARIANT` environment variable and calls the matching
  builder function from `presentation/factory/` to construct and return the app instance.
- Variants of the **same** framework (e.g. `fastapi_async` vs `fastapi_sync`) share `presentation/routes/`
  and `presentation/schemas/` wherever the framework's API allows it; only the parts that must differ (e.g.
  `async def` vs `def` handlers) are duplicated, kept as thin as possible, and delegate immediately into the
  shared `business/` layer.
- Variants across **different** frameworks (e.g. FastAPI vs Starlette) get their own builder in
  `presentation/factory/`, and may need their own route-registration code, but must still call into the same
  `business/`/`persistence/` layers rather than reimplementing logic.
- `business/` and `persistence/` are fully shared across every variant, regardless of framework — this is
  where the actual reuse payoff is.

This keeps `APP_VARIANT` (which HTTP-client implementation to run) orthogonal to `ENVIRONMENT` (`local` /
`prod`, per the root `CLAUDE.md` env-injection policy) — the two are independent knobs.

### 2.1. A second factory for the DB-access library

Which DB-access library backs `persistence/repositories/` (e.g. `asyncpg` vs a future SQLAlchemy variant) is
its own comparison knob, orthogonal to `APP_VARIANT` — a language's HTTP-client variant and its DB-driver
variant can vary independently. This gets its own, smaller factory:

- `persistence/repositories/` defines an ABC per repository (e.g. `ProductRepository`) that `business/`
  depends on, plus one concrete implementation per library under comparison (e.g.
  `AsyncpgProductRepository`).
- `persistence/factory/` reads a `DB_DRIVER` env var and returns the matching concrete implementation —
  called once at app startup (see the `lifespan` handler in a `presentation/factory/` builder), not per
  request, since the concrete implementation owns a connection pool.

See `src/sandbox/api/src/python/` for the reference implementation of both factories.

## 3. Dependency injection

Routes obtain services and repositories via FastAPI's `Depends()` mechanism — don't instantiate
services/repositories directly inside a route handler, and don't reach for a global/singleton container.
This keeps handlers testable and keeps the wiring explicit and consistent across sync and async variants.

## 4. Schemas and contracts

Every route declares an explicit Pydantic `response_model` (or equivalent typed return annotation) and typed
request body/query schemas from `presentation/schemas/`. Since sandbox API correctness is validated through
telemetry flux integration rather than unit tests (see §5), the schema layer is the main place where a
contract is actually enforced and documented — don't skip it "for now."

## 5. Correctness is validated by telemetry, not unit tests

Don't treat unit test writing or test coverage as a metric for evaluating functional development. The
correctness of the contracts should be evaluated by telemetry flux integration.

## 6. No built-in observability instrumentation

Sandbox APIs must **not** bundle their own OpenTelemetry (or other) auto-instrumentation by default.
Telemetry is collected externally, by the request/telemetry container (`src/sandbox/load_n_telemetry/`) and
infra-level metrics. Baking instrumentation into every sandbox API would:

- add a cross-language variable (instrumentation overhead/behavior differs per SDK) that contaminates the
  throughput comparison the framework exists to make, and
- foreclose the "cost of observability" experiment (OTel off / metrics only / traces at 1%/10%/100%) noted in
  `spec/bootstrap.md`, which depends on instrumentation being an explicit, controllable variable rather than
  an always-on default baked into the app.

If a specific experiment needs in-process instrumentation, add it as an explicit, env-var-gated option for
that experiment — never as a default.
