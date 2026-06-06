from rag.retriever import get_context

query = "What is the leave policy?"

result = get_context(query)

print("\nRetrieved Context:\n")
print(result["context"])

print("\nSources:\n")
print(result["sources"])