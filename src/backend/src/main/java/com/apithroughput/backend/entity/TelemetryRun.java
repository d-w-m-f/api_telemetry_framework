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
 * Mirrors src/maindb/migrations/001_telemetry_runs.sql. The backend only ever inserts and reads this row
 * (and, on an enqueue failure, records that) -- {@code is_completed} is flipped by the Python consumer
 * directly via raw SQL, never by this entity, which is why there's no general-purpose setter for it.
 */
@Entity
@Table(name = "telemetry_runs")
public class TelemetryRun {

    @Id
    private UUID id;

    @Column(nullable = false)
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> payload;

    @Column(name = "is_completed", nullable = false)
    private boolean completed;

    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> error;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    protected TelemetryRun() {
        // JPA
    }

    public TelemetryRun(UUID id, Map<String, Object> payload) {
        this.id = id;
        this.payload = payload;
        this.completed = false;
        Instant now = Instant.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    /** Records that this run's message was never successfully enqueued -- nothing will ever consume it. */
    public void markEnqueueFailed(Map<String, Object> error) {
        this.error = error;
        this.updatedAt = Instant.now();
    }

    public UUID getId() {
        return id;
    }

    public Map<String, Object> getPayload() {
        return payload;
    }

    public boolean isCompleted() {
        return completed;
    }

    public Map<String, Object> getError() {
        return error;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
