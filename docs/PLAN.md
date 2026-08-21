# Plano — API Throughput & Telemetry Lab

Monorepo para estudar arquiteturas de API REST sob carga, com medição rigorosa de
throughput, latência, IOPS e custo de telemetria. Quatro implementações: Go,
TypeScript, Java e Python.

**Decisões de rumo (fixadas):**

| Decisão | Escolha |
|---|---|
| Eixo do estudo | Ambos, em fases: baseline idêntico nas 4 linguagens → depois matriz de variantes arquiteturais |
| Workload | IO-bound sobre Postgres (pool de conexões como variável central) |
| Telemetria | OTel completo (métricas + traces) → Collector → Prometheus + Tempo + Grafana |
| Execução | Docker Compose, uma API por vez, limites de CPU/memória idênticos |

---

## 1. A tese do projeto

A pergunta que o repo precisa responder com dados, não com opinião:

> Dado o *mesmo* contrato, o *mesmo* SQL e o *mesmo* orçamento de CPU/RAM, quanto
> da diferença de performance vem do **runtime** (GC, modelo de concorrência, JIT)
> e quanto vem da **arquitetura** (pool, N+1, backpressure, cache)?

A hipótese de trabalho — que o projeto deve tentar refutar — é que em carga
IO-bound a arquitetura domina a linguagem em uma ou duas ordens de grandeza, e
que a linguagem só passa a importar quando a arquitetura já está correta.

Isso define o critério de sucesso: **todo número precisa vir acompanhado da razão**
(profile de CPU, tempo de espera no pool, `pg_stat_statements`), senão é folclore.

---

## 2. Regras de justiça (o que faz ou quebra um benchmark de linguagens)

Uma implementação que viola qualquer uma delas não é
elegível para a tabela comparativa.

1. **Contrato único.** `api/openapi.yaml` é a fonte da verdade. Mesmo shape de
   JSON, mesmo formato de data (RFC 3339, UTC), mesmo envelope de erro
   (RFC 9457 `application/problem+json`), mesmos códigos de status.
2. **SQL literalmente idêntico.** Queries ficam em `db/sql/*.sql` e são carregadas
   por todas as impls. **Sem ORM no baseline** — ORMs geram SQL diferente e
   contaminam a comparação. ORM vira um eixo explícito na Fase 2.
3. **Mesmos knobs.** Pool size, timeouts, keep-alive, tamanho de body, workers —
   declarados em `bench/profiles/*.env`, aplicados por env var em todas as impls.
4. **Mesmo orçamento.** `cpus: 2.0`, `mem_limit: 512m`, `cpuset` fixo. Mesma
   classe de imagem base. Sem exceções "porque a JVM precisa de mais".
5. **Warmup obrigatório e excluído da medição.** JVM e V8 precisam; Go e Python
   quase não. O custo do warmup é reportado como métrica própria, não escondido.
6. **Carga em modelo aberto** (taxa de chegada constante), nunca modelo fechado —
   ver §5. Modelo fechado esconde saturação por omissão coordenada.
7. **Gerador nunca é o gargalo.** Endpoint `/noop` (resposta estática) estabelece
   o teto do harness. Se o RPS medido chega a 70% do teto do `/noop`, o resultado
   é inválido.
8. **N ≥ 5 execuções.** Reporta-se mediana e IQR. Run único é anedota.
9. **Estado inicial idêntico.** Restaurar snapshot do Postgres + `VACUUM ANALYZE`
   antes de cada run. Sem isso, a ordem dos testes vira variável escondida.

---

## 3. Domínio e superfície da API

Domínio deliberadamente banal (catálogo + pedidos) para que toda a atenção fique
na arquitetura. O que importa é que ele cobre os quatro padrões de acesso a disco
que interessam.

```
categories(id, name)
products(id, sku, name, price_cents, stock, category_id, attrs jsonb, created_at)
customers(id, email, name, created_at)
orders(id, customer_id, status, total_cents, idempotency_key, created_at)
order_items(order_id, product_id, qty, unit_price_cents)
```

