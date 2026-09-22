package service

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestWaitHealthy(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	g := NewLoadGenerator(srv.URL, 100)
	if err := g.WaitHealthy(context.Background(), 3, time.Millisecond); err != nil {
		t.Fatalf("WaitHealthy() error = %v, want nil", err)
	}
}

func TestWaitHealthyNeverReady(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusServiceUnavailable)
	}))
	defer srv.Close()

	g := NewLoadGenerator(srv.URL, 100)
	if err := g.WaitHealthy(context.Background(), 2, time.Millisecond); err == nil {
		t.Fatal("WaitHealthy() error = nil, want an error")
	}
}

func TestRun(t *testing.T) {
	var requests int
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requests++
		if r.URL.Query().Get("limit") != "100" {
			t.Errorf("limit query param = %q, want 100", r.URL.Query().Get("limit"))
		}
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	g := NewLoadGenerator(srv.URL, 100)
	samples, err := g.Run(context.Background(), 5)
	if err != nil {
		t.Fatalf("Run() error = %v, want nil", err)
	}
	if len(samples) != 5 {
		t.Fatalf("len(samples) = %d, want 5", len(samples))
	}
	for _, s := range samples {
		if !s.Success {
			t.Errorf("sample.Success = false, want true")
		}
	}
	if requests != 5 {
		t.Errorf("requests = %d, want 5", requests)
	}
}

func TestRunRecordsFailures(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer srv.Close()

	g := NewLoadGenerator(srv.URL, 100)
	samples, err := g.Run(context.Background(), 3)
	if err != nil {
		t.Fatalf("Run() error = %v, want nil", err)
	}
	for _, s := range samples {
		if s.Success {
			t.Errorf("sample.Success = true, want false for a 500 response")
		}
	}
}
