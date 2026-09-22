# Not used by the MVP dev workflow (the consumer runs as a host process so it can shell out to `docker
# compose` directly -- see docker/docker-compose.yml's header comment). Kept for a future containerized
# deployment; needs the host's docker socket + docker CLI mounted in to still be able to spin sandboxes.

FROM python:3.14-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY src/telemetry_consumer/pyproject.toml ./
RUN poetry install --no-root --only main

COPY src/telemetry_consumer/src ./src

CMD ["python3", "src/main.py"]
