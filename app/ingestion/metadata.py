from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def build_document_metadata(
    file_path: str,
    file_type: str,
    document_id: str | None = None,
) -> dict:
    """
    Build common metadata for an ingested document.

    A single document_id identifies the complete source document,
    even when a PDF produces multiple page-level records.
    """

    path = Path(file_path)

    return {
        "document_id": document_id or str(uuid4()),
        "source": path.name,
        "file_type": file_type.lower().lstrip("."),
        "file_size_bytes": path.stat().st_size,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }