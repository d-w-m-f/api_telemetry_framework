-- Collected telemetry for a run. Inserted (pending, metrics NULL) by the consumer right before it spins the
-- sandbox, then updated directly by load_n_telemetry itself once its request batch finishes -- see
-- spec/bootstrap.md's "MVP decisions" section for why load_n_telemetry writes here directly instead of
-- relaying results back through the consumer.

CREATE TABLE telemetry_results (
    run_id       uuid PRIMARY KEY REFERENCES telemetry_runs (id),
    metrics      jsonb,
    completed_at timestamptz(3)
);
