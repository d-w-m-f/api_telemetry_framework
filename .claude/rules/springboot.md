# Spring Boot Rules

Spring Boot is used in two places in this repository, with different rules for each. Also read `java.md` for
base Java conventions. If you're not sure which usage applies, check the path: `src/backend/` is the main
backend, `src/sandbox/api/src/java/` is the sandbox API.

## 1. Layered architecture (both usages)

Standard Spring layout, idiomatic to the framework:

```text
src/main/java/<base-package>/
  controller/     # REST controllers — request/response mapping only, no business logic
  service/         # Business rules, orchestrates repositories
  repository/       # Spring Data repositories / data access
  entity/             # JPA entities
  dto/                  # Request/response DTOs (separate from entities — never expose entities directly)
```

- Constructor injection only. No field-level `@Autowired` — dependencies are `private final` fields set in
  the constructor (Lombok `@RequiredArgsConstructor` is fine if the project already uses Lombok).
- Controllers never return or accept entities directly — always map to/from a `dto/` type, even when it
  feels redundant for a trivial endpoint. This is what keeps the persistence model free to change without
  breaking the API contract.
- Validate incoming DTOs with Jakarta Bean Validation annotations (`@NotNull`, `@Valid`, etc.) on the
  controller method parameter, not with hand-rolled `if` checks in the service layer.

## 2. Main backend usage (`src/backend/`)

- Standard testing practices apply (unit tests for services, `@WebMvcTest`/`@DataJpaTest`/integration tests
  as normal) — this is a production-shaped, user-facing system, not a sandbox API. See `java.md` §5.
- Connects to the main PostgreSQL database (`src/maindb/`) via Spring Data JPA.
- Owns enqueueing telemetry-test payloads onto the `TelemetryTest` RabbitMQ exchange (see the root
  `CLAUDE.md` architecture section) — enqueue and the `is_completed`-row write must happen together so a
  crash between the two can't lose or duplicate a task.

## 3. Sandbox API usage (`src/sandbox/api/src/java/`)

- **One module, one factory, multiple variants.** Following the same pattern as `fastapi.md` §2 and
  `gingonic.md` §2: the Java sandbox API lives in a single directory even if it ends up comparing multiple
  HTTP-layer approaches. A factory/config class selects the active configuration via an `APP_VARIANT`
  environment variable at startup, rather than forking a separate top-level directory per variant. (The
  specific Java sandbox variants to compare are still open — see `spec/bootstrap.md` — but whatever they end
  up being, they follow this structure.)
- Don't treat unit test writing or test coverage as a metric for evaluating functional development — the
  correctness of the contracts should be evaluated by telemetry flux integration instead (see
  `writing_sandbox_apis.md` and `java.md` §5).
- No built-in observability instrumentation by default — same reasoning as `fastapi.md` §6 and `gingonic.md`
  §6: telemetry is collected externally by `src/sandbox/load_n_telemetry/`, and baking OpenTelemetry (or
  Spring Boot Actuator metrics) into the sandbox app by default would add a cross-language variable to the
  throughput comparison and foreclose the observability-cost experiment in `spec/bootstrap.md`. Add
  instrumentation only as an explicit, env-var-gated option for an experiment that specifically needs it.
