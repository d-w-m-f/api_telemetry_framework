# Writing Sandbox APIs rules

This is a guide on how to write Sandbox APIs. Sandbox APIs are APIs that are inside 'src/sandbox/api/src'.

When writing Sandbox APIs, adhere to the following standarts:


1. To better understand coding standarts and project structure, always go read the claude rules on the language AND the http framework you are utilizing.

For example, if you are writting a sandbox api at:

`sandbox/api/src/python/fastapi`

You should lookup for claude rules:
- fastapi.md
- python.md


2. Don't consider test writing and unit test coverage as metrics for evaluating functional development. The correctness of the contracts should be evaluated by telemetry flux integration. 