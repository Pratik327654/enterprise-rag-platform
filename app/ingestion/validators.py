
from pathlib import Path

# Initially supported file formats
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

# Maximum upload size: 20 MB
MAX_FILE_SIZE = 20 * 1024 * 1024


def validate_file(file_path: str) -> bool:
    """
    Validate file extension and file size.
    """

    path = Path(file_path)

    # Check whether file exists
    if not path.exists() or not path.is_file():
        raise ValueError("File does not exist.")

    # Check supported file extension
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )

    # Check file size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 20 MB limit.")

    return True
