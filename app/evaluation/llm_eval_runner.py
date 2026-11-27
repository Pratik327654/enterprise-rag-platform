
import csv
import json
import logging

from pathlib import Path
from time import perf_counter

from app.pipeline.rag_pipeline import RAGPipeline
from app.evaluation.llm_evaluator import LLMEvaluator
from app.evaluation.llm_metrics import generate_evaluation_summary


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset.json"
RESULTS_DIR = BASE_DIR / "results"

JSON_OUTPUT = RESULTS_DIR / "llm_eval_results.json"
CSV_OUTPUT = RESULTS_DIR / "llm_eval_results.csv"

TOP_K = 5
TOP_N = 3

PASS_THRESHOLD = 0.7


# --------------------------------------------------
# 2. Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. Helper Functions
# --------------------------------------------------

def get_chunk_id(chunk):
    """Extract chunk ID from retrieved chunk."""

    metadata = chunk.get("metadata") or {}

    return metadata.get("chunk_id") or chunk.get("id")


def get_chunk_text(chunk):
    """Extract text from retrieved chunk."""

    if isinstance(chunk, str):
        return chunk

    return chunk.get("text", "")


# --------------------------------------------------
# 4. Evaluate Individual Question
# --------------------------------------------------

def evaluate_question(pipeline, evaluator, item):
    """Run RAG generation and LLM evaluation for one question."""

    question_id = item["id"]
    query = item["question"]

    result = {
        "id": question_id,
        "question": query,
        "expected_answer": item.get("expected_answer", ""),
        "answerable": item.get("answerable", True),
        "generated_answer": "",
        "sources": [],
        "model": "",
        "retrieved_chunk_ids": [],
        "reranked_chunk_ids": [],
        "retrieved_context": [],
        "generation_latency_seconds": 0.0,
        "llm_evaluation_latency_seconds": 0.0,
        "total_latency_seconds": 0.0,
        "evaluation": None,
        "status": "failed",
        "error": None,
    }

    total_start = perf_counter()

    try:
        # Step 1: Retrieve chunks.

        retrieved_chunks = pipeline.retriever.retrieve(
            query=query,
            top_k=TOP_K,
        )

        result["retrieved_chunk_ids"] = [
            get_chunk_id(chunk)
            for chunk in retrieved_chunks
        ]

        # Step 2: Rerank chunks.

        reranked_chunks = pipeline.reranker.rerank(
            query=query,
            retrieved_chunks=retrieved_chunks,
            top_n=TOP_N,
        )

        result["reranked_chunk_ids"] = [
            get_chunk_id(chunk)
            for chunk in reranked_chunks
        ]

        # Step 3: Generate answer.

        generation_start = perf_counter()

        generated = pipeline.generator.generate(
            query=query,
            context_chunks=reranked_chunks,
        )

        result["generation_latency_seconds"] = (
            perf_counter() - generation_start
        )

        generated_answer = generated.get("answer", "")

        result["generated_answer"] = generated_answer
        result["sources"] = generated.get("sources", [])
        result["model"] = generated.get("model", "")

        # Step 4: Prepare retrieved context for Judge.

        context_chunks = [
            {
                "text": get_chunk_text(chunk)
            }
            for chunk in reranked_chunks
        ]

        result["retrieved_context"] = context_chunks

        # Step 5: Evaluate generated answer.

        evaluation_start = perf_counter()

        evaluation = evaluator.evaluate(
            question=query,
            expected_answer=item["expected_answer"],
            generated_answer=generated_answer,
            context_chunks=context_chunks,
            answerable=item.get("answerable", True),
        )

        result["llm_evaluation_latency_seconds"] = (
            perf_counter() - evaluation_start
        )

        result["evaluation"] = evaluation

        result["status"] = "success"

    except Exception as error:

        result["error"] = str(error)

        logger.exception(
            "LLM evaluation failed for question %s",
            question_id,
        )

    finally:

        result["total_latency_seconds"] = (
            perf_counter() - total_start
        )

    return result


