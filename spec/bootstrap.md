# MVP

THis is the specification for writing our working MVP on this project. Here we map what we want, what is the goal of this first batch of agentic programming, and some challanges and open questions we still have to answer.

## What I want:

The first product will be a minimal function e2e completed version of the framework. For that, we will have:

- A single frontend page, to select the running test

- A backend endpoint for receiving the payload, and enqueueing it.

- A local infrastructure with rabbitmq and postgresql for the broker and the normal database.

- A telemetry worker, capable on listening on the telemetry queue, capturing a task, spinning a sandbox environment, collecting telemetry data and saving to main database

- A working sandbox environment, capable of spinning the needed infrastructure and running the loaded test.

- Observability on the sandbox environment, for understanding, monitoring and debuggind.


A sucess will be a complete end to end application, successfully running this pipeline for:
- A python+fastAPI API
- On a read test
- On a simple-test type (just reading 100 lines)
- running e2e successfully, writting it on the normal database, and beeing consumed by the frontend

Also, We want:
- Local infra env with docker-compose
- .claude/rules for writting Angular, Typescript, Python and FastAPI code

## MVP decisions (resolved 2026-09-16)

- **Sandbox spin-up**: each language/framework/DB combination has its own docker-compose file (under its
  sandbox dir) bringing up all 3 layers (sandbox db + sandbox api + `load_n_telemetry`). The Python consumer
  shells out to `docker compose -f <file> up`, blocking for the sandbox's full lifetime — the consumer's own
  liveness during that call is the monitoring mechanism, no separate polling loop needed.
- **Result handoff**: the backend mints the run UUID at enqueue time (not the consumer — required for
  `is_completed` to work as a RabbitMQ redelivery guard, see the root `CLAUDE.md` architecture section) and
  carries it in the message payload. The consumer reuses that same UUID: it inserts a pending row into
  `telemetry_results` (main DB) keyed by it, and injects the UUID plus main-DB connection info into the
  sandbox via env vars. `load_n_telemetry` connects directly to the main DB and writes the finished results
  into that row itself. This means `load_n_telemetry` needs a Postgres client dependency (still no HTTP
  framework, per `.claude/rules/go.md`). If the sandbox exits non-zero, times out, or otherwise never
  completes, the consumer detects that from the process exit and writes the failure state + enqueues to
  `DLQ` itself, since a dead container can't report its own failure.
- **Sandbox API contracts**: defined as OpenAPI specs, one per test type, under `spec/contracts/` (MVP needs
  just one: the "simple read, 100 rows" contract). Every language's sandbox implementation must match it;
  each framework's own typed-schema layer (Pydantic schemas, Go structs, Java DTOs) is written to satisfy
  the spec, not the other way around.
- **Main DB MVP schema**: minimal — `telemetry_runs` (id uuid pk, payload jsonb, `is_completed` bool,
  timestamps, error info) for the RabbitMQ at-least-once dedup guarantee described in the root `CLAUDE.md`,
  plus `telemetry_results` (run_id uuid fk, metrics jsonb, completed_at) for the collected telemetry. No
  config/catalog tables yet — those get added once the frontend actually needs to query them relationally.
- **TypeScript package manager**: npm (Angular CLI default), for both the frontend and any future TypeScript
  sandbox API.
- **Frontend MVP scope**: one page — select the test (fixed to the single MVP combination for now), submit,
  poll run status, and render the finished `telemetry_results` row as a raw table/JSON once complete. No
  charts yet.
- **Sandbox observability (MVP)**: no in-app instrumentation, per `fastapi.md`/`gingonic.md`/`springboot.md`
  §6 ("no built-in OTel"). MVP observability is structured stdout logging in every sandbox container
  (inspectable via `docker compose logs`) plus the client-side latency/error telemetry `load_n_telemetry`
  collects and persists as the `telemetry_results` row. The Prometheus/cAdvisor/OTel-cost experiments in the
  Brainstorm section below remain explicitly out of scope for MVP.
- **Java package manager**: Maven — already settled in `.claude/rules/java.md`.
- **Sandbox database layer**: the reference-domain schema under `src/sandbox/api/db/migrations/` is shared
  across every language's sandbox API (one canonical schema/dataset, not one per language) — each
  implementation's persistence layer just points its ORM/driver at it.




## Brainstorm

Things extracted from an older try of implementation of this protect. Good to document and have a north after the MVP, but it does not come into play right now.

### 5. Metodologia de carga

**Modelo aberto, sempre.** k6 com executor `constant-arrival-rate`: injeta X req/s
independentemente de o servidor responder. Modelo fechado (N VUs em loop) mede o
servidor *e* se auto-limita quando o servidor engasga — o clássico problema de
**omissão coordenada**, que faz p99 parecer ótimo exatamente quando o sistema está
morrendo.

**Não medir "RPS máximo". Medir a joelhada.** O protocolo:

1. Rampa de taxa de chegada: 100 → 200 → 400 → 800 → … req/s, degraus de 60s.
2. Para cada degrau: p50/p95/p99/p99.9, taxa de erro, saturação.
3. **Max Sustainable Throughput** = maior degrau onde `p99 < SLO` e `erro < 0.1%`,
   sustentado por 5 minutos.
4. Plotar latência × throughput. A joelhada da curva é o resultado, não o pico.

**Cenários:**

