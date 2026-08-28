---
id: api/knobs
versao: 1
aplica_se_a: todas
depende_de: []
afeta_medicao: true
---

# Knobs

## Escopo

A lista fechada de variáveis de ambiente que configuram um sujeito, com
semântica exata. Toda variação de execução que não gera código novo passa por
aqui — ver `specs/README.md`, "vira diretório vs. vira knob".

## Fixo

### A regra que salva os runs

> **Knob desconhecido ou não implementado é falha de inicialização.**

Se o processo recebe uma variável `LAB_*` que ele não implementa, ele **não
sobe**: escreve o nome da variável em stderr e sai com código 78. Se falta uma
variável obrigatória, mesmo comportamento.

Sem isso existe a falha mais insidiosa possível: um run onde `LAB_POOL_SIZE=32`
foi passado, silenciosamente ignorado pela implementação, e o número foi para a
tabela como se o pool fosse 32. Nenhum log acusa, nenhum teste falha, e o
resultado é indefensável para sempre. Falhar ruidosamente na largada é barato;
descobrir seis meses depois não é.

### Catálogo

| Variável | Tipo | Default | Semântica |
|---|---|---|---|
| `LAB_SERVICE_NAME` | string | — obrigatória | Identidade `<lang>/<fw>/<estratégia>`. Vira `service.name` no OTel. |
| `LAB_PORT` | int | `8080` | Porta HTTP. |
| `LAB_DB_ENGINE` | enum | — obrigatória | `postgres`. Seleciona o adapter e o diretório de realizações. |
| `LAB_DB_DSN` | string | — obrigatória | Conexão. Nunca contém parâmetros de pool. |
| `LAB_POOL_SIZE` | int | — obrigatória | Tamanho **fixo** do pool: mínimo = máximo. |
| `LAB_POOL_ACQUIRE_TIMEOUT_MS` | int | `1000` | Espera máxima por conexão. Estourar é 503 `urn:lab:not-ready`. |
| `LAB_STATEMENT_TIMEOUT_MS` | int | `5000` | Timeout por statement, aplicado no servidor de banco. |
| `LAB_HTTP_READ_TIMEOUT_MS` | int | `5000` | Leitura de requisição. |
| `LAB_HTTP_WRITE_TIMEOUT_MS` | int | `10000` | Escrita de resposta. |
| `LAB_HTTP_IDLE_TIMEOUT_MS` | int | `60000` | Keep-alive ocioso. |
| `LAB_WORKERS` | int | `1` | Processos ou workers de aceitação. `1` = processo único. Semântica por linguagem em `specs/languages/`. |
| `LAB_TELEMETRY_LEVEL` | enum | `metrics` | `off` \| `metrics` \| `traces`. |
| `LAB_TRACE_SAMPLE_RATIO` | float | `0.0` | 0..1. Só tem efeito com `traces`. |
| `LAB_OTLP_ENDPOINT` | string | — | Collector. Obrigatória quando o nível não é `off`. |
| `LAB_SHED_ENABLED` | bool | `false` | Liga load shedding. Capacidade opcional. |
| `LAB_SHED_QUEUE_MAX` | int | `0` | Profundidade máxima de fila antes de 503. |
| `LAB_LOG_LEVEL` | enum | `warn` | `warn` \| `error`. `info` e `debug` são proibidos sob carga. |

### Pool é de tamanho fixo

Mínimo igual ao máximo, e **totalmente aberto antes de `/readyz` retornar 200**.
Pool que cresce sob demanda transforma o início da janela de medição num
transiente de abertura de conexão que aparece como cauda de latência e varia por
driver. O sweep de pool do PLAN §7.1 só significa alguma coisa se o número
declarado for o número em uso desde o primeiro request medido.

### Log sob carga

`warn` é o teto. Log por requisição é proibido em qualquer nível: uma linha por
request a 5.000 req/s é um segundo workload rodando junto, com custo de
formatação e de I/O radicalmente diferente entre runtimes. Quem quiser medir
custo de logging escreve uma estratégia para isso.

## Livre

- Como a variável é lida e validada.
- Nome do campo interno que a guarda.
- Valores adicionais **não**: o catálogo é fechado. Precisa de knob novo? Ele
  entra nesta spec com bump de versão, não no `.env` de um experimento.

## Fronteiras

- `specs/api/harness-contract.md` define quando as variáveis são lidas (na
  largada, nunca em runtime) e o que acontece na falha.
- `specs/languages/<lang>.md` traduz `LAB_WORKERS` para o conceito da linguagem.
- `bench/profiles/*.env` são conjuntos nomeados de valores destes knobs.

## Aceite

`make conformance IMPL=<id>` — bloco `knobs`. Sobe o container com uma variável
`LAB_BOGUS_KNOB=1` e exige exit 78; sobe sem `LAB_POOL_SIZE` e exige exit 78;
sobe normalmente e confere via `/metrics` que `db.client.connection.count` soma
exatamente `LAB_POOL_SIZE` antes do primeiro request.
