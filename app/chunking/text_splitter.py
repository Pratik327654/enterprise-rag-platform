from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[dict]:
    """
    Split extracted documents into smaller text chunks.

    Original document metadata is preserved in every chunk.
    Each chunk receives a unique chunk ID and its position.
    """

    # Validate chunking configuration.
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )

    chunks = []

    for document in documents:

        # Validate document structure.
        if not isinstance(document, dict):
            raise ValueError("Each document must be a dictionary.")

        text = document.get("text")
        metadata = document.get("metadata")

        if not isinstance(text, str):
            raise ValueError("Document text must be a string.")

        if not isinstance(metadata, dict):
            raise ValueError("Document metadata must be a dictionary.")

        # Ignore documents containing only whitespace.
        if not text.strip():
            continue

        # Split one source record while preserving its metadata.
        split_documents = splitter.create_documents(
            texts=[text],
            metadatas=[metadata.copy()],
        )

        for chunk_index, split_document in enumerate(
            split_documents,
            start=1,
        ):
            chunk_metadata = {
                **split_document.metadata,
                "chunk_id": str(uuid4()),
                "chunk_index": chunk_index,
            }

            chunks.append({
                "text": split_document.page_content,
                "metadata": chunk_metadata,
            })

    return chunks