| Cenário | Mix | Objetivo |
|---|---|---|
| `read_point` | 100% `GET /products/{id}` | Piso de latência |
| `read_heavy` | 80% list + 20% point | Padrão realista de leitura |
| `mixed` | 70% leitura, 25% order read, 5% `POST /orders` | Referência principal |
| `write_contended` | `POST /orders` sobre 50 SKUs quentes | Contenção de linha, deadlock |
| `slow_tail` | `mixed` + 1% de queries com `pg_sleep(2)` | **Head-of-line blocking / starvation de pool** |
| `burst` | 2× a capacidade conhecida, por 30s | Degradação graciosa vs colapso |

---

### 6. O que medir

Três camadas, correlacionadas por `trace_id`.

**Cliente (k6)** — a verdade sobre o usuário:
p50/p95/p99/p99.9/max, taxa de erro, taxa de chegada real vs pretendida.
Média é proibida no relatório.

**Servidor (OTel)** — RED + o que explica o RED:
- `http.server.duration` (histograma, por rota e status)
- `db.client.operation.duration` e **`db.client.connection.wait_time`**
- Runtime: heap/RSS, pausas e frequência de GC, taxa de alocação, goroutines /
  threads / tasks vivas, **event loop lag** (Node), tempo em GIL (Python)
- Delta entre latência do cliente e latência do servidor = **tempo em fila no accept
  queue**. Essa diferença costuma ser a descoberta mais interessante de todo o exercício.

**Postgres e disco** — o "IOPS" do nome do repo:
- `pg_stat_statements`: `calls`, `mean_exec_time`, `rows`, `shared_blks_read` vs `shared_blks_hit`
- `pg_stat_database`: `xact_commit`, `blks_read`, `tup_returned/tup_fetched`
- `pg_stat_activity`: contagem de conexões por estado (`active`/`idle in transaction`)
- blkio do container via cAdvisor → IOPS e bytes/s reais no device
- **Buffer cache hit ratio** — a variável que separa o perfil `small` do `large`

**Métricas derivadas** (a parte que torna a comparação honesta entre linguagens):
- `req/s por core-segundo de CPU` — normaliza runtimes que simplesmente usam mais CPU
- `req/s por MB de RSS` — densidade, o que de fato decide custo em produção
- `trabalho desperdiçado`: fração de queries concluídas depois que o cliente já desistiu
- Joules por request via RAPL (`/sys/class/powercap`), se acessível

---

## 7. Experimentos que valem a pena implementar

Ordenados por razão insight/esforço.

1. **Sweep de pool de conexões.** Pool 1→64 × taxa de chegada. Plotar throughput e
   `connection.wait_time`. Ajustar a **Universal Scalability Law** aos pontos e
   extrair os coeficientes de contenção (α) e coerência (β) por linguagem. Mostra
   que existe um ótimo, que ele é *pequeno*, e que passar dele piora — contrariando
   o instinto de "aumenta o pool".
2. **N+1 vs join.** `GET /orders/{id}` implementado das duas formas, nas 4
   linguagens. Aposta: o Python com join único ganha do Go com N+1. Se ganhar,
   a tese central do repo está demonstrada em um gráfico.
3. **Custo da observabilidade.** Mesma carga com: OTel off / só métricas /
   traces 1% / 10% / 100%. Quanto custa enxergar? A resposta varia brutalmente
   entre SDKs — o auto-instrumentation do Node é notoriamente caro.
4. **Perfil de warmup.** p99 em janelas de 5s desde t=0 até estabilizar. JVM JIT vs
   GraalVM native vs Go vs Node. Reportar "tempo até p99 estável" como métrica.
5. **Propagação de cancelamento.** Cliente desiste (timeout de 100ms) enquanto a
   query roda. A query no Postgres é cancelada? Medir com `pg_stat_activity`.
   `context.Context` (Go) vs `AbortSignal` (Node) vs interrupt de virtual thread
   (Java) vs `asyncio.CancelledError` (Python). Quase nenhum benchmark testa isso
   e é a diferença entre degradar e entrar em colapso sob timeout de cliente.
6. **Backpressure e load shedding.** Fila limitada + `503` com `Retry-After` ao
   encher. Rodar `burst` com e sem shedding. Quem degrada em platô e quem cai a pique?
7. **Starvation de pool** (`slow_tail`). 1% de queries lentas derruba os outros 99%?
   Mitigações a testar: pool separado por classe de query, timeout de statement,
   circuit breaker.
8. **Injeção de falha** com Toxiproxy entre API e Postgres: latência, jitter, reset
   de conexão, partição. Mede resiliência, não velocidade.
9. **Idempotência sob concorrência.** 100 `POST /orders` simultâneos com a mesma
   chave. Teste de *correção*, não de performance — e é onde implementações
   costumam divergir silenciosamente.
10. **Profiling contínuo** (Pyroscope ou Parca) ligado durante os runs, para que
    todo número tenha um flamegraph correspondente arquivado ao lado.
11. **Cache aside** (Redis) como variante da Fase 2 — muda o workload de IO-bound
    para CPU/rede-bound e reordena completamente o ranking. Bom para mostrar que
    "qual linguagem é mais rápida" é uma pergunta mal formulada.
12. **Gate de regressão em CI.** Perfil `smoke` (60s), compara com baseline
    versionado, falha se p99 piorar mais que a tolerância.
