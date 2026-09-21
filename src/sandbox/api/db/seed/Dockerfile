# Build context is the repo root (see the sandbox docker-compose.yml files). One-shot seeding image: loads
# a deterministic dataset profile (see profiles.yaml) into a freshly migrated sandbox DB, then exits.
#
# Copies the whole db/ directory (not just seed/) to keep generate.py's own path assumptions
# (Path(__file__).resolve().parents[2] / "db" / "seed" / "profiles.yaml") working unmodified.

FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pyyaml

WORKDIR /app
COPY src/sandbox/api/db ./db
WORKDIR /app/db/seed

ENTRYPOINT ["/bin/sh", "-c"]
