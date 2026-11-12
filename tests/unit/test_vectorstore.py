
import pytest

from app.core.exceptions import RetrievalError
from app.vectorstore.chroma_store import ChromaVectorStore


def make_embedding(position: int = 0) -> list[float]:
    """Create a normalized test vector with one active dimension."""

    vector = [0.0] * 384
    vector[position] = 1.0
    return vector


def make_chunk(
    chunk_id: str = "chunk-001",
    text: str = "Employees receive annual leave.",
    embedding: list[float] | None = None,
) -> dict:
    return {
        "text": text,
        "metadata": {
            "chunk_id": chunk_id,
            "document_id": "document-001",
            "source": "employee_policy.pdf",
            "file_type": "pdf",
            "page_number": 1,
            "chunk_index": 1,
        },
        "embedding": embedding or make_embedding(0),
    }


@pytest.fixture
def vector_store(tmp_path):
    return ChromaVectorStore(
        persist_directory=str(tmp_path / "chroma_test"),
        collection_name="test_documents",
    )


def test_collection_is_initialized(vector_store):
    assert vector_store.collection is not None
    assert vector_store.count() == 0


def test_add_single_embedding(vector_store):
    result = vector_store.add_embeddings([make_chunk()])

    assert result == 1
    assert vector_store.count() == 1


def test_add_multiple_embeddings(vector_store):
    chunks = [
        make_chunk("chunk-001", "Annual leave policy."),
        make_chunk(
            "chunk-002",
            "Employee salary policy.",
            make_embedding(1),
        ),
    ]

    result = vector_store.add_embeddings(chunks)

    assert result == 2
    assert vector_store.count() == 2


def test_empty_input_returns_zero(vector_store):
    assert vector_store.add_embeddings([]) == 0
    assert vector_store.count() == 0


def test_metadata_is_preserved(vector_store):
    chunk = make_chunk()

    vector_store.add_embeddings([chunk])

    results = vector_store.similarity_search(
        make_embedding(0),
        top_k=1,
    )

    assert results[0]["metadata"]["source"] == "employee_policy.pdf"
    assert results[0]["metadata"]["page_number"] == 1


def test_similarity_search_returns_closest_chunk(vector_store):
    chunks = [
        make_chunk("chunk-001", "Annual leave policy.", make_embedding(0)),
        make_chunk("chunk-002", "Salary policy.", make_embedding(1)),
    ]

    vector_store.add_embeddings(chunks)

    results = vector_store.similarity_search(
        make_embedding(0),
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-001"
    assert results[0]["text"] == "Annual leave policy."


def test_search_returns_distance(vector_store):
    vector_store.add_embeddings([make_chunk()])

    results = vector_store.similarity_search(
        make_embedding(0),
        top_k=1,
    )

    assert "distance" in results[0]
    assert results[0]["distance"] == pytest.approx(0.0, abs=1e-5)


def test_empty_collection_returns_empty_results(vector_store):
    results = vector_store.similarity_search(make_embedding(0))

    assert results == []


def test_invalid_top_k_raises_error(vector_store):
    with pytest.raises(ValueError):
        vector_store.similarity_search(
            make_embedding(0),
            top_k=0,
        )


def test_invalid_embedding_dimension_raises_error(vector_store):
    with pytest.raises(ValueError):
        vector_store.similarity_search([0.1, 0.2])


def test_invalid_chunk_id_raises_error(vector_store):
    chunk = make_chunk()
    del chunk["metadata"]["chunk_id"]

    with pytest.raises(ValueError):
        vector_store.add_embeddings([chunk])


def test_invalid_metadata_value_raises_error(vector_store):
    chunk = make_chunk()
    chunk["metadata"]["extra"] = {"nested": "value"}

    with pytest.raises(ValueError):
        vector_store.add_embeddings([chunk])


def test_upsert_updates_existing_chunk(vector_store):
    vector_store.add_embeddings([
        make_chunk(text="Old employee policy.")
    ])

    updated_chunk = make_chunk(text="Updated employee policy.")
    vector_store.add_embeddings([updated_chunk])

    assert vector_store.count() == 1

    results = vector_store.similarity_search(
        make_embedding(0),
        top_k=1,
    )

    assert results[0]["text"] == "Updated employee policy."


def test_data_persists_after_reinitialization(tmp_path):
    database_path = str(tmp_path / "persistent_chroma")

    first_store = ChromaVectorStore(
        persist_directory=database_path,
        collection_name="persistence_test",
    )

    first_store.add_embeddings([make_chunk()])

    second_store = ChromaVectorStore(
        persist_directory=database_path,
        collection_name="persistence_test",
    )

    assert second_store.count() == 1

    results = second_store.similarity_search(
        make_embedding(0),
        top_k=1,
    )

    assert results[0]["text"] == "Employees receive annual leave."
