---
id: api/data-port
versao: 1
aplica_se_a: todas
depende_de: [reference-domain/query-intents, api/knobs]
afeta_medicao: true
---

# DataPort

## Escopo

O protocolo pelo qual a aplicação fala com o Backend de Dados: um método por
`IntençãoDeQuery`, mais transação. Define também como o SQL chega ao processo,
como erros de engine viram erros de domínio e como cancelamento se propaga.

Não define o SQL (`reference-domain/query-intents.md`) nem onde o port é
instanciado dentro da aplicação (`specs/strategies/`).

## Fixo

### Forma do protocolo

Uma interface com **exatamente um método por intenção ativa**, nomeado igual à
intenção, mais:

```
transaction(fn) -> resultado de fn
```

Nenhum método aceita SQL como argumento. Nenhum método aceita nome de tabela,
coluna ou fragmento de query. Se a assinatura permite passar SQL, o port está
errado: a garantia de que todas as linguagens executam o mesmo texto deixa de
ser estrutural e vira disciplina.

### Factory por engine

```
create_data_port(engine, dsn, pool_config) -> DataPort
```

`engine` vem de `LAB_DB_ENGINE`. A aplicação depende da interface, jamais do
adapter concreto. Trocar Postgres por outro engine não toca nenhum handler.

### O SQL vem de arquivo, na largada

As realizações são lidas de `db/queries/<engine>/<intencao>.sql` durante a
inicialização e mantidas em memória. **SQL literal embutido no código-fonte é
reprovação automática na conformidade.**

É esse mecanismo que torna "byte a byte idêntico entre linguagens" uma
propriedade verificável em vez de uma promessa: as quatro implementações leem o
mesmo arquivo. Um `grep -r "SELECT" src/subjects/` que retorne resultado indica
que alguém quebrou a garantia.

### Statements parametrizados, sem prepare explícito

Parâmetros são sempre posicionais e vinculados pelo driver. Interpolação de
string em SQL é reprovação automática.

O baseline usa o mecanismo padrão de statement parametrizado do driver, **sem
prepare explícito nem cache manual de plano**. Se o driver cacheia por conta
própria, isso é propriedade do driver e vai registrada no `impl.yaml`. Cache
manual de plano é uma estratégia com nome próprio na Fase 2, não uma liberdade.

### Transação

`transaction(fn)` abre transação, executa `fn`, comita no retorno normal e faz
rollback em qualquer erro ou cancelamento. Nível de isolamento: `READ COMMITTED`
(o default do Postgres) — declarado explicitamente, não herdado por acaso.

Todas as intenções de escrita de `POST /v1/orders` rodam dentro de **uma única**
transação. Uma implementação que abre duas transações para criar um pedido está
fazendo trabalho que nenhuma outra faz.

### Mapeamento de erro

| Situação no engine | O que o port devolve | O que a API responde |
|---|---|---|
| Nenhuma linha | Retorno vazio / opcional ausente | 404 `urn:lab:not-found` |
| Timeout ao adquirir conexão | Erro de saturação | 503 `urn:lab:not-ready` |
| Timeout de statement | Erro de saturação | 503 `urn:lab:not-ready` |
| Violação da unique de `idempotency_key` | Erro de corrida | Re-leitura da chave e replay |
| Violação do CHECK de `stock >= 0` | Erro interno | 500 `urn:lab:internal` |

**Ausência de linha nunca é exceção.** Em linguagens onde o driver lança nesse
caso, o adapter converte. Usar exceção para controle de fluxo em caminho quente
tem custo abismalmente diferente entre runtimes — em Python é barato, em Java
com stack trace preenchido é caro — e mediria a máquina de exceções.

O CHECK de estoque é rede de segurança, não caminho normal. A aplicação valida
antes e devolve 409; se o CHECK dispara, a lógica está errada e a conformidade
reprova.

### Cancelamento

Todo método recebe o contexto de cancelamento da requisição e o propaga até o
driver. Cliente que desiste cancela a query em andamento no banco.

Isso é **obrigatório no baseline**, não opcional. O experimento 5 do PLAN não
mede se a propagação existe — mede quanto tempo cada runtime leva para a query
sumir de `pg_stat_activity` depois do abandono, o que varia enormemente mesmo
entre implementações todas corretas.

Requisição cancelada não conta como erro em `http.server.request.duration`; ela
alimenta o contador `lab.work.wasted` de `api/telemetry.md`.

## Livre

- Nome do tipo que implementa a interface e organização dos arquivos.
- Como as linhas viram estruturas na linguagem.
- Se o port é uma interface, um protocolo, um trait ou uma classe abstrata —
  decisão de `specs/languages/<lang>.md`.

## Fronteiras

- `reference-domain/query-intents.md` é dono do conjunto de métodos. Método que
  não corresponde a uma intenção não existe.
- `api/knobs.md` é dono do `pool_config`.
- `specs/strategies/cache-aside.md` pode evitar uma chamada ao port, nunca
  contorná-lo com SQL próprio.

## Aceite

`make conformance IMPL=<id>` — bloco `data-port`. Verifica: ausência de literal
SQL no fonte; um método por intenção, sem sobras; `POST /v1/orders` abre
exatamente uma transação (via `pg_stat_statements`); query cancelada some de
`pg_stat_activity` em até 1s após desconexão do cliente.
