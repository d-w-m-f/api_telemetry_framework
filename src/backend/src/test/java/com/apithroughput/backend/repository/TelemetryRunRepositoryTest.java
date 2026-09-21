package com.apithroughput.backend.repository;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import com.apithroughput.backend.entity.TelemetryRun;

@DataJpaTest
class TelemetryRunRepositoryTest {

    @Autowired
    private TelemetryRunRepository repository;

    @Test
    void savesAndReadsBackARun() {
        UUID id = UUID.randomUUID();
        TelemetryRun run = new TelemetryRun(id, Map.of("language", "python", "framework", "fastapi_async"));

        repository.save(run);

        TelemetryRun found = repository.findById(id).orElseThrow();
        assertThat(found.isCompleted()).isFalse();
        assertThat(found.getPayload()).containsEntry("language", "python");
    }

    @Test
    void markEnqueueFailedRecordsError() {
        UUID id = UUID.randomUUID();
        TelemetryRun run = new TelemetryRun(id, Map.of("language", "python"));
        run.markEnqueueFailed(Map.of("reason", "broker unreachable"));

        repository.save(run);

        TelemetryRun found = repository.findById(id).orElseThrow();
        assertThat(found.getError()).containsEntry("reason", "broker unreachable");
    }
}