| Endpoint | Padrão de acesso | O que expõe |
|---|---|---|
| `GET /v1/products/{id}` | point read por PK | Latência-piso, custo de serialização, cache |
| `GET /v1/products?cursor=&limit=&q=` | range scan + keyset pagination | Uso de índice, custo de resultset grande, backpressure de escrita no socket |
| `GET /v1/orders/{id}` | join agregado (order + items + products) | **N+1 vs join único** — o experimento mais didático do repo |
| `GET /v1/customers/{id}/orders` | join + paginação | Combinação realista |
| `POST /v1/orders` | transação: `SELECT … FOR UPDATE` + decremento de estoque + insert | Contenção de linha, deadlock, idempotência |
| `GET /noop` | nenhum | Calibração do gerador de carga |
| `GET /healthz`, `/readyz`, `/metrics` | — | Operacional |

Dataset determinístico: seed fixo, ~500k produtos, ~200k clientes, ~2M pedidos.
Grande o bastante para não caber em `shared_buffers` — senão não há IOPS para medir.
Um perfil `small` (tudo em cache) e um `large` (não cabe) são eixos de estudo por si só:
a diferença entre os dois **é** a medida de IOPS real.

---

## 4. Stack por linguagem

Baseline = a escolha idiomática e sem mágica. Variantes entram na Fase 2.

| | Baseline | Driver | Variantes da Fase 2 |
|---|---|---|---|
| **Go 1.25** | `net/http` (roteamento nativo 1.22+) | `pgx/v5` + `pgxpool` | chi, Gin, Fiber/fasthttp; `sqlc`; `GOGC`/`GOMEMLIMIT` sweep |
| **TypeScript** | Node 22 + Fastify | `postgres.js` | Express; `node:cluster` vs processo único; Bun; Deno; `--max-semi-space-size` |
| **Java 25** | Spring Boot MVC sobre **virtual threads** | JDBC + HikariCP | Quarkus; Helidon SE; Javalin; WebFlux reativo; **GraalVM native-image**; ZGC vs G1 |
| **Python 3.14** | FastAPI + uvicorn | `asyncpg` | Litestar; Granian; Flask sync + gunicorn threads; **build free-threaded (sem GIL)** |

Os dois itens mais interessantes da tabela inteira:

- **Java: JIT vs native-image.** Curva de p99 desde t=0 e RSS em regime. É a
  demonstração mais limpa de que "throughput em regime" e "custo de startup" são
  métricas ortogonais — e por que a resposta muda entre um pod de longa duração e
  um autoscaler agressivo.
- **Python 3.14 free-threaded.** Comparar GIL vs no-GIL no *mesmo* código, com
  `asyncpg` async e com driver sync + threads. É o experimento mais atual que este
  repo pode oferecer, e ninguém tem número bom sobre isso ainda em carga IO-bound real.

---

## 5. Metodologia de carga

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

## 6. O que medir

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

---

## 8. Estrutura do repo

```
.claude/
   skills/              Skills Claude p/ construção de uma API
   agents/              Agentes construtores de APIs (Subagentes de effort/model mais fracos, que seguem specs)
api/                    openapi.yaml, exemplos, schemas de erro
db/
  migrations/           versionadas, aplicadas por todas as impls
  sql/                  queries compartilhadas (a mesma string SQL para todos)
  seed/                 gerador determinístico + snapshot
conformance/            suite que valida qualquer impl contra o contrato
src/{go,typescript,java,python}/api/
bench/
  scenarios/            scripts k6
  profiles/             baseline.env, large.env, no-telemetry.env
  matrix.yaml           grade completa de execuções
  runner/               orquestração + coleta de resultados
deploy/
  compose.yaml          base: postgres, observabilidade
  compose.<impl>.yaml   perfis por implementação
observability/
  collector/            config do OTel Collector
  prometheus/           config + regras de recording
  grafana/              dashboards como código
  tempo/
results/                JSON bruto + relatórios, versionados
specs/                  Especificações da construção
src/                    Codigo da aplicação (APIs & webapp futuramente)
   /go
      /http
         /v1
         /v2
         ... Nível das estratégias
      /gin
      ... Nivel dos frameworks
   /python
   ... Nível das linguagens
docs/
  PLAN.md               este arquivo
  adr/                  decisões de arquitetura
  findings/             um markdown por experimento, com gráfico e conclusão
Makefile
```

**Contrato do harness** — toda impl deve honrar, e nada além disso:

```
make bench IMPL=go SCENARIO=mixed PROFILE=baseline RUNS=5
```

Sequência: sobe infra → restaura snapshot → `VACUUM ANALYZE` → sobe *uma* API com
limites → aguarda `/readyz` → warmup → calibra contra `/noop` → executa k6 →
coleta k6 + Prometheus + `pg_stat_*` → derruba → grava
`results/<data>-<impl>-<scenario>-<run>.json`.

