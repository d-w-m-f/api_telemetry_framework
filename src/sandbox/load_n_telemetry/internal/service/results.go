package service

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"

	"load_n_telemetry/internal/model"
)

// ErrRunNotFound means no pending telemetry_results row existed for the given run id -- the consumer should
// have inserted one before spinning this sandbox up.
var ErrRunNotFound = errors.New("no telemetry_results row for run id")

// ResultsWriter writes the finished metrics directly into the main DB's telemetry_results row, per
// spec/bootstrap.md's "MVP decisions" (load_n_telemetry writes results itself rather than relaying them
// back through the consumer).
type ResultsWriter struct {
	pool *pgxpool.Pool
}

func NewResultsWriter(ctx context.Context, dsn string) (*ResultsWriter, error) {
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		return nil, fmt.Errorf("connect to main db: %w", err)
	}
	return &ResultsWriter{pool: pool}, nil
}

func (w *ResultsWriter) Close() {
	w.pool.Close()
}

func (w *ResultsWriter) WriteMetrics(ctx context.Context, runID string, metrics model.Metrics) error {
	payload, err := json.Marshal(metrics)
	if err != nil {
		return fmt.Errorf("marshal metrics: %w", err)
	}

	tag, err := w.pool.Exec(
		ctx,
		`UPDATE telemetry_results SET metrics = $1, completed_at = now() WHERE run_id = $2`,
		payload,
		runID,
	)
	if err != nil {
		return fmt.Errorf("update telemetry_results: %w", err)
	}
	if tag.RowsAffected() == 0 {
		return fmt.Errorf("%w: %s", ErrRunNotFound, runID)
	}
	return nil
}
