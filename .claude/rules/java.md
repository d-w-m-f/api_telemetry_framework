# Java Rules

Base language rules for all Java code in this repository: the Spring Boot main backend (`src/backend/`) and
the Java sandbox API (`src/sandbox/api/src/java/`) — both read `springboot.md` on top of this file.

These rules apply regardless of which of the two Java uses a given piece of code is for. Where a rule
differs by usage, it's called out explicitly (§5).

## 1. Version and build tool

- **Java 21 (LTS)** for every Java module in this repo.
- **Maven** for dependency management and builds. Don't introduce Gradle into a Java module.

## 2. Formatting

Use **google-java-format** on every Java module. It's opinionated and zero-config on purpose — don't hand
override its output or argue style in review; if a formatting result looks wrong, that's a formatter-config
question, not a style preference.

## 3. Naming

- `camelCase` for variables, methods, and fields.
- `PascalCase` for classes, interfaces, enums, and records.
- `UPPER_SNAKE_CASE` for `static final` constants.
- Package names: all lowercase, no underscores.

## 4. General conventions

- Prefer immutability: `final` fields, records for simple data carriers, constructor injection over mutable
  setters.
- Favor composition over inheritance; don't build deep class hierarchies for code reuse.
- Use `Optional<T>` for values that may legitimately be absent (return types), not for fields or method
  parameters.

## 5. Testing and correctness — usage-dependent

- **Main backend usage** (Spring Boot, `src/backend/`): standard testing practices apply — this is a
  production-shaped, user-facing system. Write unit and integration tests as normal good practice.
- **Sandbox API usage** (`src/sandbox/api/src/java/`): don't treat unit test writing or test coverage as a
  metric for evaluating functional development. The correctness of the contracts should be evaluated by
  telemetry flux integration instead (see `writing_sandbox_apis.md`). This exemption is scoped to the
  sandbox API specifically — it does not extend to the main backend.
