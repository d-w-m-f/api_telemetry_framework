Append this to whatever CLAUDE.md structure you find fitting to write:

- This is a monorepo of a telemetry framework project
- On all 'sensible products' of this codebase, utilize local env var injection. Always utilize .env, .env.local and .env.prod templates. Always utilize env var ENVIRONMENT='local' or 'prod'. A 'sensible product' is something that would be affect in some way by environment differece (examples: the main frontend and backend)
- All code, comments and communication shall be in English
- Put a directory structure guide on claude.md on the following format example:

```text
docs/
docker/
src/
...
.gitignore
...
```

- The frontend stack App is Angular
- The backend stack App is Python + FastAPI 

- The project architecture can be understood by interpreting General_Architecture.png. Also, you can consider the following:

We have a frontend (Angular) and a backend (SpringBoot). This backend is also refered as the 'normal' backend, or rarelly as the 'main' backend. 

The normal backend also connects to a database layer using PostgreSQL. That is called the main database.

The frontend gets ehxibition data from the backend on a common client-server model.

The frontend also generates telemetry-test payloads to the backend. These are queued to a RabbitMQ broker and are processed asynchronously on a sandbox environment.

We utilize RabbitMQ as a broker, with two direct exchanges:
- TelemetryTest: for receiving the telemetry tasks
- DLQ: for aggregating tasks that fail/can't be processed by some reason

Note: The RabbitMQ AND worker must be both configured to garantee at-least-once processing. 
Note: For not letting the same task be processed twice, at enqueueing, a row with the event must be registered with a serial id, the json event, and a status. This status shall be atualized only on completion (so its a bool is_completed, false meaning everything thats not completed [waiting, dlq, retry, processing, etc]).

To consume telemetry events, we put a python consumer hearing to the TelemetryTest queue. This python consumer than has the following responsabilities:
- To spin the correct sandbox environment accordingly to the event payload. 
Importantly, since this is a monorepo, it needs to not bloat the image with all other apis from other languages or the same language)
Also, the doing of it is still a challenge to solve
- To monitor and collect the 
- During telemetry collection and after completion, saving temporal and general state to the main database
- In case of error, saving it to the main database and enqueueing task to DLQ

For now, we will be limiting only one consumer on the TelemetryTest queue.

The Sandbox environment by itself is composed of three separate layers:
1) Database layer: Where we spin the DB engine that is going to receive the load. For now, only PostgreSQL. This is called a sandbox database.
2) API/Application Layer: The proper API microsservice(s) that are beeing testes and metrified. This is called a sandbox application
3) Request/Telemetry Container: The container that is going to conduct the testing processes - so, possibly seeding/warming the sandbox database, firing requests, collecting telemetry, returning data somehow to the consumer. This is written in GoLang with as few dependencies as possible.


- the complete list of test/comparison criteria supported by this framework is the following:

1. Language: Python, Java, Go, ...
2. HTTP client: FastAPI, GinGonic
    2.1 Specific client implementations: FastAPI async, FastAPI sync, GinGonic w/ channels
3. Test category: Read Or Write
4. Test type: Sequential read, complex joins read, bulk write
    4.1: Test configurations: Category size (small, medium, big, extreme), environment resources, repetitions, etc...
5. Load type
6. DB Engine (For now postgreSQL only, but it will be a knob)