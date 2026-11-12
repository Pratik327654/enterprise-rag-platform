class RAGPlatformError(Exception):
    """Base exception for the Enterprise RAG Platform."""


class DocumentProcessingError(RAGPlatformError):
    """Raised when document processing fails."""


class EmbeddingError(RAGPlatformError):
    """Raised when embedding generation fails."""


class RetrievalError(RAGPlatformError):
    """Raised when document retrieval fails."""


class GenerationError(RAGPlatformError):
    """Raised when LLM response generation fails."""


class ConfigurationError(RAGPlatformError):
    """Raised when application configuration is invalid."""