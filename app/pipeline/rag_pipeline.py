

import logging
from time import perf_counter

from app.ingestion.loader_registry import load_document
from app.chunking.text_splitter import chunk_documents
from app.embeddings.embedding_generator import EmbeddingGenerator
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import DocumentRetriever
from app.reranking.reranker import DocumentReranker
from app.generation.generator import LLMGenerator
from app.monitoring.metrics import PIPELINE_STAGE_DURATION


logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate document ingestion and RAG question answering."""

    def __init__(
        self,
        embedding_generator=None,
        vector_store=None,
        retriever=None,
        reranker=None,
        generator=None,
    ):
        self.embedding_generator = (
            embedding_generator or EmbeddingGenerator()
        )

        self.vector_store = vector_store or ChromaVectorStore()

        self.retriever = retriever or DocumentRetriever(
            embedding_generator=self.embedding_generator,
            vector_store=self.vector_store,
        )

        self.reranker = reranker or DocumentReranker()
        self.generator = generator or LLMGenerator()

    def _measure_stage(self, stage: str, operation):
        """Measure one pipeline operation and record its duration."""

        start_time = perf_counter()

        try:
            return operation()
        finally:
            duration = perf_counter() - start_time

            PIPELINE_STAGE_DURATION.labels(
                stage=stage
            ).observe(duration)

            logger.info(
                "Pipeline stage '%s' completed in %.4f seconds.",
                stage,
                duration,
            )

    def ingest_document(self, file_path: str) -> dict:
        """Load, chunk, embed and store a document."""

        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("File path must be a non-empty string.")

        logger.info("Starting document ingestion.")

        documents = self._measure_stage(
            "document_loading",
            lambda: load_document(file_path),
        )

        chunks = self._measure_stage(
            "chunking",
            lambda: chunk_documents(documents),
        )

        if not chunks:
            return {
                "source": file_path,
                "documents_processed": len(documents),
                "chunks_created": 0,
                "chunks_stored": 0,
                "status": "no_content",
            }

        embedded_chunks = self._measure_stage(
            "embedding",
            lambda: self.embedding_generator.generate_embeddings(chunks),
        )

        stored_count = self._measure_stage(
            "vector_storage",
            lambda: self.vector_store.add_embeddings(embedded_chunks),
        )

        result = {
            "source": file_path,
            "documents_processed": len(documents),
            "chunks_created": len(chunks),
            "chunks_stored": stored_count,
            "status": "success",
        }

        logger.info(
            "Document ingestion completed. Stored %d chunks.",
            stored_count,
        )

        return result

    def ask(
        self,
        query: str,
        top_k: int = 5,
        top_n: int = 3,
        where: dict | None = None,
    ) -> dict:
        """Retrieve, rerank and generate an answer."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        logger.info("Starting RAG query processing.")

        retrieved_chunks = self._measure_stage(
            "retrieval",
            lambda: self.retriever.retrieve(
                query=query,
                top_k=top_k,
                where=where,
            ),
        )

        reranked_chunks = self._measure_stage(
            "reranking",
            lambda: self.reranker.rerank(
                query=query,
                retrieved_chunks=retrieved_chunks,
                top_n=top_n,
            ),
        )

        result = self._measure_stage(
            "generation",
            lambda: self.generator.generate(
                query=query,
                context_chunks=reranked_chunks,
            ),
        )

        logger.info("RAG query processing completed.")

        return result
