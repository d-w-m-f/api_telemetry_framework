package service

import (
	"sort"

	"load_n_telemetry/internal/model"
)

// Summarize reduces raw samples to the metrics summary persisted to telemetry_results.
func Summarize(samples []model.Sample) model.Metrics {
	latencies := make([]float64, 0, len(samples))
	errors := 0
	for _, s := range samples {
		if s.Success {
			latencies = append(latencies, s.LatencyMS)
		} else {
			errors++
		}
	}
	sort.Float64s(latencies)

	return model.Metrics{
		Repetitions: len(samples),
		Errors:      errors,
		MinMS:       percentile(latencies, 0),
		MaxMS:       percentile(latencies, 100),
		P50MS:       percentile(latencies, 50),
		P95MS:       percentile(latencies, 95),
	}
}

func percentile(sorted []float64, p float64) float64 {
	if len(sorted) == 0 {
		return 0
	}
	idx := int(p / 100 * float64(len(sorted)-1))
	return sorted[idx]
}
