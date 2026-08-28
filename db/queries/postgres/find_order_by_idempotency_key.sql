SELECT id, customer_id, status, total_cents, created_at
FROM orders
WHERE idempotency_key = $1;
