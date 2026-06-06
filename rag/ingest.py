from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_PATH = "docs"
VECTOR_DB_PATH = "vectorstore"


def load_documents():
    documents = []

    pdf_files = Path(DOCS_PATH).glob("*.pdf")

    for pdf in pdf_files:
        loader = PyPDFLoader(str(pdf))
        documents.extend(loader.load())

    return documents


def build_vector_db():

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    db = FAISS.from_documents(
        chunks,
        embeddings
    )

    db.save_local(VECTOR_DB_PATH)

    print("Vector DB Created Successfully")


if __name__ == "__main__":
    build_vector_db()