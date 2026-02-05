import os
import time
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency", ["path"]
)

app = FastAPI(title="lab-api")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(
        request.method, request.url.path, response.status_code
    ).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(time.time() - start)
    return response


@app.get("/")
def root():
    return {"message": "lab-api"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": os.getenv("APP_VERSION", "dev")}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
