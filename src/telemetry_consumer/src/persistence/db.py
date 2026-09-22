from typing import Any

import psycopg
from psycopg.types.json import Json


class TelemetryRepository:
    """Plain main-DB access for telemetry_runs/telemetry_results. Not a sandbox comparison knob (unlike the
    sandbox APIs' DB-driver factory), so this stays a single straightforward client."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def is_completed(self, run_id: str) -> bool:
        with psycopg.connect(self._dsn) as conn:
            row = conn.execute(
                "SELECT is_completed FROM telemetry_runs WHERE id = %s", (run_id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"no telemetry_runs row for run_id {run_id}")
            return row[0]

    def insert_pending_result(self, run_id: str) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                "INSERT INTO telemetry_results (run_id) VALUES (%s) ON CONFLICT (run_id) DO NOTHING",
                (run_id,),
            )
            conn.commit()

    def mark_completed(self, run_id: str) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                "UPDATE telemetry_runs SET is_completed = true, updated_at = now() WHERE id = %s",
                (run_id,),
            )
            conn.commit()

    def mark_failed(self, run_id: str, error: dict[str, Any]) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                "UPDATE telemetry_runs SET error = %s, updated_at = now() WHERE id = %s",
                (Json(error), run_id),
            )
            conn.commit()
