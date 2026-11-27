import csv
import json
import logging
from pathlib import Path
from time import perf_counter

from app.pipeline.rag_pipeline import RAGPipeline
from app.evaluation.metrics import (
    calculate_question_metrics,
    calculate_average_metrics,
)


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.json"
RESULTS_DIR = BASE_DIR / "results"
JSON_OUTPUT = RESULTS_DIR / "latest_results.json"
CSV_OUTPUT = RESULTS_DIR / "latest_results.csv"

TOP_K = 5
TOP_N = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_chunk_id(chunk):
    metadata = chunk.get("metadata") or {}
    return metadata.get("chunk_id") or chunk.get("id")


def evaluate_question(pipeline, item):
    question_id = item["id"]
    query = item["question"]

    result = {
        "id": question_id,
        "question": query,
        "expected_answer": item.get("expected_answer", ""),
        "answerable": item.get("answerable", True),
        "relevant_chunk_ids": item.get("relevant_chunk_ids", []),
        "retrieved_chunk_ids": [],
        "reranked_chunk_ids": [],
        "reranker_scores": [],
        "answer": "",
        "sources": [],
        "model": "",
        "retrieval_latency_seconds": 0.0,
        "reranking_latency_seconds": 0.0,
        "generation_latency_seconds": 0.0,
        "total_latency_seconds": 0.0,
        "status": "failed",
        "error": None,
    }

    total_start = perf_counter()

    try:
        # Step 1: Retrieve top-k chunks.
        start = perf_counter()

        retrieved_chunks = pipeline.retriever.retrieve(
            query=query,
            top_k=TOP_K,
        )

        result["retrieval_latency_seconds"] = (
            perf_counter() - start
        )

        result["retrieved_chunk_ids"] = [
            get_chunk_id(chunk)
            for chunk in retrieved_chunks
        ]

        # Step 2: Rerank and select top-n chunks.
        start = perf_counter()

        reranked_chunks = pipeline.reranker.rerank(
            query=query,
            retrieved_chunks=retrieved_chunks,
            top_n=TOP_N,
        )

        result["reranking_latency_seconds"] = (
            perf_counter() - start
        )

        result["reranked_chunk_ids"] = [
            get_chunk_id(chunk)
            for chunk in reranked_chunks
        ]

        result["reranker_scores"] = [
            chunk.get("rerank_score")
            for chunk in reranked_chunks
        ]

        # Step 3: Generate the answer using top-n chunks.
        start = perf_counter()

        generated = pipeline.generator.generate(
            query=query,
            context_chunks=reranked_chunks,
        )

        result["generation_latency_seconds"] = (
            perf_counter() - start
        )

        result["answer"] = generated.get("answer", "")
        result["sources"] = generated.get("sources", [])
        result["model"] = generated.get("model", "")

        result["status"] = "success"

    except Exception as error:
        result["error"] = str(error)
        logger.exception("Evaluation failed for %s", question_id)

    finally:
        result["total_latency_seconds"] = (
            perf_counter() - total_start
        )

    return result


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list) or not dataset:
        raise ValueError("Dataset must be a non-empty JSON list.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading RAG pipeline...")
    pipeline = RAGPipeline()

    results = []

    print(f"\nStarting evaluation: {len(dataset)} questions")
    print(f"Retrieval top_k: {TOP_K}")
    print(f"Reranking top_n: {TOP_N}\n")

    for index, item in enumerate(dataset, start=1):
        result = evaluate_question(pipeline, item)
        results.append(result)


       
        print(
            f"[{index}/{len(dataset)}] "
            f"{result['id']}: {result['status'].upper()}"
        )

            # Calculate metrics for every question.
    for result in results:
        result["metrics"] = calculate_question_metrics(result)

    # Calculate average metrics across successful questions.
    average_metrics = calculate_average_metrics(results)

    successful = sum(
        result["status"] == "success"
        for result in results
    )

    with JSON_OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(
    {
        "results": results,
        "average_metrics": average_metrics,
    },
    file,
    indent=4,
    ensure_ascii=False,
)
    csv_fields = [
        "id",
        "question",
        "answerable",
        "status",
        "retrieval_precision_at_5",
        "retrieval_recall_at_5",
        "retrieval_mrr_at_5",
        "reranking_precision_at_3",
        "reranking_recall_at_3",
        "reranking_mrr_at_3",
        "reranking_ndcg_at_3",
        "retrieved_chunk_ids",
        "reranked_chunk_ids",
        "answer",
        "model",
        "retrieval_latency_seconds",
        "reranking_latency_seconds",
        "generation_latency_seconds",
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

            row.update(result.get("metrics", {}))

            row["retrieved_chunk_ids"] = json.dumps(
                row["retrieved_chunk_ids"]
            )
            row["reranked_chunk_ids"] = json.dumps(
                row["reranked_chunk_ids"]
            )

            writer.writerow(row)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total questions : {len(results)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {len(results) - successful}")
    print("\n========== AVERAGE METRICS ==========")

    for metric, value in average_metrics.items():
        if value is not None:
            print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: N/A")

    print("=====================================")
    print(f"JSON results    : {JSON_OUTPUT}")
    print(f"CSV results     : {CSV_OUTPUT}")
    print("========================================")


if __name__ == "__main__":
    main()
