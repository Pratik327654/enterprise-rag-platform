from datetime import datetime
from uuid import UUID

from docx import Document as DocxDocument
from reportlab.pdfgen import canvas

from app.core.exceptions import DocumentProcessingError
from app.ingestion.loaders import (
    load_pdf,
    load_docx,
    load_txt,
)


def assert_common_metadata(metadata, file, file_type):
    """Verify metadata shared by all document formats."""

    assert UUID(metadata["document_id"])
    assert metadata["source"] == file.name
    assert metadata["file_type"] == file_type
    assert metadata["file_size_bytes"] == file.stat().st_size

    # Verify that ingestion timestamp is a valid ISO timestamp.
    timestamp = datetime.fromisoformat(metadata["ingested_at"])
    assert timestamp.tzinfo is not None


def test_load_txt(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text(
        "Enterprise RAG testing.",
        encoding="utf-8",
    )

    result = load_txt(str(file))

    assert len(result) == 1
    assert result[0]["text"] == "Enterprise RAG testing."

    assert_common_metadata(
        result[0]["metadata"],
        file,
        "txt",
    )


def test_load_docx(tmp_path):
    file = tmp_path / "sample.docx"

    document = DocxDocument()
    document.add_paragraph("Enterprise RAG document.")
    document.save(file)

    result = load_docx(str(file))

    assert len(result) == 1
    assert result[0]["text"] == "Enterprise RAG document."

    assert_common_metadata(
        result[0]["metadata"],
        file,
        "docx",
    )


def test_load_pdf(tmp_path):
    file = tmp_path / "sample.pdf"

    pdf = canvas.Canvas(str(file))
    pdf.drawString(100, 750, "Enterprise RAG Platform")
    pdf.save()

    result = load_pdf(str(file))

    assert len(result) == 1
    assert "Enterprise RAG Platform" in result[0]["text"]
    assert result[0]["metadata"]["page_number"] == 1

    assert_common_metadata(
        result[0]["metadata"],
        file,
        "pdf",
    )


def test_pdf_pages_share_same_document_id(tmp_path):
    """All extracted pages must belong to the same source document."""

    file = tmp_path / "multi_page.pdf"

    pdf = canvas.Canvas(str(file))

    pdf.drawString(100, 750, "First page content")
    pdf.showPage()

    pdf.drawString(100, 750, "Second page content")
    pdf.save()

    result = load_pdf(str(file))

    assert len(result) == 2

    first_metadata = result[0]["metadata"]
    second_metadata = result[1]["metadata"]

    assert first_metadata["document_id"] == second_metadata["document_id"]

    assert first_metadata["page_number"] == 1
    assert second_metadata["page_number"] == 2

    assert "First page content" in result[0]["text"]
    assert "Second page content" in result[1]["text"]


def test_different_documents_have_different_ids(tmp_path):
    """Separate source documents must receive separate IDs."""

    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"

    first_file.write_text("First document.", encoding="utf-8")
    second_file.write_text("Second document.", encoding="utf-8")

    first_result = load_txt(str(first_file))
    second_result = load_txt(str(second_file))

    first_id = first_result[0]["metadata"]["document_id"]
    second_id = second_result[0]["metadata"]["document_id"]

    assert first_id != second_id


def test_load_docx_with_table(tmp_path):
    file = tmp_path / "employee_data.docx"

    document = DocxDocument()
    document.add_paragraph("Employee Information")

    table = document.add_table(rows=3, cols=2)

    table.cell(0, 0).text = "Name"
    table.cell(0, 1).text = "Department"

    table.cell(1, 0).text = "Rahul"
    table.cell(1, 1).text = "IT"

    table.cell(2, 0).text = "Amit"
    table.cell(2, 1).text = "HR"

    document.save(file)

    result = load_docx(str(file))

    extracted_text = result[0]["text"]

    assert "Employee Information" in extracted_text
    assert "[Table 1]" in extracted_text
    assert "Name | Department" in extracted_text
    assert "Rahul | IT" in extracted_text
    assert "Amit | HR" in extracted_text

    assert_common_metadata(
        result[0]["metadata"],
        file,
        "docx",
    )


def test_load_empty_txt_raises_error(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("", encoding="utf-8")

    try:
        load_txt(str(file))
        assert False, "Expected DocumentProcessingError"
    except DocumentProcessingError:
        pass

   
