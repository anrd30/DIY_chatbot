# main.py
from utils import parse_file
from chunker import chunk_text
from embeddings import get_embeddings
from vectorstore import build_vectorstore, query_vectorstore

def main():
    # ================================
    # STEP 1: Test File Parsing
    # ================================
    files = ["paper.pdf"]
    all_texts = []
    print("=== Testing parse_file ===")
    for f in files:
        try:
            text = parse_file(f)
            all_texts.append(text)
            print(f"[OK] Parsed {f}: {len(text)} characters")
            print(f"Preview: {text[:200]}...\n")
        except Exception as e:
            print(f"[ERROR] {f}: {e}")

    # ================================
    # STEP 2: Test Text Chunking
    # ================================
    print("=== Testing chunk_text ===")
    combined_text = " ".join(all_texts)
    print(f"Total combined text length: {len(combined_text)} characters")
    chunks = chunk_text(combined_text, chunk_size=500, chunk_overlap=50)
    print(f"Total chunks created: {len(chunks)}")
    print("Preview of first 2 chunks:")
    for i, chunk in enumerate(chunks[:2]):
        print(f"Chunk {i+1}: {chunk[:200]}...\n")

    # ================================
    # STEP 3: Get Embeddings Object
    # ================================
    print("=== Testing get_embeddings ===")
    embedding_object = get_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Embedding object created (Chroma will handle computation internally).\n")

    # ================================
    # STEP 4: Build Vector Store
    # ================================
    print("=== Testing build_vectorstore ===")
    vectorstore = build_vectorstore(chunks, embedding_object, collection_name="rag_db")
    print("Vector store created successfully.\n")

    # ================================
    # STEP 5: Test Similarity Search
    # ================================
    print("=== Testing query_vectorstore ===")
    test_query = "Non Linear Optmization"
    results = query_vectorstore(vectorstore, test_query, top_k=3)
    print(f"Top {len(results)} retrieved chunks for query: '{test_query}'\n")
    for idx, r in enumerate(results):
        print(f"Chunk {idx+1}:\n{r[:300]}...\n")

if __name__ == "__main__":
    main()
