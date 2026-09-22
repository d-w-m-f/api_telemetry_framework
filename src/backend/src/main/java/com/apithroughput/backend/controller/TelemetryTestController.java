package com.apithroughput.backend.controller;

import java.util.UUID;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.apithroughput.backend.dto.SubmitTelemetryTestRequest;
import com.apithroughput.backend.dto.SubmitTelemetryTestResponse;
import com.apithroughput.backend.dto.TelemetryTestStatusResponse;
import com.apithroughput.backend.service.TelemetryTestService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/telemetry-tests")
public class TelemetryTestController {

    private final TelemetryTestService service;

    public TelemetryTestController(TelemetryTestService service) {
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<SubmitTelemetryTestResponse> submit(@Valid @RequestBody SubmitTelemetryTestRequest request) {
        UUID runId = service.submit(request);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(new SubmitTelemetryTestResponse(runId));
    }

    @GetMapping("/{runId}")
    public ResponseEntity<TelemetryTestStatusResponse> getStatus(@PathVariable UUID runId) {
        return service.getStatus(runId)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
