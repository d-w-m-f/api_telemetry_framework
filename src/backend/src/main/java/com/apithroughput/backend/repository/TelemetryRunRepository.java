package com.apithroughput.backend.repository;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.apithroughput.backend.entity.TelemetryRun;

public interface TelemetryRunRepository extends JpaRepository<TelemetryRun, UUID> {
}
