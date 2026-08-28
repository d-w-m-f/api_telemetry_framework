-- Carga do dataset gerado. Executado pelo orquestrador contra um banco já
-- migrado e vazio. Caminho dos TSV vem por :dir no psql.
--
-- COPY em vez de INSERT: a carga não faz parte da medição e não deve levar
-- horas. Sequences são realinhadas ao fim porque os ids vêm explícitos no TSV.

\copy categories  (id, name)                                                    FROM :'dir'/categories.tsv
\copy products    (id, sku, name, price_cents, stock, category_id, attrs, created_at) FROM :'dir'/products.tsv
\copy customers   (id, email, name, created_at)                                 FROM :'dir'/customers.tsv
\copy orders      (id, customer_id, status, total_cents, idempotency_key, created_at) FROM :'dir'/orders.tsv
\copy order_items (order_id, product_id, qty, unit_price_cents)                 FROM :'dir'/order_items.tsv

SELECT setval('categories_id_seq', (SELECT max(id) FROM categories));
SELECT setval('products_id_seq',   (SELECT max(id) FROM products));
SELECT setval('customers_id_seq',  (SELECT max(id) FROM customers));
SELECT setval('orders_id_seq',     (SELECT max(id) FROM orders));

-- Obrigatório: sem estatísticas frescas o planner escolhe planos diferentes a
-- cada réplica e a ordem dos testes vira variável escondida (PLAN §2.9).
VACUUM ANALYZE;
