import io
from PyPDF2 import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """Extracts text strictly from raw in-memory BYTEA content."""
    text = ""
    file_stream = io.BytesIO(file_bytes)
    
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(file_stream)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif filename.lower().endswith(".docx"):
        doc = Document(file_stream)
        for para in doc.paragraphs:
            text += para.text + "\n"
            
    return text.strip()

def generate_embedding(text: str) -> list:
    cleaned = text.replace("\n", " ").strip()
    return model.encode(cleaned).tolist()