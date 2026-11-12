
import pytest

from app.mcp import tools


class FakeRetriever:
    def retrieve(self, query, top_k):
        return [
            {
                "text": "Annual leave allowance is 20 days.",
                "metadata": {"source": "employee_policy.pdf"},
                "distance": 0.25,
            }
        ]


class FakeReranker:
    def rerank(self, query, retrieved_chunks, top_n):
        return [
            {
                **retrieved_chunks[0],
                "rerank_score": 0.95,
                "rerank_rank": 1,
            }
        ][:top_n]


class FakeVectorStore:
    def count(self):
        return 5


class FakePipeline:
    def __init__(self):
        self.retriever = FakeRetriever()
        self.reranker = FakeReranker()
        self.vector_store = FakeVectorStore()

    def ask(self, query, top_k, top_n):
        return {
            "answer": "Annual leave is 20 days.",
            "sources": [{"source": "employee_policy.pdf"}],
            "model": "llama3.2:1b",
        }


@pytest.fixture
def fake_pipeline(monkeypatch):
    pipeline = FakePipeline()

    monkeypatch.setattr(
        tools,
        "_rag_pipeline",
        pipeline,
    )

    return pipeline


def test_ask_knowledge_base(fake_pipeline):
    result = tools.ask_knowledge_base(
        "How many annual leave days?"
    )

    assert result["answer"] == "Annual leave is 20 days."
    assert result["model"] == "llama3.2:1b"


def test_search_company_documents(fake_pipeline):
    result = tools.search_company_documents(
        "Annual leave",
        top_k=5,
        top_n=3,
    )

    assert len(result) == 1
    assert result[0]["rerank_score"] == 0.95
    assert result[0]["rerank_rank"] == 1


def test_get_document_count(fake_pipeline):
    result = tools.get_document_count()

    assert result["total_chunks"] == 5


def test_empty_query():
    with pytest.raises(ValueError):
        tools.ask_knowledge_base("   ")


def test_invalid_top_k():
    with pytest.raises(ValueError):
        tools.search_company_documents(
            "Annual leave",
            top_k=0,
        )


def test_top_n_greater_than_top_k():
    with pytest.raises(ValueError):
        tools.ask_knowledge_base(
            "Annual leave",
            top_k=2,
            top_n=3,
        )
