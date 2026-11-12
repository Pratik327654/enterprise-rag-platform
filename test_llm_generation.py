

from app.generation.generator import LLMGenerator


generator = LLMGenerator()

context_chunks = [
    {
        "text": (
            "Employees receive 20 days of annual leave "
            "per calendar year. Leave requests must be "
            "submitted through the HR portal."
        ),
        "metadata": {
            "source": "employee_policy.pdf",
            "page_number": 3,
            "chunk_id": "chunk-001",
        },
    }
]

query = query = "Who is the CEO of this company?"

result = generator.generate(
    query=query,
    context_chunks=context_chunks,
)

print("\n--- GENERATED ANSWER ---")
print(result["answer"])

print("\n--- SOURCES / METADATA ---")
for source in result["sources"]:
    print(source)

print("\n--- MODEL ---")
print(result["model"])
