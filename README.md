# OS Chatbot

A full-stack chatbot application with:
- **Python backend** for embeddings, vector store, and LLM orchestration.
- **Next.js frontend** with a dropdown to select LLM models (e.g., Qwen) and set custom instructions.
- Supports document uploads, chunking, and querying using embeddings.

---

## Features
- Upload PDFs/CSVs and chunk them for embeddings
- Choose embedding model (e.g., sentence-transformers)
- Set custom instruction prompts for the LLM
- Chat interface with responses from uploaded documents
- Python + FastAPI backend
- Next.js + Tailwind frontend

---

## Project Structure
S_chatbot/
│── backend/
│ ├── app.py # FastAPI backend entry
│ ├── chunker.py # Document chunking logic
│ ├── embeddings.py # Embeddings generator
│ ├── vectorstore.py # Vector store integration
│ ├── utils.py # Utility functions
│ └── requirements.txt # Python dependencies
│
│── frontend/
│ ├── pages/ # Next.js pages
│ ├── components/ # React components
│ ├── styles/ # Tailwind CSS styles
│ └── package.json # Frontend dependencies
│
│── .gitignore
│── README.md





---

## Setup Instructions

### Backend
```bash
cd backend
python -m venv venv
# Activate the virtual environment:
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate


###FRONTEND
cd frontend
npm install
npm run dev


MIT LICENSE 
This one file covers everything: setup, structure, features, and contribution notes.  

If you want, I can also write a **minimal `.gitignore`** specifically for this repo so you never add `venv` or `__pycache__` files again. Do you want me to do that?


pip install -r requirements.txt
python app.py
