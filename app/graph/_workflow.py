

import logging

from langgraph.graph import StateGraph, START, END

from app.pipeline.rag_pipeline import RAGPipeline
from app.graph.state import RAGState
from app.graph.nodes import (
    retrieve_node,
    rerank_node,
    check_context_node,
    generate_answer_node,
    insufficient_context_node,
)
from app.graph.edges import route_after_context_check


logger = logging.getLogger(__name__)

_rag_graph = None


def build_rag_graph(pipeline=None):
    """Build and compile the LangGraph RAG workflow."""

    if pipeline is None:
        pipeline = RAGPipeline()

    builder = StateGraph(RAGState)

    builder.add_node(
        "retrieve",
        lambda state: retrieve_node(state, pipeline),
    )

    builder.add_node(
        "rerank",
        lambda state: rerank_node(state, pipeline),
    )

    builder.add_node(
        "check_context",
        check_context_node,
    )

    builder.add_node(
        "generate",
        lambda state: generate_answer_node(state, pipeline),
    )

    builder.add_node(
        "insufficient_context",
        insufficient_context_node,
    )

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "rerank")
    builder.add_edge("rerank", "check_context")

    builder.add_conditional_edges(
        "check_context",
        route_after_context_check,
        {
            "generate": "generate",
            "insufficient_context": "insufficient_context",
        },
    )

    builder.add_edge("generate", END)
    builder.add_edge("insufficient_context", END)

    logger.info("LangGraph RAG workflow compiled.")

    return builder.compile()


def get_rag_graph():
    """Create and reuse a shared compiled graph."""

    global _rag_graph

    if _rag_graph is None:
        _rag_graph = build_rag_graph()

    return _rag_graph


def ask_with_graph(
    query: str,
    top_k: int = 5,
    top_n: int = 3,
) -> dict:
    """Execute the LangGraph RAG workflow."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 10
    ):
        raise ValueError("top_k must be between 1 and 10.")

    if (
        not isinstance(top_n, int)
        or isinstance(top_n, bool)
        or not 1 <= top_n <= 5
        or top_n > top_k
    ):
        raise ValueError(
            "top_n must be between 1 and 5 and not exceed top_k."
        )

    graph = get_rag_graph()

    initial_state: RAGState = {
        "query": query.strip(),
        "top_k": top_k,
        "top_n": top_n,
    }

    final_state = graph.invoke(initial_state)

    return {
        "answer": final_state.get("answer", ""),
        "sources": final_state.get("sources", []),
        "model": final_state.get("model", ""),
        "status": final_state.get("status", "unknown"),
    }
