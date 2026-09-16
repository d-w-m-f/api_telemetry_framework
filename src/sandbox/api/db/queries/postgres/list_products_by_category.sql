SELECT id, sku, name, price_cents, stock, category_id, attrs, created_at
FROM products
WHERE category_id = $1
  AND (created_at, id) < ($2, $3)
ORDER BY created_at DESC, id DESC
LIMIT $4;
