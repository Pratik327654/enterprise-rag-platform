
import pytest

from app.ingestion.loader_registry import load_document


def test_registry_loads_txt_automatically(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text(
        "Enterprise RAG Platform",
        encoding="utf-8"
    )

    result = load_document(str(file))

    assert len(result) == 1
    assert result[0]["text"] == "Enterprise RAG Platform"
    assert result[0]["metadata"]["file_type"] == "txt"


def test_registry_rejects_unsupported_file(tmp_path):
    file = tmp_path / "sample.exe"
    file.write_text("Test content")

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(str(file))


def test_registry_rejects_missing_file():
    with pytest.raises(ValueError, match="File does not exist"):
        load_document("missing.txt")
