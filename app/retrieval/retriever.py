
import logging

from app.embeddings.embedding_generator import EmbeddingGenerator
from app.vectorstore.chroma_store import ChromaVectorStore


logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Retrieve relevant document chunks for a user's question.

    Coordinates query embedding generation and ChromaDB search.
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator | None = None,
        vector_store: ChromaVectorStore | None = None,
    ):
        self.embedding_generator = (
            embedding_generator or EmbeddingGenerator()
        )
        self.vector_store = vector_store or ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        """
        Convert a user query into an embedding and retrieve
        the most relevant document chunks.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError("top_k must be a positive integer.")

        if where is not None and not isinstance(where, dict):
            raise ValueError("Metadata filter must be a dictionary.")

        try:
            query_text = query.strip()

            query_chunks = [{
                "text": query_text,
                "metadata": {"record_type": "query"},
            }]

            embedded_query = (
                self.embedding_generator.generate_embeddings(
                    query_chunks,
                    batch_size=1,
                )
            )

            if len(embedded_query) != 1:
                raise ValueError(
                    "Query embedding generation returned an "
                    "unexpected number of results."
                )

            query_embedding = embedded_query[0]["embedding"]

            results = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                where=where,
            )

            logger.info(
                "Retrieved %d chunks for user query.",
                len(results),
            )

            return results

        except Exception:
            logger.exception("Document retrieval failed.")
            raise
