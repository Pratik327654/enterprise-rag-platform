
import pytest

from app.ingestion.validators import validate_file


def test_valid_pdf_file(tmp_path):
    file = tmp_path / "sample.pdf"
    file.write_text("PDF test content")

    assert validate_file(str(file)) is True


def test_valid_docx_file(tmp_path):
    file = tmp_path / "sample.docx"
    file.write_text("DOCX test content")

    assert validate_file(str(file)) is True


def test_valid_txt_file(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("TXT test content")

    assert validate_file(str(file)) is True


def test_unsupported_file_type(tmp_path):
    file = tmp_path / "sample.exe"
    file.write_text("Test content")

    with pytest.raises(ValueError, match="Unsupported file type"):
        validate_file(str(file))


def test_nonexistent_file():
    with pytest.raises(ValueError, match="File does not exist"):
        validate_file("missing.pdf")


def test_file_size_limit(tmp_path):
    file = tmp_path / "large.txt"
    file.write_bytes(b"A" * (21 * 1024 * 1024))

    with pytest.raises(ValueError, match="exceeds 20 MB"):
        validate_file(str(file))
