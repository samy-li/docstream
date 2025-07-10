# file_service – Document Upload Microservice

file_service handles file uploads, validation, and storage to MinIO as part of the Resumate platform.

## Features
- Accepts PDF, DOCX, TXT uploads
- Validates file size and MIME type
- Stores files in MinIO with retry logic
- Forwards file to parser via gRPC
- Exposes metrics for Prometheus via OpenTelemetry

## Technologies
- FastAPI
- MinIO (via `minio` Python SDK)
- Tenacity (for retry logic)
- OpenTelemetry SDK
- Prometheus + Grafana
- gRPC client

## Environment Variables
Set in `.env`:

```
MINIO_HOST=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET=resumate-files
MINIO_SECURE=false

GRPC_SERVER_HOST=parser_service
GRPC_SERVER_PORT=50051

OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_RESOURCE_ATTRIBUTES=service.name=file-service
```

## Run Locally
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

## Run with Docker
Build the image:
```
docker build -t file-service .
```

Run the container:
```
docker run --rm -p 8002:8002 --env-file .env file-service
```


## Prometheus Integration
- Metrics are exported to `otel-collector` using OTLP/gRPC.
- `otel-collector` forwards metrics to Prometheus.
- Use Grafana to visualize metrics (dashboards configured separately).

