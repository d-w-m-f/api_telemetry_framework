---
id: reference-domain/contract
versao: 1
contract_version: 1
aplica_se_a: todas
depende_de: [reference-domain/domain]
afeta_medicao: true
---

# Contrato HTTP

## Escopo

Define a superfície HTTP que toda implementação expõe: rotas, shapes, códigos,
cabeçalhos e o catálogo fechado de erros. O schema mecânico vive em
`api/openapi.yaml`; aqui ficam as **decisões normativas e as armadilhas**.

Não define como a rota é implementada nem quantas queries ela dispara — isso é
`specs/strategies/`.

## Fixo

### Rotas

| Método e rota | Sucesso | Erros possíveis |
|---|---|---|
| `GET /v1/products/{id}` | 200 `Product` | 404 |
| `GET /v1/products` | 200 `Page<Product>` | 400 |
| `GET /v1/orders/{id}` | 200 `OrderDetail` | 404 |
| `GET /v1/customers/{id}/orders` | 200 `Page<OrderSummary>` | 400, 404 |
| `POST /v1/orders` | 201 `OrderDetail` | 400, 404, 409 |
| `GET /noop` | 200 | — |
| `GET /healthz` | 200 | — |
| `GET /readyz` | 200 | 503 |
| `GET /metrics` | 200 texto Prometheus | — |

`GET /v1/products/{id}` retorna `category_id`, **não** o objeto categoria. É um
point read puro por chave primária — é o piso de latência do projeto, e um join
ali destruiria essa função. Todo join deliberado mora em `/v1/orders/{id}`.

`GET /noop` retorna exatamente os 11 bytes `{"ok":true}`, sem tocar o banco. Ele
estabelece o teto do harness; qualquer trabalho extra ali envenena a calibração
de todos os runs.

### Paginação por keyset

Ordenação fixa: `created_at DESC, id DESC`. Nunca `OFFSET`.

`limit` tem default 20 e máximo 100; acima disso é 400. `cursor` é
**base64url sem padding** de `<created_at_em_milissegundos>:<id>` — por exemplo
`1755785' + ...`, sempre a mesma codificação em toda linguagem. Cursor é opaco
para o cliente e **portável entre implementações**: um cursor emitido pelo Go
tem que funcionar no Python. Se não funciona, alguém inventou codificação
própria e a comparação de payload já está contaminada.

Resposta: `{"items":[...],"next_cursor":"...","has_more":true}`.
`next_cursor` é `null` quando `has_more` é `false`.

Filtros de `GET /v1/products`: `category_id` (opcional) e `q` (opcional, prefixo
de `name`, case-insensitive). Prefixo, não busca full-text — prefixo usa índice,
full-text arrastaria `tsvector` para dentro do baseline.

### Idempotência

`POST /v1/orders` exige o cabeçalho `Idempotency-Key` (1 a 128 caracteres).
Ausente é 400.

Replay da mesma chave com o **mesmo** corpo retorna `201` com corpo idêntico ao
original mais o cabeçalho `Idempotency-Replayed: true`. Repetir o status original
em vez de trocar para 200 evita que o cliente trate replay como caso especial —
e dá à conformidade um sinal binário para verificar.

Mesma chave com corpo **diferente** é 409 `urn:lab:idempotency-conflict`.

### Catálogo fechado de erros

Todo erro é `application/problem+json` (RFC 9457). `instance` é sempre o path da
requisição. `detail` segue o gabarito exato abaixo — não é texto livre.

| `type` | status | `title` | `detail` |
|---|---|---|---|
| `urn:lab:validation` | 400 | `Validation failed` | `field <nome> <razão>` |
| `urn:lab:not-found` | 404 | `Not found` | `<recurso> <id> does not exist` |
| `urn:lab:insufficient-stock` | 409 | `Insufficient stock` | `product <id> has <n> units, requested <m>` |
| `urn:lab:idempotency-conflict` | 409 | `Idempotency key conflict` | `key <chave> was used with a different request body` |
| `urn:lab:not-ready` | 503 | `Not ready` | `data backend unavailable` |
| `urn:lab:internal` | 500 | `Internal error` | `unexpected failure` |

Razões válidas de validação: `is required`, `must be an integer`,
`must be positive`, `exceeds maximum`.

Por que gabaritar `detail`: no cenário `write_contended` os 409 são a maioria do
tráfego. Mensagem de tamanho variável entre implementações vira diferença de
bytes no socket exatamente onde o experimento mede contenção.

### Cabeçalhos e transporte

- **Compressão desligada.** A implementação não emite `Content-Encoding` e ignora
  `Accept-Encoding`. Níveis e bibliotecas de gzip diferem brutalmente entre
  runtimes; ligar compressão mediria zlib.
- `Content-Type`: exatamente `application/json` no sucesso (sem `charset`) e
  `application/problem+json` no erro.
- **Proibidos:** `Server`, `X-Powered-By`, `ETag`, `Cache-Control`. Vários
  frameworks emitem por default; cada um adiciona bytes diferentes por resposta.
- HTTP/1.1 com keep-alive. HTTP/2 e HTTP/3 são eixos da Fase 2, não do baseline.
- Sem redirecionamento, sem negociação de conteúdo, sem CORS.

## Livre

- Roteador, middleware, forma de validação e de serialização.
- Ordem das chaves no JSON — não é verificada.
- Como o 404 é detectado (query separada ou ausência de linha).

## Fronteiras

- `specs/api/harness-contract.md` cobre `/healthz`, `/readyz`, `/metrics` do
  ponto de vista do laboratório; aqui eles constam apenas para a superfície ficar
  completa. Divergência: harness-contract vence.
- `specs/strategies/` decide quantas queries cada rota dispara. Uma estratégia
  pode mudar o número de queries; nunca o shape da resposta.

## Aceite

`make conformance IMPL=<id>` — blocos `contract` e `errors`. Inclui fuzz de
contrato (Schemathesis) contra `api/openapi.yaml` e um teste de portabilidade de
cursor: paginar iniciando numa implementação e continuar em outra.
