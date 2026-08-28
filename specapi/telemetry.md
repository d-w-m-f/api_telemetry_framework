---
id: api/telemetry
versao: 1
aplica_se_a: todas
depende_de: [api/knobs]
afeta_medicao: true
---

# Telemetria

## Escopo

Nomes de métricas, atributos, fronteiras de bucket, spans e o que
deliberadamente **não** se instrumenta. Telemetria aqui é ferramenta e sujeito
ao mesmo tempo: `LAB_TELEMETRY_LEVEL` é knob do `Experimento`, e o experimento 3
do PLAN mede quanto ela custa.

## Fixo

### As fronteiras de bucket são idênticas em todas as linguagens

```
0.001 0.0025 0.005 0.01 0.025 0.05 0.075 0.1 0.25 0.5 0.75 1 2.5 5 10
```

Em segundos, para todo histograma de duração. Esta é a armadilha mais silenciosa
do projeto: cada SDK do OpenTelemetry traz buckets default diferentes, e p99
extraído de histograma é **interpolado dentro do bucket**. Buckets diferentes
produzem p99 diferentes para latências idênticas. Você compararia a granularidade
dos histogramas achando que compara os runtimes.

Isso vale para os histogramas de servidor. O k6 mantém a distribuição completa do
lado do cliente e não sofre do problema — mais uma razão para o delta
cliente-servidor ser lido com atenção, e não como erro de medição.

### Métricas

| Nome | Tipo | Atributos |
|---|---|---|
| `http.server.request.duration` | histograma (s) | `http.route`, `http.request.method`, `http.response.status_code` |
| `http.server.active_requests` | updown counter | `http.route` |
| `db.client.operation.duration` | histograma (s) | `db.operation.name` (nome da intenção) |
| `db.client.connection.wait_time` | histograma (s) | — |
| `db.client.connection.count` | updown counter | `state` = `used` \| `idle` |
| `lab.runtime.concurrency` | gauge | `kind` = `goroutine` \| `thread` \| `task` \| `eventloop` |
| `lab.runtime.scheduler_lag` | histograma (s) | — |
| `lab.runtime.gc.pause` | histograma (s) | — |
| `lab.runtime.memory.rss` | gauge (bytes) | — |
| `lab.shed.total` | counter | `reason` |
| `lab.work.wasted` | counter | `http.route` |

`http.route` é o padrão da rota, nunca o caminho concreto: `/v1/products/{id}`,
jamais `/v1/products/8123`. Cardinalidade explosiva de label mataria o Prometheus
no meio do run e o custo disso apareceria como latência do sujeito.

`db.client.connection.wait_time` não é padrão do OpenTelemetry, e é a métrica
mais importante da lista. Em carga IO-bound ela costuma explicar a maior parte da
latência — é ela que transforma "o Java ficou lento" em "o pool estava
estrangulado", que é a diferença entre um número e um achado.

`lab.runtime.concurrency` mede o análogo do runtime: goroutines em Go, threads
vivas em Java, tasks em Python, handles ativos no event loop em Node. O atributo
`kind` declara o que está sendo contado, porque as grandezas não são
intercambiáveis.

### Spans, quando o nível é `traces`

Um span por requisição HTTP, nome igual a `<método> <rota>`. Um span filho por
chamada ao DataPort, nome igual à intenção.

Proibido: span por linha de resultado, span por etapa interna de serialização,
span por camada de arquitetura. Uma requisição do baseline produz no máximo 3
spans; `n-mais-1` produz `2 + N`, e essa diferença é o resultado do experimento,
não ruído de instrumentação.

Amostragem por `LAB_TRACE_SAMPLE_RATIO`, decidida na raiz e propagada.

### Atributos de recurso

`service.name` = `LAB_SERVICE_NAME`. Além disso, obrigatórios:
`lab.language`, `lab.framework`, `lab.strategy`, `lab.contract_version`,
`lab.runtime_version`. São eles que permitem à análise fatiar resultados sem
depender de convenção de nome de arquivo.

### O que não se instrumenta

- **Nenhum log por requisição**, em nenhum nível — ver `api/knobs.md`.
- Nenhuma métrica de negócio (pedidos criados, valor total). Não serve à
  pergunta do projeto e adiciona trabalho desigual.
- Nenhum exporter além do OTLP configurado. Sem push para serviço externo, sem
  telemetria de vendor embutida no framework — Spring Actuator e similares
  ficam desligados, porque coletam coisas que os outros não coletam.

### Nível `off` é desligado de verdade

Com `LAB_TELEMETRY_LEVEL=off` o SDK não é inicializado, nenhum middleware de
instrumentação entra na cadeia, e `/metrics` responde 200 com corpo vazio. Não
basta parar de exportar: o experimento 3 mede o custo de *instrumentar*, não o
custo de *transmitir*. Um `off` que ainda mede e descarta mediria a coisa errada.

## Livre

- Uso do SDK do OpenTelemetry ou instrumentação manual, desde que os nomes,
  atributos e buckets sejam exatamente estes.
- Instrumentação automática do framework, desde que ela seja podada até restar
  apenas o que está nesta tabela.

## Fronteiras

- `api/knobs.md` é dono de `LAB_TELEMETRY_LEVEL`, `LAB_TRACE_SAMPLE_RATIO` e
  `LAB_OTLP_ENDPOINT`.
- `api/data-port.md` é dono de onde `db.client.*` é emitida.
- O contexto Telemetria do laboratório é dono do Collector e do backend; nada
  disso é conhecido pelo sujeito além do endpoint OTLP.

## Aceite

`make conformance IMPL=<id>` — bloco `telemetry`. Compara o dump de `/metrics`
contra a lista canônica: nome faltando reprova, nome sobrando reprova, fronteira
de bucket divergente reprova. Com `off`, exige `/metrics` vazio e ausência do
processo exportador.
