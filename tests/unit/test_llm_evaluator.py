

import pytest

from types import SimpleNamespace

from app.evaluation.llm_evaluator import LLMEvaluator


# --------------------------------------------------
# 1. Mock Judge Response
# --------------------------------------------------

VALID_JUDGE_RESPONSE = """
{
    "faithfulness": {
        "score": 1.0,
        "reason": "Answer is supported by context."
    },
    "answer_relevancy": {
        "score": 1.0,
        "reason": "Answer addresses the question."
    },
    "context_relevancy": {
        "score": 1.0,
        "reason": "Context directly supports the answer."
    },
    "answer_correctness": {
        "score": 1.0,
        "reason": "Answer matches expected answer."
    }
}
"""


# --------------------------------------------------
# 2. Mock LLM
# --------------------------------------------------

class MockLLM:

    def invoke(self, prompt):
        return SimpleNamespace(
            content=VALID_JUDGE_RESPONSE
        )


# --------------------------------------------------
# 3. Fixtures
# --------------------------------------------------

@pytest.fixture
def evaluator():

    return LLMEvaluator(
        llm=MockLLM()
    )


@pytest.fixture
def evaluation_inputs():

    return {
        "question": (
            "How many annual leave days does "
            "a full-time employee receive?"
        ),
        "expected_answer": "20 days per calendar year.",
        "generated_answer": (
            "A full-time employee receives "
            "20 days of annual leave per year."
        ),
        "context_chunks": [
            {
                "text": (
                    "Full-time employees receive "
                    "20 days of annual leave per calendar year."
                )
            }
        ],
        "answerable": True,
    }


# --------------------------------------------------
# 4. Constructor Tests
# --------------------------------------------------

def test_evaluator_initialization(evaluator):

    assert evaluator.model_name is not None
    assert evaluator.temperature == 0.0
    assert evaluator.llm is not None


def test_invalid_temperature():

    with pytest.raises(ValueError):
        LLMEvaluator(temperature=2.0)


# --------------------------------------------------
# 5. Input Validation Tests
# --------------------------------------------------

def test_empty_question_validation(evaluator, evaluation_inputs):

    evaluation_inputs["question"] = ""

    with pytest.raises(ValueError):
        evaluator.evaluate(**evaluation_inputs)


def test_invalid_context_validation(evaluator, evaluation_inputs):

    evaluation_inputs["context_chunks"] = "invalid context"

    with pytest.raises(ValueError):
        evaluator.evaluate(**evaluation_inputs)


def test_invalid_answerable_validation(evaluator, evaluation_inputs):

    evaluation_inputs["answerable"] = "yes"

    with pytest.raises(ValueError):
        evaluator.evaluate(**evaluation_inputs)


# --------------------------------------------------
# 6. Context Formatting Tests
# --------------------------------------------------

def test_format_context(evaluator):

    chunks = [
        {"text": "Annual leave is 20 days."},
        {"text": "Sick leave is 10 days."},
    ]

    result = evaluator._format_context(chunks)

    assert "Context 1:" in result
    assert "Context 2:" in result
    assert "Annual leave is 20 days." in result
    assert "Sick leave is 10 days." in result


def test_empty_context_formatting(evaluator):

    result = evaluator._format_context([])

    assert result == "No context retrieved."


# --------------------------------------------------
# 7. Judge Prompt Test
# --------------------------------------------------

def test_judge_prompt_generation(evaluator, evaluation_inputs):

    context = evaluator._format_context(
        evaluation_inputs["context_chunks"]
    )

    prompt = evaluator._build_judge_prompt(
        question=evaluation_inputs["question"],
        expected_answer=evaluation_inputs["expected_answer"],
        generated_answer=evaluation_inputs["generated_answer"],
        context=context,
        answerable=True,
    )

    assert "independent evaluator for a RAG system" in prompt
    assert "FAITHFULNESS" in prompt
    assert "ANSWER RELEVANCY" in prompt
    assert "CONTEXT RELEVANCY" in prompt
    assert "ANSWER CORRECTNESS" in prompt
    assert "Score 1.0 if the context directly answers the question." in prompt
    assert "Do not require extra information beyond the question." in prompt

# --------------------------------------------------
# 8. Structured JSON Evaluation Test
# --------------------------------------------------

def test_successful_evaluation(evaluator, evaluation_inputs):

    result = evaluator.evaluate(**evaluation_inputs)

    assert isinstance(result, dict)

    assert result["faithfulness"]["score"] == 1.0
    assert result["answer_relevancy"]["score"] == 1.0
    assert result["context_relevancy"]["score"] == 1.0
    assert result["answer_correctness"]["score"] == 1.0

    assert isinstance(
        result["faithfulness"]["reason"],
        str,
    )


# --------------------------------------------------
# 9. Invalid Judge Response Test
# --------------------------------------------------

def test_invalid_judge_response(evaluation_inputs):

    class InvalidMockLLM:

        def invoke(self, prompt):
            return SimpleNamespace(
                content="Invalid JSON response"
            )

    evaluator = LLMEvaluator(
        llm=InvalidMockLLM()
    )

    with pytest.raises(RuntimeError):
        evaluator.evaluate(**evaluation_inputs)
