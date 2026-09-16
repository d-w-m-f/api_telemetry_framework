UPDATE products p
SET stock = p.stock - u.qty
FROM unnest($1::bigint[], $2::int[]) AS u(product_id, qty)
WHERE p.id = u.product_id;
