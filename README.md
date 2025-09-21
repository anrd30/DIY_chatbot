# RAG Chatbot

A minimalist, modern Retrieval-Augmented Generation (RAG) chatbot built with **React** (frontend) and **FastAPI** (backend).  
Allows you to upload PDF/CSV files, build a knowledge database, and chat with a custom LLM with instructions.

---

## Features

- Upload multiple PDF/CSV files
- Configure:
  - Chunk size & overlap
  - Embedding model (currently supports Sentence-Transformers)
  - LLM model (e.g., Qwen 1.7B)
  - Instruction template for LLM
- Interactive chat with RAG-powered responses
- Maintains conversation history

---

## Tech Stack

- Frontend: React, TypeScript, Tailwind CSS, React Dropzone
- Backend: FastAPI, Python, ChromaDB, Ollama
- AI: Sentence-Transformers for embeddings, Qwen LLM for answers

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
