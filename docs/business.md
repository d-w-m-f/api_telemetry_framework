# Business Domain

> Note: despite the filename, this isn't a business-rules document — there's no business logic to speak of.
> It's an explanation of the core domain: the dimensions this framework varies in order to produce a
> comparison.

## Test / comparison criteria

Each telemetry test is a point in the space defined by these dimensions:

1. **Language** — Python, Java, Go, TypeScript, ...
2. **HTTP client** — the framework under test (FastAPI, GinGonic, ...), which may itself have specific
   client implementations to compare (e.g. FastAPI async vs. FastAPI sync, GinGonic vs. GinGonic w/
   channels).
3. **Test category** — read or write.
4. **Test type** — sequential read, complex joins read, bulk write, ... each with its own configuration
   knobs: dataset size profile (`tiny`, `small`, `large` — see `src/sandbox/api/db/seed/profiles.yaml`),
   environment resources, repetitions, etc.
5. **Load type** — the shape of the request-arrival pattern applied during the test.
6. **DB engine** — PostgreSQL only for now, but this is meant to become a knob like the rest.