SELECT id, sku, name, price_cents, stock, category_id, attrs, created_at
FROM products
WHERE id = $1;
