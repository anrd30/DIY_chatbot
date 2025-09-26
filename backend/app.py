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
import os
from starlette.responses import FileResponse
import shutil
from langchain.vectorstores import Chroma
app = FastAPI(title="RAG Chatbot API")
DB_DIR = "vector_db"

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
    vectorstore = build_vectorstore(chunks, embeddings_model, collection_name="rag_db", persist_directory=DB_DIR)

    return {"status": "database built", "num_chunks": len(chunks)}

@app.get("/download_db/")
async def download_db():
    shutil.make_archive("vector_db_backup", "zip", "vector_db")
    return FileResponse("vector_db_backup.zip", filename="vector_db_backup.zip")

@app.post("/upload_db/")
async def upload_db(file: UploadFile = File(...)):
    global vectorstore
    import shutil
    import zipfile
    import os

    # Close the existing vectorstore if open
    if vectorstore:
        try:
            vectorstore._collection.persist()  # make sure data is saved
        except:
            pass
        vectorstore = None  # release the object

    # Delete old folder safely
    if os.path.exists("vector_db"):
        import time
        time.sleep(0.2)  # slight delay for Windows file handles
        shutil.rmtree("vector_db", ignore_errors=True)

    # Extract uploaded zip
    with open("temp.zip", "wb") as f:
        f.write(await file.read())
    with zipfile.ZipFile("temp.zip", "r") as zip_ref:
        zip_ref.extractall("vector_db")

    vectorstore = Chroma(persist_directory="vector_db", collection_name="rag_db")  # reload db
    return {"status": "database uploaded"}
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
@app.post("/recommend_chunk_settings/")
async def recommend_chunk_settings(files: List[UploadFile] = File(...)):
    def get_recommendation(file_size_kb):
        if file_size_kb < 50:
            return {"chunk_size": 300, "chunk_overlap": 30}
        elif file_size_kb < 500:
            return {"chunk_size": 600, "chunk_overlap": 60}
        elif file_size_kb < 2000:
            return {"chunk_size": 1000, "chunk_overlap": 100}
        else:
            return {"chunk_size": 1500, "chunk_overlap": 150}

    total_size_kb = 0
    for f in files:
        content = await f.read()
        total_size_kb += len(content) / 1024

    recommendation = get_recommendation(total_size_kb)
    return {
        "recommended_chunk_size": recommendation["chunk_size"],
        "recommended_chunk_overlap": recommendation["chunk_overlap"],
        "total_file_size_kb": round(total_size_kb, 2)
    }

# =========================
# Run with:
# uvicorn app:app --reload
# =========================
