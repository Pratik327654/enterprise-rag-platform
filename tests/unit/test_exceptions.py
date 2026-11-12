import pytest

from app.core.exceptions import (
    RAGPlatformError,
    DocumentProcessingError,
    EmbeddingError,
    RetrievalError,
    GenerationError,
    ConfigurationError,
)


def test_document_processing_error():
    with pytest.raises(DocumentProcessingError):
        raise DocumentProcessingError("PDF processing failed")


def test_embedding_error():
    with pytest.raises(EmbeddingError):
        raise EmbeddingError("Embedding generation failed")


def test_retrieval_error():
    with pytest.raises(RetrievalError):
        raise RetrievalError("No relevant documents found")


def test_generation_error():
    with pytest.raises(GenerationError):
        raise GenerationError("LLM generation failed")


def test_configuration_error():
    with pytest.raises(ConfigurationError):
        raise ConfigurationError("Invalid configuration")


def test_exceptions_inherit_from_base():
    assert issubclass(DocumentProcessingError, RAGPlatformError)
    assert issubclass(EmbeddingError, RAGPlatformError)
    assert issubclass(RetrievalError, RAGPlatformError)
    assert issubclass(GenerationError, RAGPlatformError)
    assert issubclass(ConfigurationError, RAGPlatformError)