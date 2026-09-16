SELECT id, sku, name, price_cents, stock, category_id, attrs, created_at
FROM products
WHERE category_id = $1
  AND lower(name) LIKE $2
  AND (created_at, id) < ($3, $4)
ORDER BY created_at DESC, id DESC
LIMIT $5;
