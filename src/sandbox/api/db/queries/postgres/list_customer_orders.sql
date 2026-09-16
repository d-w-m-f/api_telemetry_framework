SELECT o.id,
       o.customer_id,
       o.status,
       o.total_cents,
       o.created_at,
       (SELECT count(*) FROM order_items oi WHERE oi.order_id = o.id)::int AS item_count
FROM orders o
WHERE o.customer_id = $1
  AND (o.created_at, o.id) < ($2, $3)
ORDER BY o.created_at DESC, o.id DESC
LIMIT $4;
