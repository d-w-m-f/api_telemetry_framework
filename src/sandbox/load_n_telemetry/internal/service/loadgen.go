package service

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"load_n_telemetry/internal/model"
)

// LoadGenerator fires the MVP's fixed-repetition read workload against a sandbox API and times it.
type LoadGenerator struct {
	client  *http.Client
	baseURL string
	limit   int
}

func NewLoadGenerator(baseURL string, limit int) *LoadGenerator {
	return &LoadGenerator{
		client:  &http.Client{Timeout: 10 * time.Second},
		baseURL: baseURL,
		limit:   limit,
	}
}

// WaitHealthy polls GET /health until it returns 200 or attempts are exhausted.
func (g *LoadGenerator) WaitHealthy(ctx context.Context, attempts int, delay time.Duration) error {
	url := g.baseURL + "/health"
	var lastErr error
	for i := 0; i < attempts; i++ {
		if err := g.probeHealth(ctx, url); err != nil {
			lastErr = err
		} else {
			return nil
		}
		select {
		case <-ctx.Done():
			return fmt.Errorf("waiting for sandbox api: %w", ctx.Err())
		case <-time.After(delay):
		}
	}
	return fmt.Errorf("sandbox api never became healthy after %d attempts: %w", attempts, lastErr)
}

func (g *LoadGenerator) probeHealth(ctx context.Context, url string) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return fmt.Errorf("build health request: %w", err)
	}
	resp, err := g.client.Do(req)
	if err != nil {
		return fmt.Errorf("health request failed: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("health check returned status %d", resp.StatusCode)
	}
	return nil
}

// Run fires `repetitions` sequential GET /products?limit=<limit> requests, recording latency and success
// per call. It never returns an error itself — a failed request is just recorded as an unsuccessful sample.
func (g *LoadGenerator) Run(ctx context.Context, repetitions int) ([]model.Sample, error) {
	url := fmt.Sprintf("%s/products?limit=%d", g.baseURL, g.limit)
	samples := make([]model.Sample, 0, repetitions)
	for i := 0; i < repetitions; i++ {
		sample, err := g.fireOne(ctx, url)
		if err != nil {
			return nil, fmt.Errorf("request %d: %w", i, err)
		}
		samples = append(samples, sample)
	}
	return samples, nil
}

func (g *LoadGenerator) fireOne(ctx context.Context, url string) (model.Sample, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return model.Sample{}, fmt.Errorf("build request: %w", err)
	}

	start := time.Now()
	resp, err := g.client.Do(req)
	latencyMS := float64(time.Since(start).Microseconds()) / 1000.0

	success := err == nil && resp.StatusCode == http.StatusOK
	if resp != nil {
		resp.Body.Close()
	}
	return model.Sample{LatencyMS: latencyMS, Success: success}, nil
}
