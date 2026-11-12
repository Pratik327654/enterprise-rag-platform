
import pytest

from fastapi.testclient import TestClient

from app.api import main
from app.api.routes import get_rag_pipeline


class FakeVectorStore:
    def count(self):
        return 5


class FakeRAGPipeline:
    def __init__(self):
        self.vector_store = FakeVectorStore()

    def ingest_document(self, file_path):
        return {
            "source": file_path,
            "documents_processed": 2,
            "chunks_created": 5,
            "chunks_stored": 5,
            "status": "success",
        }

    def ask(self, query, top_k=5, top_n=3, where=None):
        return {
            "answer": "Employees receive 20 days of annual leave. [S1]",
            "sources": [
                {
                    "source_id": "S1",
                    "source": "employee_policy_sample.pdf",
                    "page_number": 1,
                    "chunk_id": "chunk-001",
                }
            ],
            "model": "fake-model",
        }


@pytest.fixture
def client(monkeypatch, tmp_path):
    fake_pipeline = FakeRAGPipeline()

    monkeypatch.setattr(
        main,
        "RAGPipeline",
        lambda: fake_pipeline,
    )

    monkeypatch.setattr(
        "app.api.routes.UPLOAD_DIR",
        tmp_path,
    )

    with TestClient(main.app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_document_count_endpoint(client):
    response = client.get("/documents/count")

    assert response.status_code == 200
    assert response.json()["total_chunks"] == 5


def test_query_endpoint(client):
    response = client.post(
        "/query",
        json={
            "question": "How many annual leave days?",
            "top_k": 5,
            "top_n": 3,
        },
    )

    assert response.status_code == 200
    assert "20 days" in response.json()["answer"]
    assert response.json()["sources"][0]["source_id"] == "S1"


def test_query_endpoint_uses_defaults(client):
    response = client.post(
        "/query",
        json={
            "question": "How many annual leave days?"
        },
    )

    assert response.status_code == 200


def test_query_endpoint_rejects_empty_question(client):
    response = client.post(
        "/query",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_query_endpoint_rejects_invalid_top_k(client):
    response = client.post(
        "/query",
        json={
            "question": "Test question?",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_upload_endpoint(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Employees receive 20 days of annual leave.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["chunks_stored"] == 5


def test_upload_rejects_unsupported_extension(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.exe",
                b"invalid content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_upload_rejects_empty_file(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
