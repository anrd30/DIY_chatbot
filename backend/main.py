from utils import parse_file
from chunker import chunk_text
from embeddings import get_embeddings_model
from vectorstore import build_vectorstore, query_vectorstore
from convert_to_json import convert_to_json  # if using OCR
import os

def main():
    # ================================
    # STEP 1: Parse and Preview Files
    # ================================
    files = ["Dryland Agriculture.pdf"]
    ocr_lang = "eng"  # 👈 change this if needed
    all_texts = []

    print("=== File Parsing & Preview ===")
    for f in files:
        try:
            temp_path = f"temp{os.path.splitext(f)[1]}"
            with open(f, "rb") as src, open(temp_path, "wb") as dst:
                dst.write(src.read())

            json_data = convert_to_json(temp_path, ocr_lang=ocr_lang)
            print(f"[OK] Parsed {f}: {len(json_data['pages'])} pages")

            for page in json_data["pages"][:3]:  # 👈 preview first 3 pages
                print(f"\n--- {f}, Page {page['page_number']} ---")
                preview = page.get("content_en") or page.get("content_original", "")
                print(preview[:500] + ("..." if len(preview) > 500 else ""))

                cleaned = preview.replace("\n", " ").strip()
                if cleaned:
                    all_texts.append(cleaned)

        except Exception as e:
            print(f"[ERROR] {f}: {e}")

    # ================================
    # STEP 2: Chunking
    # ================================
    print("\n=== Chunking ===")
    combined_text = " ".join(all_texts)
    print(f"Total combined text length: {len(combined_text)} characters")

    chunks = chunk_text(combined_text, chunk_size=500, chunk_overlap=50)
    print(f"Total chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks[:2]):
        print(f"\nChunk {i+1}:\n{chunk[:300]}...")

    # ================================
    # STEP 3: Embeddings
    # ================================
    print("\n=== Embeddings ===")
    embedding_object = get_embeddings_model(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Embedding object created.")

    # ================================
    # STEP 4: Build Vector Store
    # ================================
    print("\n=== Building Vector Store ===")
    vectorstore = build_vectorstore(chunks, embedding_object, collection_name="rag_db")
    print("Vector store created.")

    # ================================
    # STEP 5: Query Test
    # ================================
    print("\n=== Query Test ===")
    test_query = "What are the challenges of dryland agriculture?"
    results = query_vectorstore(vectorstore, test_query, top_k=3)
    print(f"Top {len(results)} chunks for query: '{test_query}'")
    for idx, r in enumerate(results):
        print(f"\nChunk {idx+1}:\n{r[:300]}...")

if __name__ == "__main__":
    main()