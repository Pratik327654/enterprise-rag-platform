import json
from pathlib import Path
from collections import defaultdict

from app.vectorstore.chroma_store import ChromaVectorStore


DATASET_PATH = Path("app/evaluation/dataset.json")
OUTPUT_PATH = Path("app/evaluation/chunk_candidates.json")


def main():
    with DATASET_PATH.open("r", encoding="utf-8-sig") as file:
        questions = json.load(file)

    store = ChromaVectorStore()
    data = store.collection.get(
        include=["metadatas", "documents"]
    )

    document_chunks = defaultdict(list)

    for chunk_id, metadata, text in zip(
        data["ids"], data["metadatas"], data["documents"]
    ):
        document_chunks[metadata.get("source", "")].append({
            "chunk_id": chunk_id,
            "page_number": metadata.get("page_number"),
            "chunk_index": metadata.get("chunk_index"),
            "text": text
        })

    results = []

    for question in questions:
        document_name = question["document"]

        matching_chunks = [
            chunk
            for source, chunks in document_chunks.items()
            if source.endswith(document_name)
            for chunk in chunks
        ]

        results.append({
            "id": question["id"],
            "question": question["question"],
            "document": document_name,
            "candidates": matching_chunks
        })

    OUTPUT_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("TOTAL QUESTIONS:", len(results))
    print("OUTPUT FILE:", OUTPUT_PATH)

    for item in results:
        print(
            f'{item["id"]}: '
            f'{len(item["candidates"])} candidate chunks'
        )


if __name__ == "__main__":
    main()