Cada implementação expõe exatamente a mesma interface para o harness: um
`Dockerfile`, as mesmas env vars, `/readyz`, `/metrics`. Assim adicionar Rust,
C# ou Elixir depois custa um diretório, não uma refatoração.

---

## 9. Orçamento de recursos (12 cores / 7.6 GB)

A máquina é o principal limitador de validade. Alocação proposta:

| Componente | cpuset | Memória |
|---|---|---|
| API sob teste | 0-1 | 512 MB |
| Postgres | 2-5 | 1.5 GB |
| k6 | 6-9 | 512 MB |
| Collector + Prometheus + Tempo + Grafana | 10-11 | 1.2 GB |
| Folga do host | — | ~2 GB |

Regras que decorrem disso:

- **Uma API por vez.** Perfis do Compose garantem isso.
- Scrape do Prometheus a **1s** durante runs (runs são curtos; 15s perde a
  transiente). Retenção de 7 dias.
- Tempo com sampling baixo por padrão; 100% só no experimento de custo de telemetria.
- Grafana só sobe sob demanda (`make dash`); durante o run ele é peso morto.
- Fixar governor de CPU em `performance` antes dos runs. Variação de frequência é
  a fonte número um de ruído em bench local, e explica "regressões" fantasma.
- Registrar em cada resultado: temperatura/frequência, versão de kernel, uptime.
  Sem isso, comparar um run de hoje com um de mês que vem não é defensável.

Hoje só há ~1.6 GB livres. Antes do primeiro run é preciso liberar memória ou o
Postgres vai para swap e todos os números viram lixo — vale colocar essa checagem
no próprio harness, como precondição que aborta o run.

---

## 10. Fases

**Fase 0 — Fundação.** OpenAPI, migrations, SQL compartilhado, seed determinístico,
Compose com observabilidade, harness `make bench`, suite de conformidade. Uma única
implementação de referência (Go, por ser a de menor superfície) até o pipeline
inteiro rodar ponta a ponta e produzir um `results/*.json` válido.
*Saída: um gráfico de latência × throughput do Go.*

**Fase 1 — Paridade.** TypeScript, Java e Python passando a conformidade,
rodando os mesmos cenários. Primeiro relatório comparativo com as métricas
derivadas (req/s por core, req/s por MB) e experimentos 1–4.
*Saída: `docs/findings/01-baseline-4-languages.md`.*

**Fase 2 — Variantes arquiteturais.** A matriz: frameworks alternativos, ORM vs SQL,
native-image, free-threaded Python, cluster no Node, N+1 vs join, cache aside.
*Saída: a demonstração (ou refutação) da tese do §1.*

**Fase 3 — Comportamento sob estresse.** Experimentos 5–9: cancelamento,
backpressure, starvation, injeção de falha, idempotência. É aqui que o repo deixa
de ser um benchmark e vira um laboratório de arquitetura.

**Fase 4 — Automação.** Matriz noturna completa, gate de regressão em CI,
dashboard de resultados históricos.

---

## 11. Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Gerador de carga vira o gargalo | Calibração obrigatória contra `/noop` a cada run |
| Ruído do host domina o sinal | N≥5, mediana + IQR, governor fixo, metadados no resultado |
| Postgres vira o gargalo único e achata todas as linguagens | Perfil `small` (cache quente) para expor diferenças de runtime; perfil `large` para IOPS |
| Impls divergem sutilmente e a comparação perde sentido | Conformidade + fuzz de contrato (Schemathesis) como gate |
| Viés de familiaridade (a linguagem que eu conheço melhor ganha) | SQL e contrato idênticos por construção; revisão de cada impl contra um checklist de otimizações |
| Escopo explode na Fase 2 | `matrix.yaml` explícito; nada entra na matriz sem uma pergunta escrita antes |

---

## 12. Próximo passo concreto

Fase 0, na ordem: `api/openapi.yaml` → `db/migrations` + `db/sql` + seed
determinístico → `deploy/compose.yaml` com Postgres e OTel Collector →
Definição de specs de consturção de API.
Definição das specs CLAUDE.md, dos agentes e das specs condicionadoras de DDD (Orientação geral + de domínios)

OBS: Nada de primeira linguagem ate estipularmos skill + specs como API factory
OBS: Nada de segunda linguagem antes do pipeline fechar ponta a ponta.
