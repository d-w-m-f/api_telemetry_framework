package com.apithroughput.backend.entity;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * Mirrors src/maindb/migrations/002_telemetry_results.sql. Read-only from the backend's perspective: the
 * consumer inserts the pending row and load_n_telemetry writes the finished metrics directly (see
 * spec/bootstrap.md's "MVP decisions") -- the backend never writes here, only reads it for status polling.
 */
@Entity
@Table(name = "telemetry_results")
public class TelemetryResult {

    @Id
    @Column(name = "run_id")
    private UUID runId;

    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> metrics;

    @Column(name = "completed_at")
    private Instant completedAt;

    protected TelemetryResult() {
        // JPA
    }

    public UUID getRunId() {
        return runId;
    }

    public Map<String, Object> getMetrics() {
        return metrics;
    }

    public Instant getCompletedAt() {
        return completedAt;
    }
}
