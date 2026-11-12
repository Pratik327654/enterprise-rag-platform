import os
from pathlib import Path

from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME = "Enterprise RAG Platform"
    VERSION = "0.1.0"

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "llama3.2:1b"
    )

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
)


settings = Settings()