# --------------------------------------------------
# 5. Main Evaluation Runner
# --------------------------------------------------

def main():

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        dataset = json.load(file)

    if not isinstance(dataset, list) or not dataset:

        raise ValueError(
            "Dataset must be a non-empty JSON list."
        )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info("Loading RAG pipeline...")

    pipeline = RAGPipeline()

    logger.info("Loading LLM evaluator...")

    evaluator = LLMEvaluator(
        model_name="qwen2.5:3b"
    )

    results = []

    print(f"\nStarting LLM evaluation: {len(dataset)} questions")
    print(f"Retrieval TOP_K: {TOP_K}")
    print(f"Reranking TOP_N: {TOP_N}")
    print(f"Judge model: {evaluator.model_name}\n")

    # Step 1: Evaluate all questions.

    for index, item in enumerate(dataset, start=1):

        result = evaluate_question(
            pipeline=pipeline,
            evaluator=evaluator,
            item=item,
        )

        results.append(result)

        print(
            f"[{index}/{len(dataset)}] "
            f"{result['id']}: {result['status'].upper()}"
        )

    # Step 2: Collect successful evaluations.

    successful_results = [
        result["evaluation"]
        for result in results
        if result["status"] == "success"
    ]

    if not successful_results:

        raise RuntimeError(
            "No successful LLM evaluations were produced."
        )

    # Step 3: Calculate aggregate metrics.

    summary = generate_evaluation_summary(
        successful_results,
        threshold=PASS_THRESHOLD,
    )

    successful = sum(
        result["status"] == "success"
        for result in results
    )

    # Step 4: Save JSON report.

    report = {
        "total_questions": len(dataset),
        "successful": successful,
        "failed": len(dataset) - successful,
        "judge_model": evaluator.model_name,
        "top_k": TOP_K,
        "top_n": TOP_N,
        "summary": summary,
        "results": results,
    }

    with JSON_OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    # Step 5: Save CSV report.

    csv_fields = [
        "id",
        "question",
        "expected_answer",
        "answerable",
        "status",
        "faithfulness_score",
        "faithfulness_reason",
        "answer_relevancy_score",
        "answer_relevancy_reason",
        "context_relevancy_score",
        "context_relevancy_reason",
        "answer_correctness_score",
        "answer_correctness_reason",
        "generated_answer",
        "model",
        "generation_latency_seconds",
        "llm_evaluation_latency_seconds",
        "total_latency_seconds",
        "error",
    ]

    with CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=csv_fields,
        )

        writer.writeheader()

        for result in results:

            row = {
                key: result.get(key)
                for key in csv_fields
            }

            evaluation = result.get("evaluation") or {}

            for metric in [
                "faithfulness",
                "answer_relevancy",
                "context_relevancy",
                "answer_correctness",
            ]:

                metric_result = evaluation.get(metric) or {}

                row[f"{metric}_score"] = metric_result.get("score")
                row[f"{metric}_reason"] = metric_result.get("reason")

            writer.writerow(row)

    # Step 6: Print summary.

    print("\n========== LLM EVALUATION SUMMARY ==========")

    print(f"Total questions : {len(dataset)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {len(dataset) - successful}")

    print("\n========== AVERAGE SCORES ==========")

    for metric, score in summary["average_scores"].items():

        print(f"{metric}: {score:.4f}")

    print(f"\nOverall score: {summary['overall_score']:.4f}")

    print("\n========== PASS RATES ==========")

    for metric, rate in summary["pass_statistics"]["metric_pass_rates"].items():

        print(f"{metric}: {rate:.2%}")

    print(
        "Overall pass rate: "
        f"{summary['pass_statistics']['overall_pass_rate']:.2%}"
    )

    print("\n============================================")

    print(f"JSON results: {JSON_OUTPUT}")
    print(f"CSV results : {CSV_OUTPUT}")

    print("============================================")


if __name__ == "__main__":
    main()
