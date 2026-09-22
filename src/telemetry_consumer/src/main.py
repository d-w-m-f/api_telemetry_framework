import logging
import os
from typing import Any

from business.service import TelemetryTestService
from infra.rabbitmq import RabbitMQClient
from infra.sandbox_runner import SandboxRunner
from persistence.db import TelemetryRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    sandbox_main_db_dsn = os.environ["SANDBOX_MAIN_DB_DSN"]
    rabbitmq_url = os.environ["RABBITMQ_URL"]

    repository = TelemetryRepository(database_url)
    sandbox_runner = SandboxRunner(sandbox_main_db_dsn)
    rabbitmq = RabbitMQClient(rabbitmq_url)
    service = TelemetryTestService(repository, sandbox_runner, rabbitmq)

    def on_message(message: dict[str, Any]) -> None:
        service.handle(message["run_id"], message["payload"])

    logger.info("telemetry consumer starting")
    try:
        rabbitmq.consume(on_message)
    finally:
        rabbitmq.close()


if __name__ == "__main__":
    main()
