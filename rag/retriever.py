from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_DB_PATH = "vectorstore"

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

db = FAISS.load_local(
    VECTOR_DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)


def get_context(query):

    docs = db.similarity_search(
        query,
        k=3
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    sources = list(
        set(
            [
                doc.metadata.get("source", "")
                for doc in docs
            ]
        )
    )

    return {
        "context": context,
        "sources": sources
    }