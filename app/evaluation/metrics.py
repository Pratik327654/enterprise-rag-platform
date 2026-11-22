import math


def precision_at_k(retrieved_ids, relevant_ids, k):
    if k <= 0:
        raise ValueError("k must be positive.")

    if not relevant_ids:
        return None

    retrieved = retrieved_ids[:k]
    relevant = set(relevant_ids)

    if not retrieved:
        return 0.0

    hits = sum(chunk_id in relevant for chunk_id in retrieved)

    return hits / k


def recall_at_k(retrieved_ids, relevant_ids, k):
    if k <= 0:
        raise ValueError("k must be positive.")

    if not relevant_ids:
        return None

    relevant = set(relevant_ids)
    retrieved = set(retrieved_ids[:k])

    hits = len(retrieved.intersection(relevant))

    return hits / len(relevant)


def reciprocal_rank_at_k(retrieved_ids, relevant_ids, k):
    if k <= 0:
        raise ValueError("k must be positive.")

    if not relevant_ids:
        return None

    relevant = set(relevant_ids)

    for rank, chunk_id in enumerate(retrieved_ids[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(ranked_ids, relevant_ids, k):
    if k <= 0:
        raise ValueError("k must be positive.")

    if not relevant_ids:
        return None

    relevant = set(relevant_ids)

    dcg = 0.0

    for rank, chunk_id in enumerate(ranked_ids[:k], start=1):
        relevance = 1 if chunk_id in relevant else 0
        dcg += relevance / math.log2(rank + 1)

    ideal_hits = min(len(relevant), k)

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )

    return dcg / idcg if idcg else 0.0


def calculate_question_metrics(result):
    relevant_ids = result.get("relevant_chunk_ids", [])

    retrieved_ids = result.get("retrieved_chunk_ids", [])

    reranked_ids = result.get("reranked_chunk_ids", [])

    return {
        "retrieval_precision_at_5": precision_at_k(
            retrieved_ids, relevant_ids, 5
        ),
        "retrieval_recall_at_5": recall_at_k(
            retrieved_ids, relevant_ids, 5
        ),
        "retrieval_mrr_at_5": reciprocal_rank_at_k(
            retrieved_ids, relevant_ids, 5
        ),
        "reranking_precision_at_3": precision_at_k(
            reranked_ids, relevant_ids, 3
        ),
        "reranking_recall_at_3": recall_at_k(
            reranked_ids, relevant_ids, 3
        ),
        "reranking_mrr_at_3": reciprocal_rank_at_k(
            reranked_ids, relevant_ids, 3
        ),
        "reranking_ndcg_at_3": ndcg_at_k(
            reranked_ids, relevant_ids, 3
        ),
    }


def calculate_average_metrics(results):
    question_metrics = [
        calculate_question_metrics(result)
        for result in results
        if result.get("status") == "success"
    ]

    if not question_metrics:
        return {}

    averages = {}

    metric_names = question_metrics[0].keys()

    for metric in metric_names:
        values = [
            item[metric]
            for item in question_metrics
            if item[metric] is not None
        ]

        averages[metric] = (
            sum(values) / len(values)
            if values else None
        )

    return averages
