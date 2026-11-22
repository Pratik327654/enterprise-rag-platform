# Automated RAG Evaluation

## 1. Overview

The Automated RAG Evaluation module evaluates the retrieval, reranking, and answer generation stages of the Enterprise RAG Platform.

It provides a systematic approach to measuring retrieval quality and reranking performance using a manually curated evaluation dataset and dynamically retrieved document chunks.

The evaluation process runs independently of the production RAG workflow without modifying the existing pipeline.

## 2. Evaluation Architecture

The evaluation workflow consists of three main stages:

1. Retrieval
2. Reranking
3. Answer Generation

### Evaluation Workflow

```text
Evaluation Dataset (30 Questions)
              |
              v
       Query Processing
              |
              v
      Retrieval (Top 5)
              |
              v
       Reranking (Top 3)
              |
              v
     Answer Generation
              |
              v
      Metric Calculation
              |
              v
       Results Export
         /        \
        v          v
      JSON        CSV
```

## 3. Evaluation Dataset

The evaluation dataset is maintained in `dataset.json`.

It contains 30 evaluation questions covering the documents available in the RAG knowledge base.

Each evaluation record includes:

- Question ID
- Question
- Expected answer
- Answerability
- Relevant chunk IDs

### Ground Truth

Relevant chunk IDs act as manually verified ground-truth labels.

These labels are used only during evaluation to measure retrieval and reranking performance.

They are not provided to the production retrieval pipeline.

Candidate chunks are dynamically retrieved from ChromaDB during evaluation.

## 4. Retrieval and Reranking Configuration

| Component | Configuration |
|---|---|
| Vector Database | ChromaDB |
| Embedding Model | all-MiniLM-L6-v2 |
| Retrieval Strategy | Similarity Search |
| Retrieval Top-K | 5 |
| Reranking Model | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Reranking Top-N | 3 |
| Generation Model | llama3.2:1b |

The retrieval stage selects the top 5 candidate chunks.

The reranking stage evaluates these candidates and selects the top 3 chunks.

Only the top 3 reranked chunks are passed to the LLM for answer generation.

## 5. Evaluation Metrics

### Retrieval Metrics

**Precision@5**

Measures the proportion of retrieved top-5 chunks that are relevant.

**Recall@5**

Measures the proportion of all ground-truth relevant chunks retrieved within the top 5 results.

**MRR@5 (Mean Reciprocal Rank)**

Measures how highly the first relevant chunk appears in the top 5 results.

### Reranking Metrics

**Precision@3**

Measures the proportion of relevant chunks in the top 3 reranked results.

**Recall@3**

Measures the proportion of ground-truth relevant chunks retained within the top 3 results.

**MRR@3**

Measures the rank of the first relevant chunk after reranking.

**NDCG@3 (Normalized Discounted Cumulative Gain)**

Measures the quality of the top 3 ranking using binary relevance labels and position-based discounting.

Metrics without ground-truth relevant chunk IDs are excluded from their respective averages.

## 6. Evaluation Results

### Evaluation Summary

| Parameter | Result |
|---|---:|
| Total Questions | 30 |
| Successful Evaluations | 30 |
| Failed Evaluations | 0 |
| Retrieval Top-K | 5 |
| Reranking Top-N | 3 |

### Average Retrieval Metrics

| Metric | Score |
|---|---:|
| Precision@5 | 0.1400 |
| Recall@5 | 0.7000 |
| MRR@5 | 0.6500 |

### Average Reranking Metrics

| Metric | Score |
|---|---:|
| Precision@3 | 0.2167 |
| Recall@3 | 0.6500 |
| MRR@3 | 0.6250 |
| NDCG@3 | 0.6315 |

These results represent the evaluation run performed on the current 30-question dataset and its ground-truth annotations.

Successful execution does not necessarily indicate that every generated answer is factually correct.

## 7. Output Files

Evaluation results are automatically exported into the `results/` directory.

### latest_results.json

Contains:

- Individual question results
- Ground-truth relevant chunk IDs
- Retrieved chunk IDs
- Reranked chunk IDs
- Generated answers
- Reranker scores
- Latency measurements
- Individual evaluation metrics
- Average evaluation metrics

### latest_results.csv

Contains tabular evaluation results, including:

- Question details
- Retrieval and reranking metrics
- Retrieved and reranked chunk IDs
- Generated answers
- Model information
- Stage-wise latency
- Error information

## 8. How to Run

Run the evaluation module from the project root directory.

```bash
python -m app.evaluation.evaluation_runner
```

The evaluation runner:

1. Loads the evaluation dataset.
2. Initializes the RAG pipeline.
3. Retrieves the top 5 chunks for each question.
4. Reranks the retrieved chunks and selects the top 3.
5. Generates answers using the LLM.
6. Calculates evaluation metrics.
7. Computes average metrics.
8. Exports results to JSON and CSV.

### Requirements

- Python environment with project dependencies installed.
- ChromaDB containing indexed documents.
- Ollama running with the configured LLM model.
- Evaluation dataset with manually verified ground-truth labels.

## 9. Limitations and Future Improvements

Current evaluation focuses on retrieval and reranking quality.

Potential future improvements include:

- Answer correctness evaluation.
- Faithfulness and groundedness evaluation.
- Context relevance measurement.
- LLM-as-a-Judge evaluation.
- Larger and more diverse evaluation datasets.
- Performance benchmarking across embedding and reranking models.
- Evaluation of latency and resource utilization.

## 10. Project Structure

```text
app/
└── evaluation/
    ├── __init__.py
    ├── dataset.json
    ├── evaluation_runner.py
    ├── metrics.py
    ├── map_chunks.py
    ├── chunk_candidates.json
    ├── README.md
    └── results/
        ├── latest_results.json
        └── latest_results.csv
```

`map_chunks.py` and `chunk_candidates.json` are retained as inspection utilities and are not dependencies of the automated evaluation workflow.
