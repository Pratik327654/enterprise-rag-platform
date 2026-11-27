
import logging

from statistics import mean


logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. Metric Configuration
# --------------------------------------------------

METRIC_NAMES = [
    "faithfulness",
    "answer_relevancy",
    "context_relevancy",
    "answer_correctness",
]


# --------------------------------------------------
# 2. Validate Evaluation Results
# --------------------------------------------------

def validate_evaluation_results(results):
    """Validate a collection of LLM evaluation results."""

    if not isinstance(results, list):
        raise ValueError("Evaluation results must be a list.")

    if not results:
        raise ValueError("Evaluation results cannot be empty.")

    for index, result in enumerate(results):

        if not isinstance(result, dict):
            raise ValueError(
                f"Result at index {index} must be a dictionary."
            )

        for metric in METRIC_NAMES:

            if metric not in result:
                raise ValueError(
                    f"Missing metric '{metric}' in result {index}."
                )

            metric_data = result[metric]

            if not isinstance(metric_data, dict):
                raise ValueError(
                    f"Metric '{metric}' must contain a dictionary."
                )

            score = metric_data.get("score")

            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not 0.0 <= score <= 1.0
            ):
                raise ValueError(
                    f"Invalid score for '{metric}' in result {index}."
                )


# --------------------------------------------------
# 3. Calculate Average Metric Scores
# --------------------------------------------------

def calculate_average_scores(results):
    """Calculate average score for each evaluation metric."""

    validate_evaluation_results(results)

    average_scores = {}

    for metric in METRIC_NAMES:

        scores = [
            result[metric]["score"]
            for result in results
        ]

        average_scores[metric] = round(
            mean(scores),
            4,
        )

    return average_scores


# --------------------------------------------------
# 4. Calculate Overall Score
# --------------------------------------------------

def calculate_overall_score(average_scores):
    """Calculate the overall average across four metrics."""

    if not isinstance(average_scores, dict):
        raise ValueError("Average scores must be a dictionary.")

    for metric in METRIC_NAMES:

        score = average_scores.get(metric)

        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0.0 <= score <= 1.0
        ):
            raise ValueError(
                f"Invalid or missing average score: {metric}."
            )

    overall_score = mean(
        average_scores[metric]
        for metric in METRIC_NAMES
    )

    return round(overall_score, 4)


# --------------------------------------------------
# 5. Calculate Pass Rates
# --------------------------------------------------

def calculate_pass_rates(results, threshold=0.7):
    """Calculate metric-wise and overall pass rates."""

    validate_evaluation_results(results)

    if (
        not isinstance(threshold, (int, float))
        or isinstance(threshold, bool)
        or not 0.0 <= threshold <= 1.0
    ):
        raise ValueError("Threshold must be between 0 and 1.")

    total = len(results)

    metric_pass_rates = {}

    for metric in METRIC_NAMES:

        passed = sum(
            result[metric]["score"] >= threshold
            for result in results
        )

        metric_pass_rates[metric] = round(
            passed / total,
            4,
        )

    overall_passed = sum(
        all(
            result[metric]["score"] >= threshold
            for metric in METRIC_NAMES
        )
        for result in results
    )

    return {
        "threshold": threshold,
        "metric_pass_rates": metric_pass_rates,
        "overall_pass_rate": round(
            overall_passed / total,
            4,
        ),
    }


# --------------------------------------------------
# 6. Generate Evaluation Summary
# --------------------------------------------------

def generate_evaluation_summary(results, threshold=0.7):
    """Generate a complete LLM evaluation summary."""

    validate_evaluation_results(results)

    average_scores = calculate_average_scores(results)

    overall_score = calculate_overall_score(
        average_scores
    )

    pass_rates = calculate_pass_rates(
        results,
        threshold=threshold,
    )

    summary = {
        "total_evaluations": len(results),
        "average_scores": average_scores,
        "overall_score": overall_score,
        "pass_statistics": pass_rates,
    }

    logger.info(
        "LLM evaluation summary generated successfully."
    )

    return summary
