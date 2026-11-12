
import pytest

from app.pipeline import rag_pipeline
from app.pipeline.rag_pipeline import RAGPipeline


class FakeEmbeddingGenerator:
    def generate_embeddings(self, chunks, batch_size=32):
        return [
            {
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "embedding": [0.1] * 384,
            }
            for chunk in chunks
        ]


class FakeVectorStore:
    def __init__(self):
        self.stored_chunks = []

    def add_embeddings(self, chunks):
        self.stored_chunks.extend(chunks)
        return len(chunks)


class FakeRetriever:
    def __init__(self, results=None):
        self.results = results or []
        self.last_query = None

    def retrieve(self, query, top_k=5, where=None):
        self.last_query = query
        return self.results


class FakeReranker:
    def rerank(self, query, retrieved_chunks, top_n=3):
        return retrieved_chunks[:top_n]



class FakeGenerator:
    def generate(self, query, context_chunks):
        if not context_chunks:
            return {
                "answer": (
                    "I don't have enough information in the "
                    "provided documents to answer this question."
                ),
                "sources": [],
                "model": "fake-model",
            }

        return {
            "answer": "Employees receive 20 days of annual leave. [S1]",
            "sources": [],
            "model": "fake-model",
        }



@pytest.fixture
def sample_documents():
    return [
        {
            "text": "Employees receive 20 days of annual leave.",
            "metadata": {
                "document_id": "doc-001",
                "source": "employee_policy.pdf",
                "file_type": "pdf",
                "page_number": 1,
            },
        }
    ]


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "Employees receive 20 days of annual leave.",
            "metadata": {
                "document_id": "doc-001",
                "source": "employee_policy.pdf",
                "page_number": 1,
                "chunk_id": "chunk-001",
            },
        }
    ]


@pytest.fixture
def pipeline():
    return RAGPipeline(
        embedding_generator=FakeEmbeddingGenerator(),
        vector_store=FakeVectorStore(),
        retriever=FakeRetriever(),
        reranker=FakeReranker(),
        generator=FakeGenerator(),
    )


def test_ingest_document_pipeline(
    pipeline,
    sample_documents,
    monkeypatch,
):
    monkeypatch.setattr(
        rag_pipeline,
        "load_document",
        lambda path: sample_documents,
    )

    monkeypatch.setattr(
        rag_pipeline,
        "chunk_documents",
        lambda documents: [
            {
                "text": documents[0]["text"],
                "metadata": documents[0]["metadata"],
            }
        ],
    )

    result = pipeline.ingest_document("employee_policy.pdf")

    assert result["status"] == "success"
    assert result["documents_processed"] == 1
    assert result["chunks_created"] == 1
    assert result["chunks_stored"] == 1


def test_ingestion_stores_embeddings(
    pipeline,
    sample_documents,
    monkeypatch,
):
    monkeypatch.setattr(
        rag_pipeline,
        "load_document",
        lambda path: sample_documents,
    )

    monkeypatch.setattr(
        rag_pipeline,
        "chunk_documents",
        lambda documents: [
            {
                "text": documents[0]["text"],
                "metadata": documents[0]["metadata"],
            }
        ],
    )

    pipeline.ingest_document("employee_policy.pdf")

    assert len(pipeline.vector_store.stored_chunks) == 1
    assert "embedding" in pipeline.vector_store.stored_chunks[0]


def test_ingestion_handles_empty_chunks(
    pipeline,
    sample_documents,
    monkeypatch,
):
    monkeypatch.setattr(
        rag_pipeline,
        "load_document",
        lambda path: sample_documents,
    )

    monkeypatch.setattr(
        rag_pipeline,
        "chunk_documents",
        lambda documents: [],
    )

    result = pipeline.ingest_document("empty.txt")

    assert result["status"] == "no_content"
    assert result["chunks_stored"] == 0


def test_ask_pipeline_returns_answer(
    pipeline,
    sample_chunks,
):
    pipeline.retriever.results = sample_chunks

    result = pipeline.ask(
        "How many annual leave days?",
    )

    assert "20 days" in result["answer"]


def test_ask_passes_query_to_retriever(pipeline):
    pipeline.ask("What is the leave policy?")

    assert pipeline.retriever.last_query == (
        "What is the leave policy?"
    )


def test_ask_returns_no_context_response(pipeline):
    result = pipeline.ask("Who is the CEO?")

    assert "20 days" not in result["answer"]


def test_ask_rejects_empty_query(pipeline):
    with pytest.raises(ValueError):
        pipeline.ask("")


def test_ingestion_rejects_empty_file_path(pipeline):
    with pytest.raises(ValueError):
        pipeline.ingest_document("")


def test_pipeline_uses_shared_dependencies():
    embedding = FakeEmbeddingGenerator()
    vector_store = FakeVectorStore()

    pipeline = RAGPipeline(
        embedding_generator=embedding,
        vector_store=vector_store,
    )

    assert pipeline.retriever.embedding_generator is embedding
    assert pipeline.retriever.vector_store is vector_store
