SELECT id, price_cents, stock
FROM products
WHERE id = ANY ($1::bigint[])
ORDER BY id
FOR UPDATE;
