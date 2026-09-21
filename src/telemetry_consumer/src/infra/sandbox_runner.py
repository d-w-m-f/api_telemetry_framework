import os
import subprocess
from pathlib import Path


class SandboxRunner:
    """Wraps the blocking `docker compose up` call that IS the sandbox's lifetime (see the root CLAUDE.md
    architecture section and spec/bootstrap.md's "MVP decisions"). `sandbox_main_db_dsn` must be reachable
    from *inside* the sandbox's docker network, which is why it's a different value than the consumer's own
    `DATABASE_URL` -- the consumer runs as a host process, but load_n_telemetry runs in a container on the
    shared `telemetry-net` external network (see docker/docker-compose.yml)."""

    def __init__(self, sandbox_main_db_dsn: str) -> None:
        self._sandbox_main_db_dsn = sandbox_main_db_dsn

    def run(self, compose_path: Path, run_id: str) -> int:
        env = {
            **os.environ,
            "RUN_ID": run_id,
            "MAIN_DB_DSN": self._sandbox_main_db_dsn,
        }
        try:
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_path),
                    "up",
                    "--build",
                    "--abort-on-container-exit",
                    "--exit-code-from",
                    "load_n_telemetry",
                ],
                env=env,
                check=False,
            )
            return result.returncode
        finally:
            subprocess.run(
                ["docker", "compose", "-f", str(compose_path), "down", "--volumes"],
                env=env,
                check=False,
            )
