
from prometheus_client import Counter, Histogram


# Total HTTP requests grouped by method, endpoint and status.
API_REQUESTS = Counter(
    "rag_api_requests_total",
    "Total number of HTTP requests.",
    ["method", "endpoint", "status"],
)

# HTTP request processing duration.
API_REQUEST_DURATION = Histogram(
    "rag_api_request_duration_seconds",
    "HTTP request processing duration in seconds.",
    ["method", "endpoint"],
)

# Total failed HTTP requests.
API_ERRORS = Counter(
    "rag_api_errors_total",
    "Total number of failed HTTP requests.",
    ["method", "endpoint"],
)

# Time spent in individual RAG pipeline stages.
PIPELINE_STAGE_DURATION = Histogram(
    "rag_pipeline_stage_duration_seconds",
    "Execution duration of RAG pipeline stages.",
    ["stage"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60),
)
