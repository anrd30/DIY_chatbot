# utils.py
import pdfplumber
import pandas as pd

def parse_file(file_path):
    """
    Parses a PDF or CSV file into plain text.
    """
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return text
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        text = " ".join(df.astype(str).values.flatten())
        return text
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
