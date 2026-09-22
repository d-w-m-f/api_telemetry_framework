package com.apithroughput.backend.service;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.springframework.amqp.AmqpException;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

import com.apithroughput.backend.config.RabbitMQConfig;
import com.apithroughput.backend.dto.SubmitTelemetryTestRequest;
import com.apithroughput.backend.dto.TelemetryTestStatusResponse;
import com.apithroughput.backend.entity.TelemetryResult;
import com.apithroughput.backend.entity.TelemetryRun;
import com.apithroughput.backend.repository.TelemetryResultRepository;
import com.apithroughput.backend.repository.TelemetryRunRepository;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.ObjectMapper;

@Service
public class TelemetryTestService {

    private final TelemetryRunRepository runRepository;
    private final TelemetryResultRepository resultRepository;
    private final RabbitTemplate rabbitTemplate;
    private final ObjectMapper objectMapper;

    public TelemetryTestService(
            TelemetryRunRepository runRepository,
            TelemetryResultRepository resultRepository,
            RabbitTemplate rabbitTemplate,
            ObjectMapper objectMapper) {
        this.runRepository = runRepository;
        this.resultRepository = resultRepository;
        this.rabbitTemplate = rabbitTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Mints the run id here (not the consumer) and carries it into the message body -- required for
     * {@code is_completed} to work as a RabbitMQ redelivery guard, see the root CLAUDE.md architecture
     * section. The row is committed before the publish attempt; a plain {@code @Transactional} can't span
     * Postgres and RabbitMQ, so if the publish itself fails, the row is marked with that failure instead of
     * being left "pending" forever with no explanation.
     */
    public UUID submit(SubmitTelemetryTestRequest request) {
        UUID runId = UUID.randomUUID();
        Map<String, Object> payload = toPayloadMap(request);

        runRepository.save(new TelemetryRun(runId, payload));

        try {
            rabbitTemplate.convertAndSend(
                    RabbitMQConfig.TELEMETRY_TEST_EXCHANGE,
                    RabbitMQConfig.TELEMETRY_TEST_ROUTING_KEY,
                    Map.of("run_id", runId.toString(), "payload", payload));
        } catch (AmqpException e) {
            markEnqueueFailure(runId, e);
            throw e;
        }

        return runId;
    }

    public Optional<TelemetryTestStatusResponse> getStatus(UUID runId) {
        return runRepository.findById(runId).map(run -> toStatusResponse(run, resultRepository.findById(runId)));
    }

    private void markEnqueueFailure(UUID runId, Exception e) {
        runRepository.findById(runId).ifPresent(run -> {
            run.markEnqueueFailed(Map.of("reason", "enqueue failed: " + e.getMessage()));
            runRepository.save(run);
        });
    }

    private Map<String, Object> toPayloadMap(SubmitTelemetryTestRequest request) {
        return objectMapper.convertValue(request, new TypeReference<>() {});
    }

    private TelemetryTestStatusResponse toStatusResponse(TelemetryRun run, Optional<TelemetryResult> result) {
        return new TelemetryTestStatusResponse(
                run.getId(),
                run.isCompleted(),
                run.getError(),
                result.map(TelemetryResult::getMetrics).orElse(null),
                result.map(TelemetryResult::getCompletedAt).orElse(null));
    }
}
