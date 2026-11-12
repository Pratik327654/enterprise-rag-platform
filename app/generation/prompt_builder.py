


def build_rag_prompt(query: str, context_chunks: list[dict]) -> str:
    """Build a concise prompt for grounded document question answering."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    if not isinstance(context_chunks, list):
        raise ValueError("Context chunks must be a list.")

    if not context_chunks:
        raise ValueError("Context chunks cannot be empty.")

    context_sections = []

    for index, chunk in enumerate(context_chunks, start=1):
        if not isinstance(chunk, dict):
            raise ValueError("Each context chunk must be a dictionary.")

        text = chunk.get("text")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Each context chunk must contain non-empty text."
            )

        context_sections.append(f"[S{index}] {text.strip()}")

    context = "\n\n".join(context_sections)

    return f"""Use the following document excerpts to answer the question.

Document excerpts:
{context}

Question: {query.strip()}

Give a short answer based on the excerpts. Include the source reference.
If the excerpts do not contain the answer, say you do not know.

Answer:"""
