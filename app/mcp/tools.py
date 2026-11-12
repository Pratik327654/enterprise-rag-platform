
import logging

from app.pipeline.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

_rag_pipeline = None


def get_rag_pipeline():
    """Create and reuse a single RAG pipeline instance."""
    global _rag_pipeline

    if _rag_pipeline is None:
        logger.info("Initializing RAG pipeline for MCP server.")
        _rag_pipeline = RAGPipeline()

    return _rag_pipeline


def ask_knowledge_base(
    query: str,
    top_k: int = 5,
    top_n: int = 3,
) -> dict:
    """Answer a question using the enterprise document knowledge base."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must not be empty.")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10.")

    if not 1 <= top_n <= 5 or top_n > top_k:
        raise ValueError("top_n must be between 1 and 5 and not exceed top_k.")

    pipeline = get_rag_pipeline()

    return pipeline.ask(
        query=query,
        top_k=top_k,
        top_n=top_n,
    )


def search_company_documents(
    query: str,
    top_k: int = 5,
    top_n: int = 3,
) -> list[dict]:
    """Search company documents and return relevant reranked chunks."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must not be empty.")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10.")

    if not 1 <= top_n <= 5 or top_n > top_k:
        raise ValueError("top_n must be between 1 and 5 and not exceed top_k.")

    pipeline = get_rag_pipeline()

    retrieved_chunks = pipeline.retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    reranked_chunks = pipeline.reranker.rerank(
        query=query,
        retrieved_chunks=retrieved_chunks,
        top_n=top_n,
    )

    results = []

    for chunk in reranked_chunks:
        results.append({
            "text": chunk.get("text", ""),
            "metadata": chunk.get("metadata", {}),
            "distance": chunk.get("distance"),
            "rerank_score": chunk.get("rerank_score"),
            "rerank_rank": chunk.get("rerank_rank"),
        })

    return results


def get_document_count() -> dict:
    """Return the total number of document chunks stored in ChromaDB."""

    pipeline = get_rag_pipeline()

    return {
        "total_chunks": pipeline.vector_store.count()
    }
