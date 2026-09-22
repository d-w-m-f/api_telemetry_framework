infra: docker compose --env-file docker/.env.local -f docker/docker-compose.yml up
backend: bash -c 'until (echo > /dev/tcp/localhost/5432) 2>/dev/null; do sleep 1; done; until (echo > /dev/tcp/localhost/5672) 2>/dev/null; do sleep 1; done; set -a; source src/backend/.env.local; set +a; cd src/backend && mvn spring-boot:run'
telemetry_consumer: bash -c 'until (echo > /dev/tcp/localhost/5432) 2>/dev/null; do sleep 1; done; until (echo > /dev/tcp/localhost/5672) 2>/dev/null; do sleep 1; done; set -a; source src/telemetry_consumer/.env.local; set +a; cd src/telemetry_consumer && poetry run python src/main.py'
web: cd src/web && npm start
