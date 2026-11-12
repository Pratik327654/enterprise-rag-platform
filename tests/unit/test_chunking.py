from uuid import UUID

import pytest

from app.chunking.text_splitter import chunk_documents


def sample_document(text="Enterprise RAG Platform"):
    """Create a sample extracted document."""

    return {
        "text": text,
        "metadata": {
            "document_id": "doc-123",
            "source": "employee_policy.pdf",
            "file_type": "pdf",
            "page_number": 1,
        },
    }


def test_short_text_creates_single_chunk():
    document = sample_document()

    result = chunk_documents([document])

    assert len(result) == 1
    assert result[0]["text"] == document["text"]


def test_long_text_creates_multiple_chunks():
    text = "Enterprise RAG Platform. " * 100
    document = sample_document(text)

    result = chunk_documents(
        [document],
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(result) > 1

    for chunk in result:
        assert len(chunk["text"]) <= 100


def test_chunk_metadata_is_preserved():
    document = sample_document()

    result = chunk_documents([document])

    metadata = result[0]["metadata"]

    assert metadata["document_id"] == "doc-123"
    assert metadata["source"] == "employee_policy.pdf"
    assert metadata["file_type"] == "pdf"
    assert metadata["page_number"] == 1


def test_each_chunk_has_unique_id():
    text = "Enterprise RAG Platform. " * 100

    result = chunk_documents(
        [sample_document(text)],
        chunk_size=100,
        chunk_overlap=20,
    )

    chunk_ids = [
        chunk["metadata"]["chunk_id"]
        for chunk in result
    ]

    for chunk_id in chunk_ids:
        UUID(chunk_id)

    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunk_index_is_sequential():
    text = "Enterprise RAG Platform. " * 100

    result = chunk_documents(
        [sample_document(text)],
        chunk_size=100,
        chunk_overlap=20,
    )

    indexes = [
        chunk["metadata"]["chunk_index"]
        for chunk in result
    ]

    assert indexes == list(range(1, len(result) + 1))


def test_chunk_start_index_is_preserved():
    text = "Enterprise RAG Platform. " * 100

    result = chunk_documents(
        [sample_document(text)],
        chunk_size=100,
        chunk_overlap=20,
    )

    for chunk in result:
        assert isinstance(
            chunk["metadata"]["start_index"],
            int,
        )

        assert chunk["metadata"]["start_index"] >= 0


def test_chunk_overlap_preserves_context():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    result = chunk_documents(
        [sample_document(text)],
        chunk_size=10,
        chunk_overlap=3,
    )

    assert len(result) > 1

    first_chunk = result[0]["text"]
    second_chunk = result[1]["text"]

    assert first_chunk[-3:] == second_chunk[:3]


def test_empty_document_list_returns_empty_list():
    result = chunk_documents([])

    assert result == []


def test_whitespace_document_is_skipped():
    document = sample_document("   \n   ")

    result = chunk_documents([document])

    assert result == []


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_documents(
            [sample_document()],
            chunk_size=0,
        )


def test_invalid_chunk_overlap_raises_error():
    with pytest.raises(ValueError):
        chunk_documents(
            [sample_document()],
            chunk_size=100,
            chunk_overlap=100,
        )