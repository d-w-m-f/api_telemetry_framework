# Python Rules

These rules apply to all Python code in this repository (sandbox APIs, the telemetry consumer, seed/tooling
scripts). For Python code that is also a FastAPI sandbox API, also read `fastapi.md`.

## 1. PEP 8

No formatter/linter is mandated by this rule — follow PEP 8 by convention. The parts that matter most:

- **Indentation:** 4 spaces per level. Never tabs.
- **Line length:** 79 characters for code, 72 for comments and docstrings. Break long expressions with
  parentheses rather than backslash continuation.
- **Naming:**
  - `snake_case` for functions, methods, variables, and module names.
  - `PascalCase` (CapWords) for class names.
  - `UPPER_SNAKE_CASE` for constants.
  - A single leading underscore (`_name`) for internal/non-public attributes and functions.
- **Imports:**
  - One import per line.
  - Grouped in this order, each group separated by a blank line: standard library, third-party, local
    (first-party) — and alphabetized within each group.
  - Always at the top of the file, never inside functions unless avoiding a circular import.
  - Absolute imports preferred over relative imports.
- **Whitespace:**
  - No trailing whitespace on any line.
  - One space around binary operators (`x = a + b`, not `x=a+b`).
  - No space immediately inside parentheses, brackets, or braces (`foo(a, b)`, not `foo( a, b )`).
  - No space before a comma, semicolon, or colon; one space after.
- **Blank lines:** two blank lines between top-level function/class definitions, one blank line between
  methods inside a class.
- **Comparisons:**
  - Use `is` / `is not` when comparing to `None`, never `==`.
  - Use `isinstance(x, T)` for type checks, never `type(x) == T`.
  - Don't compare boolean values with `==`/`!=` against `True`/`False` — use the value (or `not value`)
    directly.
- **Strings:** pick one quote style (`"double quotes"`) and use it consistently within a file/project.

## 2. Type hints

Type hints are required on the signatures of all public functions and methods (route handlers, service
methods, repository methods, factory/builder functions) — parameters and return type. Type hints on
private helpers and local variables are encouraged but not required.

This is enforced leniently: hints are expected as a matter of code review/readability, but no static type
checker (mypy, pyright, ...) gates CI or blocks a change over a typing issue. If you add a type checker
later, treat its output as advisory here, not a merge gate.

## 3. Package manager

Use **Poetry** for dependency management in every Python app (see `src/sandbox/api/src/python/pyproject.toml`
for the existing example, which uses `package-mode = false` since these are applications, not libraries).
Don't mix in pip/requirements.txt-based workflows or switch a given app to another manager.

## 4. Correctness

Don't treat unit test writing or test coverage as a metric for evaluating functional development on sandbox
APIs specifically — see `fastapi.md` and `writing_sandbox_apis.md` for why (contract correctness there is
validated through telemetry flux integration instead). This does **not** apply to non-sandbox Python code
(e.g. the telemetry consumer) — normal testing practice applies there.
