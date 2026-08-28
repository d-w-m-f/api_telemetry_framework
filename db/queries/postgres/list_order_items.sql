SELECT product_id, qty, unit_price_cents
FROM order_items
WHERE order_id = $1
ORDER BY product_id;
