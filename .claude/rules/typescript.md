# TypeScript Rules

Base language rules for all TypeScript code in this repository: the Angular frontend (`src/web/`, also read
`angular.md`) and any future TypeScript sandbox API under `src/sandbox/api/src/typescript/` (also read that
framework's rule file, e.g. `express.md`, once it exists — see `writing_sandbox_apis.md`).

## 1. Compiler strictness

`tsconfig.json` must have `"strict": true` (which enables `noImplicitAny`, `strictNullChecks`,
`strictFunctionTypes`, etc.) in every TypeScript app in this repo. Don't loosen it per-app.

## 2. Typing discipline

- Never use `any`. If a type is genuinely unknown, use `unknown` and narrow it before use.
- Prefer `interface` for object shapes that might be extended/implemented; use `type` for unions,
  intersections, tuples, and function types.
- Exported/public functions and class methods must have an explicit return type — don't rely on inference
  across a module boundary.
- Use `enum`/union-of-string-literals for closed sets of values (e.g. `'local' | 'prod'` for `ENVIRONMENT`)
  rather than bare strings.

## 3. Modules

- ES modules only (`import`/`export`). No CommonJS (`require`/`module.exports`).
- Prefer named exports over default exports — named exports are grep-able and rename-safe across the
  codebase; reserve default exports for cases a framework specifically requires them (e.g. some Angular
  schematics-generated files).

## 4. Naming

- `camelCase` for variables, functions, and methods.
- `PascalCase` for classes, interfaces, type aliases, and enums.
- `UPPER_SNAKE_CASE` for module-level constants.

## 5. Async

Use `async`/`await` for asynchronous code. Avoid raw `.then()`/`.catch()` chains except where a library's API
forces it.

## 6. Tooling

Use ESLint (with `@typescript-eslint`) and Prettier in every TypeScript app. Let Prettier own formatting;
ESLint is for correctness/style rules Prettier doesn't cover. Don't hand-format around what a formatter would
otherwise do automatically.
