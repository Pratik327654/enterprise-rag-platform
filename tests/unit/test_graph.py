

import pytest

from app.graph._workflow import build_rag_graph, ask_with_graph
from app.graph.edges import route_after_context_check


class FakeRetriever:
    def __init__(self, chunks=None):
        self.chunks = chunks or []

    def retrieve(self, query, top_k):
        return self.chunks


class FakeReranker:
    def rerank(self, query, retrieved_chunks, top_n):
        return retrieved_chunks[:top_n]


class FakeGenerator:
    def __init__(self):
        self.called = False

    def generate(self, query, context_chunks):
        self.called = True

        return {
            "answer": "Annual leave is 20 days per year.",
            "sources": [{"source": "employee_policy.pdf"}],
            "model": "llama3.2:1b",
        }


class FakePipeline:
    def __init__(self, chunks=None):
        self.retriever = FakeRetriever(chunks)
        self.reranker = FakeReranker()
        self.generator = FakeGenerator()


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "Employees receive 20 annual leave days.",
            "metadata": {
                "source": "employee_policy.pdf",
                "page_number": 1,
                "chunk_id": "test-chunk-1",
            },
        }
    ]


def test_graph_generates_answer(sample_chunks):
    pipeline = FakePipeline(sample_chunks)

    graph = build_rag_graph(pipeline)

    result = graph.invoke({
        "query": "How many annual leave days?",
        "top_k": 5,
        "top_n": 3,
    })

    assert result["answer"] == "Annual leave is 20 days per year."
    assert result["status"] == "success"
    assert result["sources"][0]["source"] == "employee_policy.pdf"
    assert pipeline.generator.called is True


def test_graph_handles_missing_context():
    pipeline = FakePipeline([])

    graph = build_rag_graph(pipeline)

    result = graph.invoke({
        "query": "Who is the company CEO?",
        "top_k": 5,
        "top_n": 3,
    })

    assert result["status"] == "insufficient_context"
    assert result["sources"] == []
    assert pipeline.generator.called is False


def test_graph_rejects_empty_query():
    with pytest.raises(ValueError):
        ask_with_graph("   ")


def test_graph_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        ask_with_graph(
            "Annual leave",
            top_k=0,
        )


def test_graph_rejects_invalid_top_n():
    with pytest.raises(ValueError):
        ask_with_graph(
            "Annual leave",
            top_k=2,
            top_n=3,
        )


def test_route_after_context_check():
    assert route_after_context_check(
        {"has_context": True}
    ) == "generate"

    assert route_after_context_check(
        {"has_context": False}
    ) == "insufficient_context"
