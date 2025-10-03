```markdown
# DIY RAG Bot
Fast, private, and simple Retrieval-Augmented Generation (RAG) over your own documents. Upload files → build a vector database → chat with your knowledge. No cloud required.

## Highlights
- Works locally with your files (PDF, CSV, TXT, DOCX, PPTX) + OCR language selection
- One-click “Use Recommended Size” (based on extracted text length)
- Clean preview of extracted snippets and chunk count after build
- Switch LLM model and instruction per question (no rebuild needed)
- Wide, responsive UI built with Tailwind + Glassmorphism
- Download your built database as a zip

## Stack
- Backend: FastAPI, Chroma, LangChain, HuggingFace embeddings, Ollama
- Frontend: React (Vite) + Tailwind
- Models: Local via Ollama (e.g., `qwen3:1.7b`, `tinyllama`, `mistral`, `phi`)

## Prerequisites
- Python 3.10+ and Node 18+
- Ollama installed (`https://ollama.com`)
- Pull at least one model, e.g.:
```bash
ollama pull qwen3:1.7b
```

## Quick Start

### 1) Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```
Backend runs at `http://localhost:8000`.

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

## How to Use
1. Open the UI at `http://localhost:3000`.
2. Drag & drop your files.
3. Choose OCR language and embedding model.
4. Click “Use Recommended Size” to auto-set chunk size/overlap (based on extracted text).
5. Click “Build Knowledge DB”:
   - You’ll see: status, number of chunks, and a preview of extracted snippets.
6. Ask questions:
   - Pick an LLM from the dropdown (e.g., qwen3, tinyllama, mistral, phi).
   - Add an “LLM Instruction” (e.g., “Answer concisely”)—this can be changed anytime without rebuilding.
   - Send your question and view the response.

Notes:
- Rebuilding replaces the previous database (non-append by design).
- You can change LLM or instruction for each query without rebuilding.

## LLM Models (Ollama)
The dropdown includes:
- qwen3:1.7b — Fast & efficient, good for general tasks
- tinyllama:latest — Ultra-fast for simple prompts
- mistral:7b-instruct-q4_K_M — Most capable for complex queries
- phi:latest — Great for reasoning

Pull models as needed:
```bash
ollama pull mistral:7b-instruct-q4_K_M
ollama pull tinyllama:latest
ollama pull phi:latest
```

## API (current)
- POST `/build_db/` (multipart form)
  - `files[]`, `chunk_size`, `chunk_overlap`, `embedding_model`, `ocr_lang`
  - Response: `{ status, num_chunks, preview }`
- POST `/query/` (JSON)
  - `{ prompt, top_k, llm_model }`
  - Response: `{ answer, retrieved_chunks }`
- GET `/status/`
  - Response: `{ vector_store_ready, num_chunks }`
- GET `/download_db/`
  - Returns a zip of `vector_db`

## Under the Hood
- Files are parsed and converted to normalized JSON (`convert_to_json`), including OCR when needed.
- Text is cleaned and chunked (`chunker`), then embedded.
- Chunks are stored in Chroma with embeddings for fast similarity search.
- On query, top-k chunks are retrieved and passed as context to the chosen LLM via Ollama.

High-level flow:
```
Upload → Convert/OCR → Chunk → Embed → Chroma
                          ↓
                       Preview
                          ↓
Query → Retrieve Top-k → Compose Prompt → Ollama → Answer
```

## Windows Notes (important)
Windows can lock Chroma files during rebuilds. The app:
- Releases the in-memory vectorstore
- Triggers garbage collection
- Safely clears and recreates `vector_db`

If you still see `PermissionError [WinError 32]`, ensure no other processes are accessing `vector_db` and retry.

## Troubleshooting
- Preview not shown:
  - Ensure backend is running and the response includes `"preview"`. Restart backend after code edits.
- “Vector store not built yet”:
  - Build the DB first in the UI, then query.
- Verbose answers / “thinking” text:
  - Use a short instruction, e.g., “Answer concisely using only the provided context.”
- Ollama model missing:
  - Run `ollama pull <model>` and select it in the dropdown.

## Performance Tips
- For large corpora, start with:
  - Chunk size: 700–1000
  - Overlap: 70–100
- Use a smaller LLM (e.g., tinyllama) when prototyping; switch to larger models (e.g., mistral) for complex tasks.
- Keep an eye on the number of chunks—very small chunk sizes can increase retrieval noise.

## Roadmap
- Append mode (add docs without replacing)
- Query history and source highlighting
- Optional re-ranking
- Cloud storage integrations (Drive/Dropbox)
- One-click export/import of configuration

## License
MIT
```
