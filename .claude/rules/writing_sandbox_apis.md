# Writing Sandbox APIs rules

This is a guide on how to write Sandbox APIs. Sandbox APIs are APIs that live inside `src/sandbox/api/src/`,
one directory per language (e.g. `src/sandbox/api/src/python/`) — see the root `CLAUDE.md` directory
structure guide.

When writing Sandbox APIs, adhere to the following standards:

1. To better understand coding standards and project structure, always read the rules for both the language
   AND the HTTP framework you are using.

   For example, if you are writing a sandbox API at:

   `src/sandbox/api/src/python/`

   using FastAPI, you should read:
   - `fastapi.md`
   - `python.md`

   A single language directory can contain multiple HTTP-client variants (e.g. FastAPI async and FastAPI
   sync) selected by a factory at the app entrypoint, rather than one directory per variant — see `fastapi.md`
   §2 for the pattern.

2. Don't consider test writing and unit test coverage as metrics for evaluating functional development. The
   correctness of the contracts should be evaluated by telemetry flux integration.
