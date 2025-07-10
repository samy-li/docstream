from fastapi import FastAPI
from app.api.routes import router
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.metrics.metrics_provider import MetricsProvider

app = FastAPI()


app.include_router(router)
FastAPIInstrumentor.instrument_app(app)

metrics_provider = MetricsProvider("file_service")
metrics_provider.init()

request_counter = metrics_provider.create_counter(
    "requests", "Total HTTP requests", initial_labels={"endpoint": "__startup__"}
)


@app.get("/d-health")
def health():
    print("hi")
    request_counter.add(1, attributes={
        "endpoint": "/health",
        "method": "GET",
        "service": "file_service"
    })
    return {"status": "ok"}

