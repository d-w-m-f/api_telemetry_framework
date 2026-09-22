import json
import logging
from collections.abc import Callable
from typing import Any

import pika

logger = logging.getLogger(__name__)

TELEMETRY_TEST_EXCHANGE = "TelemetryTest"
TELEMETRY_TEST_QUEUE = "telemetry_test"
TELEMETRY_TEST_ROUTING_KEY = "telemetry_test"

DLQ_EXCHANGE = "DLQ"
DLQ_QUEUE = "dlq"
DLQ_ROUTING_KEY = "dlq"


class RabbitMQClient:
    """Declares the TelemetryTest/DLQ topology (idempotently -- the backend, the actual producer, declares
    the same exchanges with the same parameters) and drives the consume loop for the root CLAUDE.md's
    at-least-once processing design: a message is only ever acked once it's been fully handled (success or
    a recorded, DLQ'd failure); an unexpected exception nacks with requeue instead."""

    def __init__(self, url: str) -> None:
        self._connection = pika.BlockingConnection(pika.URLParameters(url))
        self._channel = self._connection.channel()
        self._declare_topology()

    def _declare_topology(self) -> None:
        self._channel.exchange_declare(TELEMETRY_TEST_EXCHANGE, exchange_type="direct", durable=True)
        self._channel.exchange_declare(DLQ_EXCHANGE, exchange_type="direct", durable=True)
        self._channel.queue_declare(TELEMETRY_TEST_QUEUE, durable=True)
        self._channel.queue_declare(DLQ_QUEUE, durable=True)
        self._channel.queue_bind(TELEMETRY_TEST_QUEUE, TELEMETRY_TEST_EXCHANGE, TELEMETRY_TEST_ROUTING_KEY)
        self._channel.queue_bind(DLQ_QUEUE, DLQ_EXCHANGE, DLQ_ROUTING_KEY)

    def consume(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        self._channel.basic_qos(prefetch_count=1)

        def _callback(ch: Any, method: Any, _properties: Any, body: bytes) -> None:
            message = json.loads(body)
            try:
                on_message(message)
            except Exception:
                logger.exception("unexpected failure handling run %s, requeueing", message.get("run_id"))
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self._channel.basic_consume(TELEMETRY_TEST_QUEUE, _callback)
        logger.info("consuming from %s", TELEMETRY_TEST_QUEUE)
        self._channel.start_consuming()

    def publish_dlq(self, message: dict[str, Any]) -> None:
        self._channel.basic_publish(
            exchange=DLQ_EXCHANGE,
            routing_key=DLQ_ROUTING_KEY,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def close(self) -> None:
        self._connection.close()
