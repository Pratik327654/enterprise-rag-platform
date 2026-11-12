
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question to ask the RAG knowledge base.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve.",
    )

    top_n: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of chunks to rerank.",
    )


class SourceResponse(BaseModel):
    source_id: str
    source: str
    page_number: int | None = None
    chunk_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    model: str


class IngestionResponse(BaseModel):
    filename: str
    documents_processed: int
    chunks_created: int
    chunks_stored: int
    status: str


class DocumentCountResponse(BaseModel):
    total_chunks: int


class HealthResponse(BaseModel):
    status: str
    project: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
