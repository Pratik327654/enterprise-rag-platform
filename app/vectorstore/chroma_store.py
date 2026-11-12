
import logging
from math import isfinite
from pathlib import Path

import chromadb

from app.core.config import settings
from app.core.exceptions import RetrievalError


logger = logging.getLogger(__name__)

COLLECTION_NAME = "enterprise_rag_documents"
EMBEDDING_DIMENSION = 384


class ChromaVectorStore:
    """
    Persistent vector store for document chunks and embeddings.

    Stores chunk text, metadata, and vectors in ChromaDB.
    Supports upserting records and semantic similarity search.
    """

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str = COLLECTION_NAME,
    ):
        self.persist_directory = str(
            persist_directory or settings.CHROMA_PERSIST_DIR
        )
        self.collection_name = collection_name

        self.client = None
        self.collection = None

        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize the persistent ChromaDB client and collection."""

        try:
            Path(self.persist_directory).mkdir(
                parents=True,
                exist_ok=True,
            )

            self.client = chromadb.PersistentClient(
                path=self.persist_directory
            )

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(
                "ChromaDB collection initialized: %s",
                self.collection_name,
            )

        except Exception as error:
            raise RetrievalError(
                f"Failed to initialize ChromaDB: {error}"
            ) from error

    @staticmethod
    def _validate_embedding(embedding: list[float]) -> list[float]:
        """Validate and normalize the input representation of a vector."""

        if not isinstance(embedding, (list, tuple)):
            raise ValueError("Embedding must be a list or tuple.")

        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Embedding must contain {EMBEDDING_DIMENSION} dimensions."
            )

        try:
            values = [float(value) for value in embedding]
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Embedding must contain numerical values."
            ) from error

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "Embedding contains invalid numerical values."
            )

        return values

    @staticmethod
    def _validate_metadata(metadata: dict) -> dict:
        """Ensure metadata contains ChromaDB-compatible scalar values."""

        if not isinstance(metadata, dict):
            raise ValueError("Chunk metadata must be a dictionary.")

        if not metadata:
            raise ValueError("Chunk metadata cannot be empty.")

        for key, value in metadata.items():
            if not isinstance(key, str) or not key:
                raise ValueError("Metadata keys must be non-empty strings.")

            if isinstance(value, bool):
                continue

            if isinstance(value, (str, int, float)):
                if isinstance(value, float) and not isfinite(value):
                    raise ValueError(
                        f"Metadata value for '{key}' must be finite."
                    )
                continue

            raise ValueError(
                f"Unsupported metadata value for '{key}'. "
                "Use string, integer, float, or boolean."
            )

        return metadata.copy()

    def add_embeddings(self, embedded_chunks: list[dict]) -> int:
        """
        Store embedded chunks in ChromaDB.

        Uses upsert so an existing chunk ID can be updated.
        Returns the number of processed chunks.
        """

        if not isinstance(embedded_chunks, list):
            raise ValueError("Embedded chunks must be provided as a list.")

        if not embedded_chunks:
            return 0

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for chunk in embedded_chunks:
            if not isinstance(chunk, dict):
                raise ValueError("Each embedded chunk must be a dictionary.")

            text = chunk.get("text")
            metadata = chunk.get("metadata")
            embedding = chunk.get("embedding")

            if not isinstance(text, str) or not text.strip():
                raise ValueError("Each chunk must contain non-empty text.")

            if not isinstance(metadata, dict):
                raise ValueError("Each chunk must contain metadata.")

            chunk_id = metadata.get("chunk_id")

            if not isinstance(chunk_id, str) or not chunk_id.strip():
                raise ValueError(
                    "Each chunk must have a valid chunk_id in metadata."
                )

            validated_metadata = self._validate_metadata(metadata)
            validated_embedding = self._validate_embedding(embedding)

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(validated_metadata)
            embeddings.append(validated_embedding)

        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )

            logger.info(
                "Stored or updated %d embedded chunks.",
                len(ids),
            )

            return len(ids)

        except Exception as error:
            raise RetrievalError(
                f"Failed to store embeddings: {error}"
            ) from error

    
    
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError("top_k must be a positive integer.")

        if where is not None and not isinstance(where, dict):
            raise ValueError("Metadata filter must be a dictionary.")

        validated_embedding = self._validate_embedding(query_embedding)

        try:
            if self.collection.count() == 0:
                return []

            query_arguments = {
                "query_embeddings": [validated_embedding],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"],
            }

            if where is not None:
                query_arguments["where"] = where

            results = self.collection.query(**query_arguments)

            retrieved_chunks = []

            for chunk_id, document, metadata, distance in zip(
                results.get("ids", [[]])[0],
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
                results.get("distances", [[]])[0],
            ):
                retrieved_chunks.append({
                    "id": chunk_id,
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                })

            logger.info(
                "Retrieved %d relevant chunks.",
                len(retrieved_chunks),
            )

            return retrieved_chunks

        except Exception as error:
            raise RetrievalError(
                f"Similarity search failed: {error}"
            ) from error

    def count(self) -> int:
        """Return the number of records in the collection."""

        try:
            return self.collection.count()

        except Exception as error:
            raise RetrievalError(
                f"Failed to count stored chunks: {error}"
            ) from error
