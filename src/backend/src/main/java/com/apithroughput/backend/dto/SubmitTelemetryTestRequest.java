package com.apithroughput.backend.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * MVP payload shape consumed by src/telemetry_consumer -- see
 * SANDBOX_COMPOSE_FILES in business/service.py for which (language, framework) combinations it currently
 * resolves to a sandbox.
 */
public record SubmitTelemetryTestRequest(
        @NotBlank String language,
        @NotBlank String framework,
        @NotBlank String testCategory,
        @NotBlank String testType) {
}
