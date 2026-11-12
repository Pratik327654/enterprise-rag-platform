
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.api.schemas import HealthResponse
from app.core.config import settings
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


app.include_router(router)


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
