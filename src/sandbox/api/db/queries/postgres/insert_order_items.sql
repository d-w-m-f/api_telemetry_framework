INSERT INTO order_items (order_id, product_id, qty, unit_price_cents)
SELECT $1, u.product_id, u.qty, u.unit_price_cents
FROM unnest($2::bigint[], $3::int[], $4::int[])
         AS u(product_id, qty, unit_price_cents);
