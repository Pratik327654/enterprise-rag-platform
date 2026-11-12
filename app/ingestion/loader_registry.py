
from pathlib import Path

from app.ingestion.loaders import (
    load_pdf,
    load_docx,
    load_txt,
)

from app.ingestion.validators import validate_file


# Maps file extensions to their respective loaders
LOADER_REGISTRY = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_txt,
}


def load_document(file_path: str) -> list[dict]:
    """
    Validate a file and automatically select
    the appropriate document loader.
    """

    validate_file(file_path)

    extension = Path(file_path).suffix.lower()

    loader = LOADER_REGISTRY.get(extension)

    if loader is None:
        raise ValueError(
            f"No loader registered for: {extension}"
        )

    return loader(file_path)
