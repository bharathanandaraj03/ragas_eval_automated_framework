"""Load docs, split into chunks, embed, and store in local Qdrant."""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_app.settings import get_settings


def ingest() -> int:
    s= get_settings()
    docs = DirectoryLoader(
        s.docs_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    ).load()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size = s.chunk_size,
        chunk_overlap = s.chunk_overlap,
        add_start_index = True,
    ).split_documents(docs)

    QdrantVectorStore.from_documents(
        chunks,
        embedding=OpenAIEmbeddings(model=s.embedding_model,
                                   api_key=s.openai_api_key),
                                    path = s.qdrant_path,
                                    collection_name = s.collection,
                                    force_recreate = True,                               
    )
    return len(chunks)

if __name__ == "__main__":
    print(f"Ingested {ingest()} chunks")