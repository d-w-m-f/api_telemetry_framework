-- Telemetry run bookkeeping row. One row per enqueued telemetry test.
--
-- The id is minted by the Spring Boot backend at enqueue time (never by the consumer) and carried
-- unchanged through the whole pipeline: the AMQP message body, the sandbox env vars, and the
-- telemetry_results row it's joined to. This is what makes `is_completed` a valid redelivery guard under
-- RabbitMQ's at-least-once guarantee — if the same message is delivered twice, both deliveries reference
-- the same row, so the second one can see the flag already flipped and skip reprocessing.

CREATE TABLE telemetry_runs (
    id           uuid PRIMARY KEY,
    payload      jsonb NOT NULL,
    is_completed boolean NOT NULL DEFAULT false,
    error        jsonb,
    created_at   timestamptz(3) NOT NULL DEFAULT now(),
    updated_at   timestamptz(3) NOT NULL DEFAULT now()
);
