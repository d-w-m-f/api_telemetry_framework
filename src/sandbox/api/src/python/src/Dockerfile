# Build context is the repo root (see the sandbox docker-compose.yml) -- this Dockerfile pulls in both the
# app source and the shared reference-domain SQL queries from src/sandbox/api/db/.

FROM python:3.14-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    SANDBOX_DB_QUERIES_DIR=/app/db/queries/postgres

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY src/sandbox/api/src/python/pyproject.toml ./
RUN poetry install --no-root --only main

COPY src/sandbox/api/src/python/src ./src
COPY src/sandbox/api/db/queries/postgres ./db/queries/postgres

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
