
import logging

from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.exceptions import GenerationError
from app.generation.prompt_builder import build_rag_prompt


logger = logging.getLogger(__name__)


DEFAULT_LLM_MODEL = settings.LLM_MODEL
DEFAULT_OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL


class LLMGenerator:
    """
    Generate grounded answers using a local Ollama LLM.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_LLM_MODEL,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        temperature: float = 0.0,
        llm=None,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.llm = llm

        if not isinstance(temperature, (int, float)) or isinstance(
            temperature, bool
        ):
            raise ValueError("Temperature must be a numeric value.")

        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1.")

    def _load_model(self):
        """Load the Ollama model lazily and reuse it."""

        if self.llm is None:
            try:
                logger.info(
                    "Loading LLM model: %s",
                    self.model_name,
                )

                self.llm = ChatOllama(
                    model=self.model_name,
                    base_url=self.base_url,
                    temperature=self.temperature,
                )

                logger.info("LLM model initialized successfully.")

            except Exception as error:
                raise GenerationError(
                    f"Failed to initialize LLM model: {error}"
                ) from error

        return self.llm

    def generate(
        self,
        query: str,
        context_chunks: list[dict],
    ) -> dict:
        """
        Generate an answer using reranked document chunks.

        Returns:
            A dictionary containing answer, sources, and model name.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        if not isinstance(context_chunks, list):
            raise ValueError("Context chunks must be a list.")

        # No context means no LLM call.
        if not context_chunks:
            return {
                "answer": (
                    "I don't have enough information in the "
                    "provided documents to answer this question."
                ),
                "sources": [],
                "model": self.model_name,
            }

        try:
            prompt = build_rag_prompt(
                query=query,
                context_chunks=context_chunks,
            )

            llm = self._load_model()

            response = llm.invoke(prompt)

            

            answer = response.content

            if not isinstance(answer, str) or not answer.strip():
                raise GenerationError(
                    "LLM returned an empty or invalid response."
                )

            sources = []

            for index, chunk in enumerate(context_chunks, start=1):
                metadata = chunk.get("metadata", {})

                source_info = {
                    "source_id": f"S{index}",
                    "source": metadata.get(
                        "source",
                        "Unknown source",
                    ),
                    "page_number": metadata.get("page_number"),
                    "chunk_id": metadata.get("chunk_id"),
                }

                sources.append(source_info)

            result = {
                "answer": answer.strip(),
                "sources": sources,
                "model": self.model_name,
            }

            logger.info(
                "Answer generated successfully using %s.",
                self.model_name,
            )

            return result

        except GenerationError:
            raise

        except Exception as error:
            logger.exception("LLM generation failed.")

            raise GenerationError(
                f"Failed to generate answer: {error}"
            ) from error
