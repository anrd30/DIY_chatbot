from langchain_community.embeddings import HuggingFaceEmbeddings
import torch

def get_embeddings_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using {device} for embeddings...")

    embeddings_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device}
    )
    return embeddings_model
