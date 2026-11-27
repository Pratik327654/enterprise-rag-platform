
import pytest

from app.evaluation.llm_metrics import (
    validate_evaluation_results,
    calculate_average_scores,
    calculate_overall_score,
    calculate_pass_rates,
    generate_evaluation_summary,
)


# --------------------------------------------------
# 1. Sample Evaluation Results
# --------------------------------------------------

@pytest.fixture
def evaluation_results():

    return [
        {
            "faithfulness": {"score": 1.0, "reason": "Supported."},
            "answer_relevancy": {"score": 0.9, "reason": "Relevant."},
            "context_relevancy": {"score": 0.8, "reason": "Useful."},
            "answer_correctness": {"score": 1.0, "reason": "Correct."},
        },
        {
            "faithfulness": {"score": 0.8, "reason": "Supported."},
            "answer_relevancy": {"score": 0.8, "reason": "Relevant."},
            "context_relevancy": {"score": 0.6, "reason": "Partial."},
            "answer_correctness": {"score": 0.8, "reason": "Correct."},
        },
    ]


# --------------------------------------------------
# 2. Validation Tests
# --------------------------------------------------

def test_valid_evaluation_results(evaluation_results):

    validate_evaluation_results(evaluation_results)


def test_empty_evaluation_results():

    with pytest.raises(ValueError):

        validate_evaluation_results([])


def test_missing_metric(evaluation_results):

    del evaluation_results[0]["faithfulness"]

    with pytest.raises(ValueError):

        validate_evaluation_results(evaluation_results)


def test_invalid_score(evaluation_results):

    evaluation_results[0]["faithfulness"]["score"] = 1.5

    with pytest.raises(ValueError):

        validate_evaluation_results(evaluation_results)


# --------------------------------------------------
# 3. Average Score Tests
# --------------------------------------------------

def test_calculate_average_scores(evaluation_results):

    result = calculate_average_scores(evaluation_results)

    assert result["faithfulness"] == 0.9
    assert result["answer_relevancy"] == 0.85
    assert result["context_relevancy"] == 0.7
    assert result["answer_correctness"] == 0.9


# --------------------------------------------------
# 4. Overall Score Tests
# --------------------------------------------------

def test_calculate_overall_score():

    average_scores = {
        "faithfulness": 0.9,
        "answer_relevancy": 0.85,
        "context_relevancy": 0.7,
        "answer_correctness": 0.9,
    }

    result = calculate_overall_score(average_scores)

    assert result == 0.8375


def test_invalid_overall_score():

    average_scores = {
        "faithfulness": 0.9,
        "answer_relevancy": 0.85,
        "context_relevancy": 1.5,
        "answer_correctness": 0.9,
    }

    with pytest.raises(ValueError):

        calculate_overall_score(average_scores)


# --------------------------------------------------
# 5. Pass Rate Tests
# --------------------------------------------------

def test_calculate_pass_rates(evaluation_results):

    result = calculate_pass_rates(
        evaluation_results,
        threshold=0.7,
    )

    assert result["threshold"] == 0.7

    assert result["metric_pass_rates"]["faithfulness"] == 1.0
    assert result["metric_pass_rates"]["answer_relevancy"] == 1.0
    assert result["metric_pass_rates"]["context_relevancy"] == 0.5
    assert result["metric_pass_rates"]["answer_correctness"] == 1.0

    assert result["overall_pass_rate"] == 0.5


def test_invalid_threshold(evaluation_results):

    with pytest.raises(ValueError):

        calculate_pass_rates(
            evaluation_results,
            threshold=1.5,
        )


# --------------------------------------------------
# 6. Evaluation Summary Test
# --------------------------------------------------

def test_generate_evaluation_summary(evaluation_results):

    result = generate_evaluation_summary(
        evaluation_results,
        threshold=0.7,
    )

    assert result["total_evaluations"] == 2

    assert result["average_scores"]["faithfulness"] == 0.9

    assert result["overall_score"] == 0.8375

    assert result["pass_statistics"]["overall_pass_rate"] == 0.5


# --------------------------------------------------
# 7. Invalid Input Tests
# --------------------------------------------------

def test_invalid_results_type():

    with pytest.raises(ValueError):

        validate_evaluation_results("invalid")


def test_invalid_result_structure():

    with pytest.raises(ValueError):

        validate_evaluation_results([None])
