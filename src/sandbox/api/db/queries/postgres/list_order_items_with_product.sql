SELECT oi.product_id, p.sku, p.name, oi.qty, oi.unit_price_cents
FROM order_items oi
JOIN products p ON p.id = oi.product_id
WHERE oi.order_id = $1
ORDER BY oi.product_id;
