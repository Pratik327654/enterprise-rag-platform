
import logging

from sentence_transformers import CrossEncoder

from app.core.exceptions import RetrievalError

from app.core.config import settings



logger = logging.getLogger(__name__)

DEFAULT_RERANKER_MODEL = settings.RERANKER_MODEL


class DocumentReranker:
    """
    Rerank retrieved document chunks using a Cross-Encoder model.

    The model evaluates each query-document pair and assigns
    a relevance score. Higher scores indicate greater relevance.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
        model=None,
    ):
        self.model_name = model_name
        self.model = model

    def _load_model(self):
        """Load the Cross-Encoder model lazily and reuse it."""

        if self.model is None:
            try:
                logger.info(
                    "Loading reranker model: %s",
                    self.model_name,
                )

                self.model = CrossEncoder(self.model_name)

                logger.info("Reranker model loaded successfully.")

            except Exception as error:
                raise RetrievalError(
                    f"Failed to load reranker model: {error}"
                ) from error

        return self.model

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
        top_n: int = 3,
    ) -> list[dict]:
        """
        Reorder retrieved chunks based on Cross-Encoder relevance scores.

        Returns the highest-scoring top_n chunks with rerank scores
        and their updated ranking positions.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        if not isinstance(retrieved_chunks, list):
            raise ValueError("Retrieved chunks must be a list.")

        if (
            not isinstance(top_n, int)
            or isinstance(top_n, bool)
            or top_n <= 0
        ):
            raise ValueError("top_n must be a positive integer.")

        if not retrieved_chunks:
            return []

        query_text = query.strip()
        pairs = []

        for chunk in retrieved_chunks:
            if not isinstance(chunk, dict):
                raise ValueError(
                    "Each retrieved chunk must be a dictionary."
                )

            text = chunk.get("text")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    "Each retrieved chunk must contain non-empty text."
                )

            pairs.append((query_text, text))

        try:
            model = self._load_model()

            scores = model.predict(
                pairs,
                show_progress_bar=False,
            )

            if len(scores) != len(retrieved_chunks):
                raise RetrievalError(
                    "Reranking score count does not match "
                    "the number of retrieved chunks."
                )

            scored_chunks = []

            for chunk, score in zip(retrieved_chunks, scores):
                scored_chunks.append({
                    **chunk,
                    "rerank_score": float(score),
                })

            ranked_chunks = sorted(
                scored_chunks,
                key=lambda item: item["rerank_score"],
                reverse=True,
            )

            final_results = []

            for rank, chunk in enumerate(
                ranked_chunks[:top_n],
                start=1,
            ):
                final_results.append({
                    **chunk,
                    "rerank_rank": rank,
                })

            logger.info(
                "Reranked %d chunks and selected top %d.",
                len(retrieved_chunks),
                len(final_results),
            )

            return final_results

        except RetrievalError:
            raise

        except Exception as error:
            raise RetrievalError(
                f"Failed to rerank retrieved chunks: {error}"
            ) from error
