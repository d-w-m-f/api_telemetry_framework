INSERT INTO orders (customer_id, status, total_cents, idempotency_key, created_at)
VALUES ($1, $2, $3, $4, now())
RETURNING id, customer_id, status, total_cents, created_at;
