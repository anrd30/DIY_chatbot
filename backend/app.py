# app.py
from fastapi import FastAPI, UploadFile, File
from typing import List
from utils import parse_file
from chunker import chunk_text
from embeddings import get_embeddings_model
from vectorstore import build_vectorstore, query_vectorstore
import ollama
from fastapi.middleware.cors import CORSMiddleware
import io
from pydantic import BaseModel

app = FastAPI(title="RAG Chatbot API")

# Global variable to store vectorstore
vectorstore = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Endpoint 1: Build DB
# =========================
@app.post("/build_db/")
async def build_db(
    files: List[UploadFile] = File(...),
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
):
    global vectorstore
    all_texts = []

    # Parse each uploaded file
    for f in files:
        content = await f.read()
        if f.filename.endswith(".pdf"):
            with open("temp.pdf", "wb") as temp:
                temp.write(content)
            text = parse_file("temp.pdf")
        elif f.filename.endswith(".csv"):
            df = io.BytesIO(content)
            text = parse_file(df)
        else:
            return {"error": f"Unsupported file type: {f.filename}"}
        all_texts.append(text)

    combined_text = " ".join(all_texts)
    chunks = chunk_text(combined_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # Get embedding model (not embeddings)
    embeddings_model = get_embeddings_model(model_name=embedding_model)
    # Build ChromaDB vector store
    vectorstore = build_vectorstore(chunks, embeddings_model, collection_name="rag_db")

    return {"status": "database built", "num_chunks": len(chunks)}


# =========================
# Endpoint 2: Query RAG
# =========================


# Pydantic model for query request
class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 5

@app.post("/query/")
async def query_rag(request: QueryRequest):
    global vectorstore
    if not vectorstore:
        return {"error": "Vector store not built yet. Please build database first."}

    prompt = request.prompt
    top_k = request.top_k

    # Retrieve top_k chunks
    retrieved_chunks = query_vectorstore(vectorstore, prompt, top_k=top_k)
    context = " ".join(retrieved_chunks)

    # Create prompt for LLM
    llm_prompt = f"Answer the question based on the context below:\n\n{context}\n\nQuestion: {prompt}"
    response = ollama.chat(
        model="qwen3:1.7b",
        messages=[{"role": "user", "content": llm_prompt}]
    )

    return {
        "answer": response,
        "retrieved_chunks": retrieved_chunks
    }

# =========================
# Endpoint 3: Status
# =========================
@app.get("/status/")
async def status():
    global vectorstore
    if vectorstore:
        return {"vector_store_ready": True, "num_chunks": len(vectorstore._collection.get()["documents"])}
    else:
        return {"vector_store_ready": False, "num_chunks": 0}


# =========================
# Run with:
# uvicorn app:app --reload
# =========================
