SELECT id, sku, name, price_cents, stock, category_id, attrs, created_at
FROM products
WHERE (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
LIMIT $3;
