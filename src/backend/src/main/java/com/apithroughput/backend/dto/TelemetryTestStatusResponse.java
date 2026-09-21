package com.apithroughput.backend.dto;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record TelemetryTestStatusResponse(
        UUID runId,
        boolean completed,
        Map<String, Object> error,
        Map<String, Object> metrics,
        Instant completedAt) {
}
