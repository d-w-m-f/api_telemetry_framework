import logging
import os
from pathlib import Path
from typing import Any

from infra.rabbitmq import RabbitMQClient
from infra.sandbox_runner import SandboxRunner
from persistence.db import TelemetryRepository

logger = logging.getLogger(__name__)

_DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]
REPO_ROOT = Path(os.environ.get("REPO_ROOT") or _DEFAULT_REPO_ROOT)

# MVP supports exactly one combination end-to-end -- see spec/bootstrap.md's MVP scope. Adding a language or
# framework is a matter of adding an entry here plus that stack's own docker-compose.yml, not touching this
# service's orchestration logic.
SANDBOX_COMPOSE_FILES: dict[tuple[str, str], Path] = {
    ("python", "fastapi_async"): REPO_ROOT / "src/sandbox/api/src/python/docker-compose.yml",
}


class TelemetryTestService:
    def __init__(
        self,
        repository: TelemetryRepository,
        sandbox_runner: SandboxRunner,
        rabbitmq: RabbitMQClient,
    ) -> None:
        self._repository = repository
        self._sandbox_runner = sandbox_runner
        self._rabbitmq = rabbitmq

    def handle(self, run_id: str, payload: dict[str, Any]) -> None:
        if self._repository.is_completed(run_id):
            logger.info("run %s already completed, skipping (redelivery)", run_id)
            return

        compose_path = self._resolve_compose_path(payload)
        if compose_path is None:
            self._fail(run_id, payload, f"unsupported language/framework combination: {payload}")
            return

        self._repository.insert_pending_result(run_id)

        logger.info("spinning sandbox for run %s: %s", run_id, compose_path)
        exit_code = self._sandbox_runner.run(compose_path, run_id)

        if exit_code == 0:
            self._repository.mark_completed(run_id)
            logger.info("run %s completed successfully", run_id)
        else:
            self._fail(run_id, payload, f"sandbox exited with code {exit_code}")

    def _resolve_compose_path(self, payload: dict[str, Any]) -> Path | None:
        key = (payload.get("language"), payload.get("framework"))
        return SANDBOX_COMPOSE_FILES.get(key)

    def _fail(self, run_id: str, payload: dict[str, Any], reason: str) -> None:
        logger.error("run %s failed: %s", run_id, reason)
        self._repository.mark_failed(run_id, {"reason": reason})
        self._rabbitmq.publish_dlq({"run_id": run_id, "payload": payload, "reason": reason})
