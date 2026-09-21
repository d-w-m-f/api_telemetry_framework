# Build context is the repo root (see the sandbox docker-compose.yml files).

FROM golang:1.25 AS build

WORKDIR /src
COPY src/sandbox/load_n_telemetry/go.mod src/sandbox/load_n_telemetry/go.sum ./
RUN go mod download

COPY src/sandbox/load_n_telemetry/cmd ./cmd
COPY src/sandbox/load_n_telemetry/internal ./internal
RUN CGO_ENABLED=0 go build -o /out/load_n_telemetry ./cmd

FROM gcr.io/distroless/static-debian12

COPY --from=build /out/load_n_telemetry /load_n_telemetry

ENTRYPOINT ["/load_n_telemetry"]
