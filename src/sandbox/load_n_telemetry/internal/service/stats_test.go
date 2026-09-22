package service

import (
	"testing"

	"load_n_telemetry/internal/model"
)

func TestSummarize(t *testing.T) {
	samples := []model.Sample{
		{LatencyMS: 10, Success: true},
		{LatencyMS: 30, Success: true},
		{LatencyMS: 20, Success: true},
		{LatencyMS: 0, Success: false},
	}

	got := Summarize(samples)

	if got.Repetitions != 4 {
		t.Errorf("Repetitions = %d, want 4", got.Repetitions)
	}
	if got.Errors != 1 {
		t.Errorf("Errors = %d, want 1", got.Errors)
	}
	if got.MinMS != 10 {
		t.Errorf("MinMS = %v, want 10", got.MinMS)
	}
	if got.MaxMS != 30 {
		t.Errorf("MaxMS = %v, want 30", got.MaxMS)
	}
	if got.P50MS != 20 {
		t.Errorf("P50MS = %v, want 20", got.P50MS)
	}
}

func TestSummarizeAllErrors(t *testing.T) {
	samples := []model.Sample{
		{LatencyMS: 0, Success: false},
		{LatencyMS: 0, Success: false},
	}

	got := Summarize(samples)

	if got.Errors != 2 {
		t.Errorf("Errors = %d, want 2", got.Errors)
	}
	if got.MinMS != 0 || got.MaxMS != 0 || got.P50MS != 0 || got.P95MS != 0 {
		t.Errorf("expected all-zero percentiles with no successful samples, got %+v", got)
	}
}
