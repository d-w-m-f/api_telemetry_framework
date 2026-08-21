---
id: reference-domain/domain
versao: 1
contract_version: 1
aplica_se_a: todas
depende_de: []
afeta_medicao: true
---

# Domínio de Referência — entidades e invariantes

## Escopo

Define **o que** toda API sob teste modela: entidades, tipos, invariantes de
negócio e as armadilhas de representação que fariam duas linguagens divergirem
sem que ninguém percebesse.

Não define endpoints (`contract.md`), nem acesso a dados (`query-intents.md`),
nem estrutura interna da aplicação (`specs/strategies/`).

Este é um domínio **fixture**: existe para ser idêntico em toda implementação, não
para servir bem a um negócio. É fechado para modelagem — ver `specs/DDD/general.md §2.1`.

## Fixo

### Entidades

```
categories(id, name)
products(id, sku, name, price_cents, stock, category_id, attrs, created_at)
customers(id, email, name, created_at)
orders(id, customer_id, status, total_cents, idempotency_key, created_at)
order_items(order_id, product_id, qty, unit_price_cents)
```

### Tipos — as três decisões que evitam divergência silenciosa

**Identificadores são `bigint` sequenciais.** Não UUID. Duas razões: o gerador de
carga sorteia IDs de uma faixa conhecida sem precisar consultar o banco, e UUID
infla índice e payload de forma desigual entre linguagens. UUIDv7 é um eixo
possível na Fase 2, nunca no baseline.

**Dinheiro é `integer` em centavos.** Nunca decimal, nunca ponto flutuante.
`price_cents`, `unit_price_cents`, `total_cents`. Decimal tem representação e
custo radicalmente diferentes entre Java `BigDecimal`, Python `Decimal`,
JavaScript (que não tem) e Go (que também não) — comparar isso mediria a
biblioteca de decimais, não o runtime.

**Timestamps têm precisão de milissegundo, sempre em UTC, sempre com sufixo `Z`.**
Formato exato: `2026-08-21T14:03:11.482Z`. Esta é a armadilha cross-language mais
comum do projeto: `Instant` em Java carrega nanossegundos, `datetime` em Python
carrega microssegundos, `Date` em JS carrega milissegundos. Truncar para
milissegundo é obrigação da implementação, verificada byte a byte pela
conformidade.

**`attrs` é um objeto JSON plano** com 3 a 8 chaves, todas string, valores string.
Determinístico por produto a partir do seed. É repassado verbatim: a
implementação não interpreta, não reordena, não valida seu conteúdo. Existe para
dar peso realista ao payload e custo real de serialização.

**`status` de pedido** é um dos quatro literais minúsculos:
`pending`, `paid`, `shipped`, `cancelled`.

### Invariantes de negócio

Normativos. Verificados pela suíte de conformidade, não pela boa vontade da
implementação.

1. **Estoque nunca fica negativo.** Uma requisição que levaria `stock` abaixo de
   zero falha inteira — nenhum item do pedido é aplicado.
2. **Idempotência.** Duas requisições com a mesma `Idempotency-Key` produzem o
   efeito colateral uma única vez e retornam o mesmo corpo. A chave é única por
   pedido, globalmente.
3. **Total é derivado.** `total_cents = Σ(qty × unit_price_cents)` dos itens.
   Nunca informado pelo cliente, nunca recalculado na leitura.
4. **Preço é snapshot.** `unit_price_cents` grava o `price_cents` do produto no
   instante do pedido. Alterar o preço de um produto não muda pedido passado.
5. **Pedido tem ao menos um item.**
6. **`sku` e `email` são únicos.**
7. **Ordem de travamento é crescente por `product_id`.** Toda transação que
   trava múltiplos produtos os trava em ordem crescente de id. Sem isso, o
   cenário `write_contended` produz deadlocks cuja frequência varia por
   implementação — e aí você mede a sorte do escalonador, não o sujeito.

## Livre

- Nomes de tipos, structs, classes e módulos internos.
- Se a entidade existe como tipo próprio ou como mapa/tupla — decisão da
  estratégia, não deste documento.
- Presença ou ausência de validação de domínio interna, desde que os invariantes
  observáveis se sustentem.

## Fronteiras

- `contract.md` traduz estas entidades em shapes HTTP. Divergência entre os dois
  documentos é bug **deste** documento: ele é a fonte.
- `query-intents.md` traduz em operações de dados. Nenhuma intenção pode violar
  um invariante daqui.
- `specs/strategies/` decide como a regra é organizada no código, nunca qual é a
  regra.

## Aceite

`make conformance IMPL=<id>` — bloco `reference-domain`. Cobre: precisão de
timestamp byte a byte, ausência de estoque negativo sob 100 escritas
concorrentes, replay idempotente, consistência de total, imutabilidade de preço
em pedido passado.
