


from app.graph._workflow import ask_with_graph

print("\n--- LangGraph: Annual Leave Test ---")

result = ask_with_graph(
    query="How many annual leave days are provided per year?",
    top_k=5,
    top_n=3,
)

print("Status:", result["status"])
print("Answer:", result["answer"])
print("Sources:", result["sources"])
print("Model:", result["model"])

assert result["status"] == "success"
assert "20" in result["answer"]

print("\n--- LangGraph: Missing Context Test ---")

missing_result = ask_with_graph(
    query="Who is the CEO of this company?",
    top_k=5,
    top_n=3,
)

print("Status:", missing_result["status"])
print("Answer:", missing_result["answer"])
print("Sources:", missing_result["sources"])

assert missing_result["status"] == "success"
assert "not explicitly stated" in missing_result["answer"].lower()
assert len(missing_result["sources"]) > 0

print("\nBoth LangGraph integration tests passed!")
