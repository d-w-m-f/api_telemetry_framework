# Angular Rules

Rules for the frontend app at `src/web/`. Also read `typescript.md` for base language rules — this file
adds Angular-specific conventions on top.

## 1. Standalone components + Signals

- No `NgModule`s. Every component, directive, and pipe is `standalone: true` (the Angular CLI default in
  recent versions — don't add `standalone: false` or hand-roll an `NgModule`).
- Use Signals (`signal()`, `computed()`, `effect()`) for component and service state instead of
  `BehaviorSubject`-based state patterns.
- HTTP calls still go through Angular's `HttpClient`, which returns `Observable`s — convert the result to a
  Signal at the boundary with `toSignal()` rather than subscribing manually and pushing into a `signal()` by
  hand.

## 2. Styling: Angular Material

Use Angular Material for UI components (buttons, forms, tables, selects, dialogs, etc.). Don't hand-roll a
component Material already provides. App-specific layout/spacing still lives in component SCSS files.

## 3. Structure

```text
src/
  app/
    core/              # Singleton services (API clients, app-wide config), provided in root
    features/
      <feature>/       # One folder per feature (e.g. run-test/): its components, services, and state
    shared/            # Reusable standalone components, pipes, and directives used by 2+ features
  environments/        # See §4 — environment loading
```

Keep feature code inside its `features/<feature>/` folder; promote something to `shared/` only once a second
feature actually needs it.

## 4. Environment configuration

Per the root `CLAUDE.md` policy, the frontend is a "sensible product" and must use `.env` / `.env.local` /
`.env.prod` templates selected by `ENVIRONMENT=local|prod` — not Angular's traditional
`environment.ts`/`environment.prod.ts` file-replacement mechanism, which bypasses actual `.env` files. Load
env values at build time from the real `.env*` files (e.g. via an Angular builder such as `@ngx-env/builder`,
or an equivalent dotenv-for-Angular integration) so there is one env-var mechanism across the whole
repository, not a frontend-specific variant of it.

## 5. Forms

Use Reactive Forms (`FormGroup`/`FormControl` built with `FormBuilder`) for anything beyond a single
uncontrolled input. Don't use Template-Driven Forms.

## 6. Testing

Standard testing practices apply here (unlike sandbox APIs, which validate correctness via telemetry
instead of unit tests — see `writing_sandbox_apis.md`). Use Angular's `TestBed`-based component/unit tests
for components, services, and pipes.
