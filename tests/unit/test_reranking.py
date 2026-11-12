
import pytest

from app.core.exceptions import RetrievalError
from app.reranking.reranker import DocumentReranker


class FakeCrossEncoder:
    """Fake Cross-Encoder that returns controlled relevance scores."""

    def __init__(self, scores=None):
        self.scores = scores or []
        self.received_pairs = None
        self.predict_call_count = 0

    def predict(self, pairs, show_progress_bar=False):
        self.received_pairs = pairs
        self.predict_call_count += 1
        return self.scores


@pytest.fixture
def sample_chunks():
    return [
        {
            "id": "chunk-001",
            "text": "The company provides health insurance.",
            "metadata": {"source": "benefits.pdf"},
            "distance": 0.10,
        },
        {
            "id": "chunk-002",
            "text": "Employees receive 20 days of annual leave.",
            "metadata": {"source": "leave_policy.pdf"},
            "distance": 0.20,
        },
        {
            "id": "chunk-003",
            "text": "The office is located in Mumbai.",
            "metadata": {"source": "company_info.pdf"},
            "distance": 0.30,
        },
    ]


@pytest.fixture
def reranker():
    fake_model = FakeCrossEncoder([0.20, 0.95, 0.10])

    instance = DocumentReranker(model=fake_model)

    return instance, fake_model


def test_rerank_returns_top_relevant_chunk(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "How many annual leave days do employees receive?",
        sample_chunks,
        top_n=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-002"


def test_rerank_sorts_by_descending_score(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
        top_n=3,
    )

    assert [
        chunk["id"] for chunk in results
    ] == ["chunk-002", "chunk-001", "chunk-003"]


def test_rerank_adds_relevance_scores(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
    )

    assert results[0]["rerank_score"] == pytest.approx(0.95)


def test_rerank_adds_sequential_ranks(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
    )

    assert [
        chunk["rerank_rank"] for chunk in results
    ] == [1, 2, 3]


def test_original_metadata_is_preserved(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
    )

    assert results[0]["metadata"]["source"] == "leave_policy.pdf"


def test_original_distance_is_preserved(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
    )

    assert results[0]["distance"] == 0.20


def test_query_document_pairs_are_created(
    reranker,
    sample_chunks,
):
    instance, fake_model = reranker

    instance.rerank(
        "  What is annual leave?  ",
        sample_chunks,
    )

    assert fake_model.received_pairs[0] == (
        "What is annual leave?",
        "The company provides health insurance.",
    )


def test_top_n_limits_results(
    reranker,
    sample_chunks,
):
    instance, _ = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        sample_chunks,
        top_n=2,
    )

    assert len(results) == 2


def test_empty_chunks_return_empty_results(reranker):
    instance, fake_model = reranker

    results = instance.rerank(
        "What is the annual leave policy?",
        [],
    )

    assert results == []
    assert fake_model.predict_call_count == 0


def test_invalid_query_is_rejected(reranker, sample_chunks):
    instance, _ = reranker

    with pytest.raises(ValueError):
        instance.rerank("", sample_chunks)


def test_invalid_top_n_is_rejected(reranker, sample_chunks):
    instance, _ = reranker

    with pytest.raises(ValueError):
        instance.rerank(
            "What is the annual leave policy?",
            sample_chunks,
            top_n=0,
        )


def test_invalid_chunk_text_is_rejected(reranker):
    instance, _ = reranker

    with pytest.raises(ValueError):
        instance.rerank(
            "What is the annual leave policy?",
            [{"text": "   "}],
        )


def test_invalid_chunks_input_is_rejected(reranker):
    instance, _ = reranker

    with pytest.raises(ValueError):
        instance.rerank(
            "What is the annual leave policy?",
            "not-a-list",
        )


def test_model_loading_is_reused(monkeypatch, sample_chunks):
    load_count = 0

    def fake_cross_encoder(model_name):
        nonlocal load_count
        load_count += 1
        return FakeCrossEncoder([0.20, 0.95, 0.10])

    monkeypatch.setattr(
        "app.reranking.reranker.CrossEncoder",
        fake_cross_encoder,
    )

    instance = DocumentReranker()

    instance.rerank("What is annual leave?", sample_chunks)
    instance.rerank("What are employee benefits?", sample_chunks)

    assert load_count == 1


def test_model_failure_raises_retrieval_error(
    monkeypatch,
    sample_chunks,
):
    def failing_cross_encoder(model_name):
        raise RuntimeError("Model loading failed")

    monkeypatch.setattr(
        "app.reranking.reranker.CrossEncoder",
        failing_cross_encoder,
    )

    instance = DocumentReranker()

    with pytest.raises(RetrievalError):
        instance.rerank("What is annual leave?", sample_chunks)


def test_prediction_failure_raises_retrieval_error(
    sample_chunks,
):
    class FailingModel:
        def predict(self, pairs, show_progress_bar=False):
            raise RuntimeError("Prediction failed")

    instance = DocumentReranker(model=FailingModel())

    with pytest.raises(RetrievalError):
        instance.rerank("What is annual leave?", sample_chunks)


def test_score_count_mismatch_raises_error(sample_chunks):
    fake_model = FakeCrossEncoder([0.5])

    instance = DocumentReranker(model=fake_model)

    with pytest.raises(RetrievalError):
        instance.rerank("What is annual leave?", sample_chunks)
