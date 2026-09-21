// Command load_n_telemetry is the request/telemetry container described in the root CLAUDE.md: it seeds no
// data itself (the sandbox-seed compose service already did that), fires the MVP's fixed-repetition read
// workload at the sandbox API, and writes the resulting metrics directly into the main DB's
// telemetry_results row. See go.md for why this binary stays stdlib-only aside from a Postgres driver.
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"load_n_telemetry/internal/service"
)

func main() {
	if err := run(context.Background()); err != nil {
		log.Fatalf("load_n_telemetry: %v", err)
	}
}

func run(ctx context.Context) error {
	baseURL, err := requireEnv("SANDBOX_API_URL")
	if err != nil {
		return err
	}
	dsn, err := requireEnv("MAIN_DB_DSN")
	if err != nil {
		return err
	}
	runID, err := requireEnv("RUN_ID")
	if err != nil {
		return err
	}
	limit, err := intEnv("LIMIT", 100)
	if err != nil {
		return err
	}
	repetitions, err := intEnv("REPETITIONS", 50)
	if err != nil {
		return err
	}

	generator := service.NewLoadGenerator(baseURL, limit)

	log.Printf("waiting for sandbox api at %s to become healthy", baseURL)
	if err := generator.WaitHealthy(ctx, 30, 2*time.Second); err != nil {
		return fmt.Errorf("sandbox api did not become healthy: %w", err)
	}

	log.Printf("firing %d requests against %s (limit=%d)", repetitions, baseURL, limit)
	samples, err := generator.Run(ctx, repetitions)
	if err != nil {
		return fmt.Errorf("load run failed: %w", err)
	}
	metrics := service.Summarize(samples)
	log.Printf("run complete: %+v", metrics)

	writer, err := service.NewResultsWriter(ctx, dsn)
	if err != nil {
		return err
	}
	defer writer.Close()

	if err := writer.WriteMetrics(ctx, runID, metrics); err != nil {
		return fmt.Errorf("writing metrics: %w", err)
	}

	log.Println("metrics written to telemetry_results, exiting 0")
	return nil
}

func requireEnv(name string) (string, error) {
	value := os.Getenv(name)
	if value == "" {
		return "", errors.New("missing required env var: " + name)
	}
	return value, nil
}

func intEnv(name string, fallback int) (int, error) {
	raw := os.Getenv(name)
	if raw == "" {
		return fallback, nil
	}
	value, err := strconv.Atoi(raw)
	if err != nil {
		return 0, fmt.Errorf("invalid int env var %s=%q: %w", name, raw, err)
	}
	return value, nil
}
