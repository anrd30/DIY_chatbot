from langchain.text_splitter import CharacterTextSplitter

def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Splits text into chunks with specified size and overlap.
    """
    splitter = CharacterTextSplitter(
        separator="",         # split purely by characters
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    return chunks
