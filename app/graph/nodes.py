

import logging

logger = logging.getLogger(__name__)


def retrieve_node(state: dict, pipeline) -> dict:
    """Retrieve relevant document chunks."""

    query = state["query"]
    top_k = state.get("top_k", 5)

    logger.info("LangGraph: Starting retrieval.")

    retrieved_chunks = pipeline.retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    logger.info(
        "LangGraph: Retrieved %d chunks.",
        len(retrieved_chunks),
    )

    return {
        "retrieved_chunks": retrieved_chunks,
    }


def rerank_node(state: dict, pipeline) -> dict:
    """Rerank retrieved document chunks."""

    query = state["query"]
    retrieved_chunks = state.get("retrieved_chunks", [])
    top_n = state.get("top_n", 3)

    logger.info("LangGraph: Starting reranking.")

    reranked_chunks = pipeline.reranker.rerank(
        query=query,
        retrieved_chunks=retrieved_chunks,
        top_n=top_n,
    )

    logger.info(
        "LangGraph: Selected %d reranked chunks.",
        len(reranked_chunks),
    )

    return {
        "reranked_chunks": reranked_chunks,
    }


def check_context_node(state: dict) -> dict:
    """Check whether reranked document context is available."""

    reranked_chunks = state.get("reranked_chunks", [])
    has_context = bool(reranked_chunks)

    logger.info(
        "LangGraph: Context available = %s",
        has_context,
    )

    return {
        "has_context": has_context,
    }


def generate_answer_node(state: dict, pipeline) -> dict:
    """Generate an answer using the existing LLM generator."""

    logger.info("LangGraph: Generating answer.")

    result = pipeline.generator.generate(
        query=state["query"],
        context_chunks=state["reranked_chunks"],
    )

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "model": result.get("model", ""),
        "status": "success",
    }


def insufficient_context_node(state: dict) -> dict:
    """Return a safe response when no context is available."""

    logger.info("LangGraph: No usable context found.")

    return {
        "answer": (
            "I do not have sufficient information in the "
            "available documents to answer this question."
        ),
        "sources": [],
        "model": "not_used",
        "status": "insufficient_context",
    }
