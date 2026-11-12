
import logging
import uuid

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.schemas import (
    DocumentCountResponse,
    IngestionResponse,
    QueryRequest,
    QueryResponse,
)
from app.core.config import BASE_DIR
from app.ingestion.validators import validate_file
from app.pipeline.rag_pipeline import RAGPipeline


logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = BASE_DIR / "data" / "raw"
MAX_UPLOAD_SIZE = 20 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024


from fastapi import Request

def get_rag_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.rag_pipeline


@router.post(
    "/documents/upload",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """Upload and ingest a supported document."""

    original_filename = Path(file.filename or "").name

    if not original_filename:
        raise HTTPException(
            status_code=400,
            detail="A valid filename is required.",
        )

    file_extension = Path(original_filename).suffix.lower()

    allowed_extensions = {".pdf", ".docx", ".txt"}

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload PDF, DOCX or TXT.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    destination = UPLOAD_DIR / unique_filename

    total_size = 0

    try:
        with destination.open("wb") as output_file:
            while True:
                content = await file.read(UPLOAD_CHUNK_SIZE)

                if not content:
                    break

                total_size += len(content)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the 20 MB limit.",
                    )

                output_file.write(content)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        validate_file(str(destination))

        result = pipeline.ingest_document(str(destination))

        if result["status"] != "success":
            raise HTTPException(
                status_code=422,
                detail="Document contains no processable content.",
            )

        return IngestionResponse(
            filename=original_filename,
            documents_processed=result["documents_processed"],
            chunks_created=result["chunks_created"],
            chunks_stored=result["chunks_stored"],
            status=result["status"],
        )

    except HTTPException:
        destination.unlink(missing_ok=True)
        raise

    except ValueError as error:
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Document upload or ingestion failed.")

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        ) from error

    finally:
        await file.close()


@router.post(
    "/query",
    response_model=QueryResponse,
)
def ask_question(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """Ask a question using the RAG knowledge base."""

    try:
        result = pipeline.ask(
            query=request.question,
            top_k=request.top_k,
            top_n=request.top_n,
        )

        return QueryResponse(**result)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Question answering failed.")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer.",
        ) from error


@router.get(
    "/documents/count",
    response_model=DocumentCountResponse,
)
def get_document_count(
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """Return the number of stored document chunks."""

    try:
        return DocumentCountResponse(
            total_chunks=pipeline.vector_store.count()
        )

    except Exception as error:
        logger.exception("Failed to retrieve document count.")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document count.",
        ) from error
