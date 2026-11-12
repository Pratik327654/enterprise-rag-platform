import logging
from math import isfinite

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.exceptions import EmbeddingError


logger = logging.getLogger(__name__)

# Dimension for the currently configured all-MiniLM-L6-v2 model.
EMBEDDING_DIMENSION = 384


class EmbeddingGenerator:
    """
    Generate normalized vector embeddings for document chunks.

    The model is loaded lazily and reused across calls.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = None

    def _load_model(self):
        """Load the embedding model only when required."""

        if self.model is None:
            try:
                logger.info(
                    "Loading embedding model: %s",
                    self.model_name,
                )

                self.model = SentenceTransformer(self.model_name)

                logger.info("Embedding model loaded successfully.")

            except Exception as error:
                raise EmbeddingError(
                    f"Failed to load embedding model: {error}"
                ) from error

        return self.model

    def generate_embeddings(
        self,
        chunks: list[dict],
        batch_size: int = 32,
    ) -> list[dict]:
        """
        Generate embeddings for document chunks.

        Each output record contains the original text,
        preserved metadata, and its numerical embedding.
        """

        if batch_size <= 0:
            raise ValueError("Batch size must be greater than zero.")

        if not isinstance(chunks, list):
            raise ValueError("Chunks must be provided as a list.")

        if not chunks:
            return []

        texts = []

        for chunk in chunks:
            if not isinstance(chunk, dict):
                raise ValueError("Each chunk must be a dictionary.")

            text = chunk.get("text")
            metadata = chunk.get("metadata")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    "Each chunk must contain non-empty text."
                )

            if not isinstance(metadata, dict):
                raise ValueError(
                    "Each chunk must contain a metadata dictionary."
                )

            texts.append(text)

        try:
            model = self._load_model()

            vectors = model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            if len(vectors) != len(chunks):
                raise EmbeddingError(
                    "Embedding count does not match chunk count."
                )

            results = []

            for chunk, vector in zip(chunks, vectors):
                vector_values = vector.tolist()

                if len(vector_values) != EMBEDDING_DIMENSION:
                    raise EmbeddingError(
                        "Unexpected embedding dimension: "
                        f"expected {EMBEDDING_DIMENSION}, "
                        f"received {len(vector_values)}."
                    )

                if not all(isfinite(value) for value in vector_values):
                    raise EmbeddingError(
                        "Embedding contains invalid numerical values."
                    )

                results.append({
                    "text": chunk["text"],
                    "metadata": chunk["metadata"].copy(),
                    "embedding": vector_values,
                })

            logger.info(
                "Generated embeddings for %d chunks.",
                len(results),
            )

            return results

        except EmbeddingError:
            raise

        except Exception as error:
            raise EmbeddingError(
                f"Failed to generate embeddings: {error}"
            ) from error