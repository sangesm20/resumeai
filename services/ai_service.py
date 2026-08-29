import io
import requests

from PyPDF2 import PdfReader
from docx import Document
from core.config import settings


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
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
    response = requests.post(
        settings.HF_API_URL,
        headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
        json={"inputs": text.replace("\n", " ").strip()},
        timeout=60,
    )
    response.raise_for_status()

    embedding = response.json()
    return embedding[0] if embedding and isinstance(embedding[0], list) else embedding