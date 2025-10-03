# app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List, Optional
from chunker import chunk_text
from embeddings import get_embeddings_model
from vectorstore import build_vectorstore, query_vectorstore
import ollama
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from starlette.responses import FileResponse
import shutil
import tempfile
from convert_to_json import convert_to_json
import gc, time

app = FastAPI(title="RAG Chatbot API")
DB_DIR = "vector_db"

# Global variable to store vectorstore
vectorstore = None

def _safe_rmtree(path, retries=5, delay=0.25):
    last = None
    for _ in range(retries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError as e:
            last = e
            time.sleep(delay)
    if last:
        raise last

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 5
    llm_model: str

@app.post("/build_db/")
async def build_db(
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(50),
    embedding_model: str = Form("sentence-transformers/all-MiniLM-L6-v2"),
    ocr_lang: str = Form("eng"),
):
    global vectorstore
    
    # release any open handles then delete the folder safely (Windows)
    if vectorstore is not None:
        try:
            vectorstore.persist()
        except Exception:
            pass
        vectorstore = None
        gc.collect()

    if os.path.exists(DB_DIR):
        _safe_rmtree(DB_DIR)
    os.makedirs(DB_DIR, exist_ok=True)

    temp_files = []  # make sure this exists even if an error happens

    try:
        all_texts = []
        preview_lines = []
        
        for f in files:
            if not f.filename:
                continue
                
            content = await f.read()
            if not content:
                continue
                
            # Create temp file with proper cleanup
            temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(f.filename)[1])
            temp_files.append(temp_path)
            
            try:
                with os.fdopen(temp_fd, "wb") as temp:
                    temp.write(content)

                # Convert to JSON
                json_data = convert_to_json(temp_path, ocr_lang=ocr_lang)
                for page in json_data["pages"]:
                    text = page.get("content_en") or page.get("content_original", "")
                    cleaned = text.replace("\n", " ").strip()
                    if cleaned:
                        all_texts.append(cleaned)
                        if len(preview_lines) < 10:
                            preview_lines.append(f"--- From file: {f.filename}, page {page['page_number']} ---")
                            preview_lines.append(cleaned[:500] + ("..." if len(cleaned) > 500 else ""))
                            preview_lines.append("")
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        if not all_texts:
            raise HTTPException(status_code=400, detail="No valid content found in uploaded files")

        combined_text = " ".join(all_texts)
        chunks = chunk_text(combined_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        embeddings_model = get_embeddings_model(model_name=embedding_model)
        vectorstore = build_vectorstore(chunks, embeddings_model, collection_name="rag_db", persist_directory=DB_DIR)
        
        return {"status": "database built", "num_chunks": len(chunks), "preview": preview_lines}
        
    except Exception as e:
        # Clean up any remaining temp files
        for p in temp_files:
            if os.path.exists(p):
                os.unlink(p)
        raise HTTPException(status_code=500, detail=f"Error building database: {str(e)}")

@app.get("/download_db/")
async def download_db():
    shutil.make_archive("vector_db_backup", "zip", "vector_db")
    return FileResponse("vector_db_backup.zip", filename="vector_db_backup.zip")


# =========================
# Endpoint 2: Query RAG
# =========================

@app.post("/query/")
async def query_rag(request: QueryRequest):
    global vectorstore
    if not vectorstore:
        raise HTTPException(status_code=400, detail="Vector store not built yet. Please build database first.")

    try:
        # Retrieve top_k chunks
        retrieved_chunks = query_vectorstore(vectorstore, request.prompt, top_k=request.top_k)
        context = " ".join(retrieved_chunks)

        # Create prompt for LLM
        llm_prompt = f"Answer the question based on the context below:\n\n{context}\n\nQuestion: {request.prompt}"
        response = ollama.chat(
            model=request.llm_model,  # Use model from request
            messages=[{"role": "user", "content": llm_prompt}]
        )

        return {
            "answer": response,
            "retrieved_chunks": retrieved_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying: {str(e)}")

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
