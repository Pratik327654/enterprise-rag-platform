import numpy as np
import pytest

from app.core.exceptions import EmbeddingError
from app.embeddings.embedding_generator import (
    EmbeddingGenerator,
    EMBEDDING_DIMENSION,
)


class FakeEmbeddingModel:
    """Mock embedding model for unit testing."""

    def encode(
        self,
        texts,
        batch_size,
        convert_to_numpy,
        normalize_embeddings,
        show_progress_bar,
    ):
        return np.ones(
            (len(texts), EMBEDDING_DIMENSION),
            dtype=float,
        )


@pytest.fixture
def generator(monkeypatch):
    """Create an embedding generator with a fake model."""

    instance = EmbeddingGenerator()

    monkeypatch.setattr(
        instance,
        "_load_model",
        lambda: FakeEmbeddingModel(),
    )

    return instance


def sample_chunk():
    return {
        "text": "Employee password reset policy.",
        "metadata": {
            "document_id": "doc-123",
            "chunk_id": "chunk-456",
            "chunk_index": 1,
            "source": "employee_policy.pdf",
            "page_number": 1,
        },
    }


def test_generate_single_embedding(generator):
    result = generator.generate_embeddings(
        [sample_chunk()]
    )

    assert len(result) == 1
    assert len(result[0]["embedding"]) == EMBEDDING_DIMENSION


def test_generate_multiple_embeddings(generator):
    chunks = [
        sample_chunk(),
        sample_chunk(),
        sample_chunk(),
    ]

    result = generator.generate_embeddings(chunks)

    assert len(result) == 3

    for item in result:
        assert len(item["embedding"]) == EMBEDDING_DIMENSION


def test_embedding_metadata_is_preserved(generator):
    chunk = sample_chunk()

    result = generator.generate_embeddings([chunk])

    assert result[0]["metadata"] == chunk["metadata"]


def test_embedding_text_is_preserved(generator):
    chunk = sample_chunk()

    result = generator.generate_embeddings([chunk])

    assert result[0]["text"] == chunk["text"]


def test_empty_chunks_return_empty_list(generator):
    result = generator.generate_embeddings([])

    assert result == []


def test_invalid_batch_size_raises_error(generator):
    with pytest.raises(ValueError):
        generator.generate_embeddings(
            [sample_chunk()],
            batch_size=0,
        )


def test_invalid_chunk_text_raises_error(generator):
    chunk = sample_chunk()
    chunk["text"] = ""

    with pytest.raises(ValueError):
        generator.generate_embeddings([chunk])


def test_missing_metadata_raises_error(generator):
    chunk = {"text": "Sample document text."}

    with pytest.raises(ValueError):
        generator.generate_embeddings([chunk])


def test_model_loading_is_reused(monkeypatch):
    load_count = 0
    instance = EmbeddingGenerator()

    def fake_load_model():
        nonlocal load_count
        load_count += 1
        return FakeEmbeddingModel()

    monkeypatch.setattr(
        instance,
        "_load_model",
        fake_load_model,
    )

    instance.generate_embeddings([sample_chunk()])
    instance.generate_embeddings([sample_chunk()])

    assert load_count == 2


def test_invalid_embedding_dimension(monkeypatch):
    instance = EmbeddingGenerator()

    class InvalidDimensionModel:
        def encode(self, texts, **kwargs):
            return np.ones((len(texts), 100))

    monkeypatch.setattr(
        instance,
        "_load_model",
        lambda: InvalidDimensionModel(),
    )

    with pytest.raises(EmbeddingError):
        instance.generate_embeddings([sample_chunk()])


def test_model_failure_raises_embedding_error(monkeypatch):
    instance = EmbeddingGenerator()

    def failing_model():
        raise RuntimeError("Model unavailable")

    monkeypatch.setattr(
        instance,
        "_load_model",
        failing_model,
    )

    with pytest.raises(EmbeddingError):
        instance.generate_embeddings([sample_chunk()])