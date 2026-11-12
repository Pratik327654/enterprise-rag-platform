

from typing import TypedDict, Any


class RAGState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    query: str
    top_k: int
    top_n: int

    retrieved_chunks: list[dict[str, Any]]
    reranked_chunks: list[dict[str, Any]]

    has_context: bool

    answer: str
    sources: list[dict[str, Any]]
    model: str
    status: str
