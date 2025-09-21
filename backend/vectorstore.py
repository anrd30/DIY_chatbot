# vectorstore.py
from langchain.vectorstores import Chroma

def build_vectorstore(chunks, embeddings, collection_name="rag_db"):
    """
    Stores chunks + embeddings in ChromaDB for retrieval.
    """
    vectorstore = Chroma.from_texts(chunks, embedding=embeddings, collection_name=collection_name)
    return vectorstore

def query_vectorstore(vectorstore, query, top_k=5):
    """
    Retrieve top_k chunks relevant to query.
    """
    results = vectorstore.similarity_search(query, k=top_k)
    return [r.page_content for r in results]
