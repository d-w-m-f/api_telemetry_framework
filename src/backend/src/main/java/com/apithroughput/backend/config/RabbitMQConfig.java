package com.apithroughput.backend.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Declares the same TelemetryTest/DLQ topology the Python consumer declares (see
 * src/telemetry_consumer/src/infra/rabbitmq.py) -- both sides declaring identical, idempotent definitions
 * is what lets either one start first.
 */
@Configuration
public class RabbitMQConfig {

    public static final String TELEMETRY_TEST_EXCHANGE = "TelemetryTest";
    public static final String TELEMETRY_TEST_QUEUE = "telemetry_test";
    public static final String TELEMETRY_TEST_ROUTING_KEY = "telemetry_test";

    public static final String DLQ_EXCHANGE = "DLQ";
    public static final String DLQ_QUEUE = "dlq";
    public static final String DLQ_ROUTING_KEY = "dlq";

    @Bean
    DirectExchange telemetryTestExchange() {
        return new DirectExchange(TELEMETRY_TEST_EXCHANGE, true, false);
    }

    @Bean
    DirectExchange dlqExchange() {
        return new DirectExchange(DLQ_EXCHANGE, true, false);
    }

    @Bean
    Queue telemetryTestQueue() {
        return new Queue(TELEMETRY_TEST_QUEUE, true);
    }

    @Bean
    Queue dlqQueue() {
        return new Queue(DLQ_QUEUE, true);
    }

    @Bean
    Binding telemetryTestBinding() {
        return BindingBuilder.bind(telemetryTestQueue())
                .to(telemetryTestExchange())
                .with(TELEMETRY_TEST_ROUTING_KEY);
    }

    @Bean
    Binding dlqBinding() {
        return BindingBuilder.bind(dlqQueue()).to(dlqExchange()).with(DLQ_ROUTING_KEY);
    }
}
