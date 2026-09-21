package com.apithroughput.backend.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.apithroughput.backend.dto.TelemetryTestStatusResponse;
import com.apithroughput.backend.service.TelemetryTestService;

@WebMvcTest(TelemetryTestController.class)
class TelemetryTestControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private TelemetryTestService service;

    @Test
    void submitReturnsAcceptedWithRunId() throws Exception {
        UUID runId = UUID.randomUUID();
        when(service.submit(any())).thenReturn(runId);

        mockMvc.perform(post("/api/telemetry-tests")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"language":"python","framework":"fastapi_async","testCategory":"read","testType":"simple_read"}
                                """))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.runId").value(runId.toString()));
    }

    @Test
    void submitRejectsBlankFields() throws Exception {
        mockMvc.perform(post("/api/telemetry-tests")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"language":"","framework":"fastapi_async","testCategory":"read","testType":"simple_read"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getStatusReturnsNotFoundForUnknownRun() throws Exception {
        UUID runId = UUID.randomUUID();
        when(service.getStatus(eq(runId))).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/telemetry-tests/{runId}", runId)).andExpect(status().isNotFound());
    }

    @Test
    void getStatusReturnsRunWhenFound() throws Exception {
        UUID runId = UUID.randomUUID();
        when(service.getStatus(eq(runId)))
                .thenReturn(Optional.of(
                        new TelemetryTestStatusResponse(runId, true, null, Map.of("p50_ms", 12.3), null)));

        mockMvc.perform(get("/api/telemetry-tests/{runId}", runId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.completed").value(true));
    }
}
