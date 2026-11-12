
import logging

from app.ingestion.loader_registry import load_document
from app.chunking.text_splitter import chunk_documents
from app.embeddings.embedding_generator import EmbeddingGenerator
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import DocumentRetriever
from app.reranking.reranker import DocumentReranker
from app.generation.generator import LLMGenerator


logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Orchestrate document ingestion and RAG question answering.
    """

    def __init__(
        self,
        embedding_generator=None,
        vector_store=None,
        retriever=None,
        reranker=None,
        generator=None,
    ):
        # Shared instances for ingestion and retrieval.
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

    def ingest_document(self, file_path: str) -> dict:
        """
        Load, chunk, embed and store a document.
        """

        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("File path must be a non-empty string.")

        logger.info("Starting document ingestion: %s", file_path)

        # Step 1: Load document.
        documents = load_document(file_path)

        # Step 2: Generate document chunks.
        chunks = chunk_documents(documents)

        if not chunks:
            return {
                "source": file_path,
                "documents_processed": len(documents),
                "chunks_created": 0,
                "chunks_stored": 0,
                "status": "no_content",
            }

        # Step 3: Generate embeddings.
        embedded_chunks = (
            self.embedding_generator.generate_embeddings(chunks)
        )

        # Step 4: Store embeddings in ChromaDB.
        stored_count = self.vector_store.add_embeddings(
            embedded_chunks
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
        """
        Retrieve, rerank and generate an answer for a user query.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        logger.info("Starting RAG query processing.")

        # Step 1: Retrieve relevant chunks.
        retrieved_chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            where=where,
        )

        # Step 2: Rerank retrieved chunks.
        reranked_chunks = self.reranker.rerank(
            query=query,
            retrieved_chunks=retrieved_chunks,
            top_n=top_n,
        )

        # Step 3: Generate grounded answer.
        result = self.generator.generate(
            query=query,
            context_chunks=reranked_chunks,
        )

        logger.info("RAG query processing completed.")

        return result
