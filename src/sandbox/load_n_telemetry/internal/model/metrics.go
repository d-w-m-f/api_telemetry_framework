package model

// Sample is one request's outcome.
type Sample struct {
	LatencyMS float64
	Success   bool
}

// Metrics is the summary written into telemetry_results.metrics. Kept intentionally small for the MVP —
// see spec/bootstrap.md's "MVP decisions" for why this isn't the full k6-style load methodology yet.
type Metrics struct {
	Repetitions int     `json:"repetitions"`
	Errors      int     `json:"errors"`
	MinMS       float64 `json:"min_ms"`
	MaxMS       float64 `json:"max_ms"`
	P50MS       float64 `json:"p50_ms"`
	P95MS       float64 `json:"p95_ms"`
}
