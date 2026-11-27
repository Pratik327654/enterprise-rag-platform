
from types import SimpleNamespace
from unittest.mock import Mock

from app.evaluation.llm_eval_runner import (
    TOP_K,
    TOP_N,
    evaluate_question,
    get_chunk_id,
    get_chunk_text,
)


def test_get_chunk_id_from_metadata():
    chunk = {
        "metadata": {"chunk_id": "chunk_01"},
        "id": "fallback_id",
    }

    assert get_chunk_id(chunk) == "chunk_01"


def test_get_chunk_id_from_id():
    chunk = {"id": "chunk_02"}

    assert get_chunk_id(chunk) == "chunk_02"


def test_get_chunk_id_returns_none_when_missing():
    assert get_chunk_id({}) is None


def test_get_chunk_text_from_string():
    chunk = "This is sample context."

    assert get_chunk_text(chunk) == "This is sample context."


def test_get_chunk_text_from_dictionary():
    chunk = {"text": "Employee leave policy."}

    assert get_chunk_text(chunk) == "Employee leave policy."


def test_get_chunk_text_returns_empty_string_when_missing():
    assert get_chunk_text({}) == ""


def test_evaluate_question_success():
    # Arrange: sample retrieved chunks
    retrieved_chunks = [
        {
            "id": "chunk_01",
            "text": "Employees receive 20 paid leaves.",
            "metadata": {"chunk_id": "chunk_01"},
        },
        {
            "id": "chunk_02",
            "text": "Unused leaves follow company policy.",
            "metadata": {"chunk_id": "chunk_02"},
        },
    ]

    reranked_chunks = retrieved_chunks[:1]

    # Mock RAG pipeline components
    pipeline = SimpleNamespace(
        retriever=SimpleNamespace(
            retrieve=Mock(return_value=retrieved_chunks)
        ),
        reranker=SimpleNamespace(
            rerank=Mock(return_value=reranked_chunks)
        ),
        generator=SimpleNamespace(
            generate=Mock(
                return_value={
                    "answer": "Employees receive 20 paid leaves.",
                    "sources": ["policy.pdf"],
                    "model": "llama3.2:1b",
                }
            )
        ),
    )

    # Mock LLM evaluator
    evaluation_result = {
        "faithfulness": {"score": 1.0, "reason": "Supported by context."},
        "answer_relevancy": {"score": 1.0, "reason": "Answers the question."},
        "context_relevancy": {"score": 1.0, "reason": "Relevant context."},
        "answer_correctness": {"score": 1.0, "reason": "Matches expected answer."},
    }

    evaluator = SimpleNamespace(
        evaluate=Mock(return_value=evaluation_result)
    )

    item = {
        "id": "E01",
        "question": "How many paid leaves do employees receive?",
        "expected_answer": "Employees receive 20 paid leaves.",
        "answerable": True,
        "relevant_chunk_ids": ["chunk_01"],
    }

    # Act
    result = evaluate_question(pipeline, evaluator, item)

    # Assert: pipeline calls
    pipeline.retriever.retrieve.assert_called_once_with(
        query=item["question"],
        top_k=TOP_K,
    )

    pipeline.reranker.rerank.assert_called_once_with(
        query=item["question"],
        retrieved_chunks=retrieved_chunks,
        top_n=TOP_N,
    )

    pipeline.generator.generate.assert_called_once_with(
        query=item["question"],
        context_chunks=reranked_chunks,
    )

    # Assert: evaluator call
    evaluator.evaluate.assert_called_once()

    evaluation_kwargs = evaluator.evaluate.call_args.kwargs

    assert evaluation_kwargs["question"] == item["question"]
    assert evaluation_kwargs["expected_answer"] == item["expected_answer"]
    assert evaluation_kwargs["generated_answer"] == (
        "Employees receive 20 paid leaves."
    )
    assert evaluation_kwargs["answerable"] is True
    assert evaluation_kwargs["context_chunks"] == [
        {"text": "Employees receive 20 paid leaves."}
    ]

    # Assert: final result
    assert result["id"] == "E01"
    assert result["question"] == item["question"]
    assert result["generated_answer"] == (
        "Employees receive 20 paid leaves."
    )
    assert result["evaluation"] == evaluation_result
    assert result["status"] == "success"
    assert result["error"] is None
    assert result["total_latency_seconds"] >= 0
