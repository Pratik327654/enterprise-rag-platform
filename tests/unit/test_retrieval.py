
import pytest

from app.retrieval.retriever import DocumentRetriever


class FakeEmbeddingGenerator:

    def __init__(self):
        self.received_chunks = None
        self.received_batch_size = None

    def generate_embeddings(self, chunks, batch_size=32):
        self.received_chunks = chunks
        self.received_batch_size = batch_size

        return [{
            "text": chunks[0]["text"],
            "metadata": chunks[0]["metadata"],
            "embedding": [0.1] * 384,
        }]


class FakeVectorStore:

    def __init__(self):
        self.received_embedding = None
        self.received_top_k = None
        self.received_where = None

    def similarity_search(
        self,
        query_embedding,
        top_k=5,
        where=None,
    ):
        self.received_embedding = query_embedding
        self.received_top_k = top_k
        self.received_where = where

        return [{
            "id": "chunk-001",
            "text": "Employees receive annual leave.",
            "metadata": {
                "source": "employee_policy.pdf",
                "page_number": 1,
            },
            "distance": 0.12,
        }]


@pytest.fixture
def retriever():
    embedding_generator = FakeEmbeddingGenerator()
    vector_store = FakeVectorStore()

    instance = DocumentRetriever(
        embedding_generator=embedding_generator,
        vector_store=vector_store,
    )

    return instance, embedding_generator, vector_store


def test_retrieve_returns_relevant_chunks(retriever):
    instance, _, _ = retriever

    results = instance.retrieve(
        "How many annual leave days are available?"
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-001"
    assert results[0]["text"] == "Employees receive annual leave."


def test_query_is_converted_to_embedding(retriever):
    instance, embedding_generator, _ = retriever

    instance.retrieve("What is the leave policy?")

    assert embedding_generator.received_chunks[0]["text"] == (
        "What is the leave policy?"
    )
    assert embedding_generator.received_batch_size == 1


def test_generated_embedding_is_passed_to_vector_store(retriever):
    instance, _, vector_store = retriever

    instance.retrieve("What is the leave policy?")

    assert vector_store.received_embedding == [0.1] * 384


def test_default_top_k_is_five(retriever):
    instance, _, vector_store = retriever

    instance.retrieve("What is the leave policy?")

    assert vector_store.received_top_k == 5


def test_custom_top_k_is_passed(retriever):
    instance, _, vector_store = retriever

    instance.retrieve(
        "What is the leave policy?",
        top_k=3,
    )

    assert vector_store.received_top_k == 3


def test_metadata_filter_is_passed(retriever):
    instance, _, vector_store = retriever

    filter_condition = {"source": "employee_policy.pdf"}

    instance.retrieve(
        "What is the leave policy?",
        where=filter_condition,
    )

    assert vector_store.received_where == filter_condition


def test_query_whitespace_is_removed(retriever):
    instance, embedding_generator, _ = retriever

    instance.retrieve("  What is the leave policy?  ")

    assert embedding_generator.received_chunks[0]["text"] == (
        "What is the leave policy?"
    )


@pytest.mark.parametrize("query", ["", "   ", None, 123])
def test_invalid_query_is_rejected(retriever, query):
    instance, _, _ = retriever

    with pytest.raises(ValueError):
        instance.retrieve(query)


@pytest.mark.parametrize("top_k", [0, -1, 1.5, True])
def test_invalid_top_k_is_rejected(retriever, top_k):
    instance, _, _ = retriever

    with pytest.raises(ValueError):
        instance.retrieve(
            "What is the leave policy?",
            top_k=top_k,
        )


def test_invalid_metadata_filter_is_rejected(retriever):
    instance, _, _ = retriever

    with pytest.raises(ValueError):
        instance.retrieve(
            "What is the leave policy?",
            where=["invalid"],
        )


def test_empty_retrieval_results_are_returned(retriever):
    instance, _, vector_store = retriever

    vector_store.similarity_search = lambda **kwargs: []

    results = instance.retrieve("What is the leave policy?")

    assert results == []


def test_embedding_failure_is_propagated(retriever):
    instance, embedding_generator, _ = retriever

    def raise_error(*args, **kwargs):
        raise RuntimeError("Embedding failed")

    embedding_generator.generate_embeddings = raise_error

    with pytest.raises(RuntimeError, match="Embedding failed"):
        instance.retrieve("What is the leave policy?")


def test_unexpected_embedding_count_is_rejected(retriever):
    instance, embedding_generator, _ = retriever

    embedding_generator.generate_embeddings = lambda *args, **kwargs: []

    with pytest.raises(ValueError, match="unexpected number"):
        instance.retrieve("What is the leave policy?")
