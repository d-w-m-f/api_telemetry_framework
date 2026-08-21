---
id: reference-domain/query-intents
versao: 1
contract_version: 1
aplica_se_a: todas
depende_de: [reference-domain/domain]
afeta_medicao: true
---

# Catálogo de IntençõesDeQuery

## Escopo

Define o conjunto fechado de operações de dados que uma implementação pode
executar. A **intenção** é o que é fixo: nome, parâmetros, cardinalidade, shape
de retorno e plano de acesso esperado. O SQL é realização por engine e vive em
`db/queries/<engine>/<nome>.sql`.

Não define o protocolo pelo qual a aplicação chama essas intenções — isso é
`specs/api/data-port.md`.

## Fixo

### Leitura

| Intenção | Parâmetros | Retorno | Plano esperado |
|---|---|---|---|
| `get_product_by_id` | `id` | 0..1 produto | Index Scan `products_pkey` |
| `list_products` | `category_id?`, `name_prefix?`, `cursor_created_at?`, `cursor_id?`, `limit` | 0..limit+1 produtos | Index Scan `idx_products_created_id` ou `idx_products_category_created` |
| `get_order_header` | `order_id` | 0..1 pedido | Index Scan `orders_pkey` |
| `list_order_items` | `order_id` | 1..N itens | Index Scan `order_items_pkey` |
| `list_order_items_with_product` | `order_id` | 1..N itens + `sku`, `name` | Index Scan + Nested Loop em `products_pkey` |
| `list_customer_orders` | `customer_id`, `cursor_created_at?`, `cursor_id?`, `limit` | 0..limit+1 resumos | Index Scan `idx_orders_customer_created` + agregação de `item_count` |
| `customer_exists` | `customer_id` | booleano | Index Only Scan `customers_pkey` |
| `find_order_by_idempotency_key` | `key` | 0..1 id de pedido | Index Scan `uq_orders_idempotency_key` |

**`limit + 1` é obrigatório** em toda paginação: busca-se uma linha a mais que o
`limit` para decidir `has_more` sem uma segunda query. Implementação que faz
`COUNT(*)` para isso está fazendo trabalho que nenhuma outra faz.

### Escrita — todas dentro de uma única transação

| Intenção | Parâmetros | Retorno |
|---|---|---|
| `lock_products_for_update` | `product_ids[]` | `id`, `price_cents`, `stock` |
| `insert_order` | `customer_id`, `status`, `total_cents`, `idempotency_key` | `order_id` |
| `insert_order_items` | `order_id`, linhas | — |
| `decrement_stock_batch` | linhas `(product_id, qty)` | linhas afetadas |

`lock_products_for_update` é `SELECT … FOR UPDATE` com **`ORDER BY id ASC`
obrigatório** — é a realização do invariante 7 de `domain.md`. Sem ordenação
determinística, a taxa de deadlock no cenário `write_contended` passa a depender
do escalonador e você mede sorte, não sujeito.

`insert_order_items` e `decrement_stock_batch` são operações **em lote**, uma
ida ao banco cada. Fazer N idas é uma estratégia com nome próprio (`n-mais-1`),
não uma liberdade de implementação.

### Realização

- Dentro de um mesmo engine, o SQL de uma intenção é **byte a byte idêntico**
  para as quatro linguagens. É aqui que a regra de justiça do PLAN §2.2 se
  materializa depois da mudança para intenções nomeadas.
- Toda intenção ativa tem realização em todo engine ativo. Engine sem cobertura
  total não é elegível para a tabela comparativa.
- Parâmetros são sempre posicionais e vinculados pelo driver. String
  interpolada em SQL é reprovação automática na conformidade.

### Índices que o plano esperado pressupõe

```sql
products_pkey (id)
idx_products_created_id      (created_at DESC, id DESC)
idx_products_category_created(category_id, created_at DESC, id DESC)
idx_products_name_prefix     (lower(name) text_pattern_ops)
uq_products_sku              (sku)
customers_pkey (id)          uq_customers_email (email)
orders_pkey (id)             uq_orders_idempotency_key (idempotency_key)
idx_orders_customer_created  (customer_id, created_at DESC, id DESC)
order_items_pkey (order_id, product_id)
```

Busca por `q` é prefixo sobre `lower(name)`, casando com
`idx_products_name_prefix`. `ILIKE` sem `lower()` no índice faz Seq Scan e o
resultado do cenário `read_heavy` deixa de significar qualquer coisa.

## Livre

- Nomes dos métodos gerados na linguagem, desde que mapeiem 1:1 para as
  intenções e mantenham o vocabulário de `general.md §4`.
- Como o resultado é materializado: struct, dict, tupla, cursor de streaming.
- Se a implementação faz prepared statement explícito ou deixa para o driver —
  **desde que seja a mesma decisão em todas as intenções**, registrada no
  `impl.yaml`.

## Fronteiras

- `specs/strategies/n-mais-1.md` é a única estratégia autorizada a usar
  `list_order_items` seguido de N × `get_product_by_id`. As demais usam
  `list_order_items_with_product`.
- `specs/strategies/cache-aside.md` pode evitar `get_product_by_id`, jamais
  substituí-lo por outra query.
- Adicionar intenção nova é mudança de `contract_version`: muda o trabalho que o
  banco faz, logo muda o sujeito medido.

## Aceite

`make conformance IMPL=<id>` — bloco `data`. Para cada intenção: `EXPLAIN` da
realização vigente e asserção do tipo de nó esperado, mais contagem de idas ao
banco por rota, capturada via `pg_stat_statements` durante a suíte. Uma rota que
dispara mais queries que a estratégia declara é reprovação.
