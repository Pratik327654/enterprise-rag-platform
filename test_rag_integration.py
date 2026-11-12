

import logging
import tempfile
import gc
import time
from pathlib import Path

from app.core.config import settings
from app.pipeline.rag_pipeline import RAGPipeline
from app.embeddings.embedding_generator import EmbeddingGenerator
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import DocumentRetriever
from app.reranking.reranker import DocumentReranker
from app.generation.generator import LLMGenerator


logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parent

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "employee_policy_sample.pdf"
)


def main():

    print("\n========================================")
    print("REAL END-TO-END RAG INTEGRATION TEST")
    print("========================================")

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Sample PDF not found: {PDF_PATH}"
        )

    print("\n[1] PDF VERIFICATION")
    print(f"PDF found: {PDF_PATH.name}")

    temp_directory = tempfile.mkdtemp(
        prefix="rag_integration_"
    )

    vector_store = None
    pipeline = None

    try:

        # Initialize shared components
        print("\n[2] INITIALIZING COMPONENTS")

        embedding_generator = EmbeddingGenerator()

        vector_store = ChromaVectorStore(
            persist_directory=temp_directory,
            collection_name="integration_test_documents",
        )

        retriever = DocumentRetriever(
            embedding_generator=embedding_generator,
            vector_store=vector_store,
        )

        reranker = DocumentReranker()
        generator = LLMGenerator()

        pipeline = RAGPipeline(
            embedding_generator=embedding_generator,
            vector_store=vector_store,
            retriever=retriever,
            reranker=reranker,
            generator=generator,
        )

        print("All components initialized.")

        # Document ingestion
        print("\n[3] DOCUMENT INGESTION")

        ingestion_result = pipeline.ingest_document(
            str(PDF_PATH)
        )

        print("\n--- INGESTION RESULT ---")
        print(ingestion_result)

        assert ingestion_result["status"] == "success"
        assert ingestion_result["chunks_stored"] > 0

        # Verify ChromaDB
        print("\n[4] CHROMADB VERIFICATION")

        stored_count = vector_store.count()

        print("Stored chunks:", stored_count)

        assert stored_count == ingestion_result["chunks_stored"]

        # User question
        query = "How many annual leave days do employees receive?"

        # Retrieval debug
        print("\n[5] RETRIEVAL DEBUG")

        retrieved_chunks = pipeline.retriever.retrieve(
            query=query,
            top_k=5,
        )

        print("Retrieved chunks:", len(retrieved_chunks))

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            print(f"\nRetrieved Chunk {index}")
            print("Text:", chunk["text"])
            print("Metadata:", chunk["metadata"])
            print("Distance:", chunk["distance"])

        assert retrieved_chunks, "No chunks retrieved."

        # Reranking debug
        print("\n[6] RERANKING DEBUG")

        reranked_chunks = pipeline.reranker.rerank(
            query=query,
            retrieved_chunks=retrieved_chunks,
            top_n=3,
        )

        print("Reranked chunks:", len(reranked_chunks))

        for index, chunk in enumerate(
            reranked_chunks,
            start=1,
        ):
            print(f"\nReranked Chunk {index}")
            print("Text:", chunk["text"])
            print("Metadata:", chunk["metadata"])
            print("Rerank score:", chunk["rerank_score"])

        assert reranked_chunks, "No chunks after reranking."

        # Actual LLM generation using pipeline
        print("\n[7] LLM GENERATION")

        result = pipeline.ask(
            query=query,
            top_k=5,
            top_n=3,
        )

        print("\n--- GENERATED ANSWER ---")
        print(result["answer"])

        print("\n--- SOURCE METADATA ---")

        for source in result["sources"]:
            print(source)

        print("\n--- MODEL ---")
        print(result["model"])

        assert result["answer"].strip()
        assert result["sources"]
        assert result["model"] == settings.LLM_MODEL

        # Check expected information
        if "20" in result["answer"]:
            print("\nPASS: Annual leave answer found.")
        else:
            print(
                "\nWARNING: Expected answer not clearly found."
            )

        # Missing-context test
        print("\n[8] MISSING CONTEXT TEST")

        missing_result = pipeline.ask(
            query="Who is the CEO of this company?",
            top_k=5,
            top_n=3,
            where={
                "source": "nonexistent_document.pdf"
            },
        )

        print("\n--- MISSING CONTEXT ANSWER ---")
        print(missing_result["answer"])

        assert missing_result["sources"] == []
        assert "enough information" in (
            missing_result["answer"].lower()
        )

        print("\nPASS: Missing-context handling verified.")

        print("\n========================================")
        print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("========================================")

    finally:
        print("\n[CLEANUP]")
        print("Temporary ChromaDB directory:")
        print(temp_directory)

        pipeline = None
        retriever = None
        reranker = None
        generator = None
        embedding_generator = None
        vector_store = None

        gc.collect()

        print(
            "Database handles released. "
            "Temporary folder can be deleted after process exit."
        )


if __name__ == "__main__":
    main()
