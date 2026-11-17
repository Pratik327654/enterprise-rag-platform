

import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app

from app.api.routes import router
from app.api.schemas import HealthResponse
from app.core.config import settings
from app.monitoring.metrics import (
    API_ERRORS,
    API_REQUESTS,
    API_REQUEST_DURATION,
)
from app.pipeline.rag_pipeline import RAGPipeline


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared RAG components on application startup."""

    logger.info("Starting Enterprise RAG Platform API.")

    app.state.rag_pipeline = RAGPipeline()

    logger.info("RAG pipeline initialized.")

    yield

    logger.info("Shutting down Enterprise RAG Platform API.")

    app.state.rag_pipeline = None


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "REST API for document ingestion and "
        "Retrieval-Augmented Generation."
    ),
    lifespan=lifespan,
)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Collect HTTP request count, duration and error metrics."""

    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    endpoint = request.url.path
    start_time = perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response


    finally:
        duration = perf_counter() - start_time

        API_REQUESTS.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code),
        ).inc()

        API_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        if status_code >= 500:
            API_ERRORS.labels(
                method=method,
                endpoint=endpoint,
            ).inc()


app.include_router(router)

# Prometheus metrics endpoint.
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health_check():
    """Check whether the API application is running."""

    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
    )
