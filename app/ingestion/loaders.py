from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument

from app.core.exceptions import DocumentProcessingError
from app.ingestion.metadata import build_document_metadata


def load_pdf(file_path: str) -> list[dict]:
    """Extract text from a PDF, keeping each page separate."""

    try:
        reader = PdfReader(file_path)

        # Generate common metadata only once per PDF.
        base_metadata = build_document_metadata(
            file_path=file_path,
            file_type="pdf",
        )

        documents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                documents.append({
                    "text": text.strip(),
                    "metadata": {
                        **base_metadata,
                        "page_number": page_number,
                    },
                })

        if not documents:
            raise DocumentProcessingError(
                "No extractable text found in PDF."
            )

        return documents

    except DocumentProcessingError:
        raise
    except Exception as error:
        raise DocumentProcessingError(
            f"Failed to process PDF: {error}"
        ) from error


def load_docx(file_path: str) -> list[dict]:
    """Extract paragraphs and tables from a DOCX document."""

    try:
        document = DocxDocument(file_path)

        base_metadata = build_document_metadata(
            file_path=file_path,
            file_type="docx",
        )

        content = []

        # Extract paragraphs.
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text.strip())

        # Extract tables.
        for table_index, table in enumerate(document.tables, start=1):
            content.append(f"\n[Table {table_index}]")

            for row in table.rows:
                row_data = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                content.append(" | ".join(row_data))

        text = "\n".join(content)

        if not text.strip():
            raise DocumentProcessingError(
                "No extractable text found in DOCX."
            )

        return [{
            "text": text,
            "metadata": base_metadata,
        }]

    except DocumentProcessingError:
        raise
    except Exception as error:
        raise DocumentProcessingError(
            f"Failed to process DOCX: {error}"
        ) from error


def load_txt(file_path: str) -> list[dict]:
    """Extract text from a TXT file."""

    try:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise DocumentProcessingError(
                "TXT file is empty."
            )

        base_metadata = build_document_metadata(
            file_path=file_path,
            file_type="txt",
        )

        return [{
            "text": text.strip(),
            "metadata": base_metadata,
        }]

    except DocumentProcessingError:
        raise
    except Exception as error:
        raise DocumentProcessingError(
            f"Failed to process TXT: {error}"
        ) from error
