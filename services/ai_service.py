import io
import pdfplumber  # type: ignore
from docx import Document

from huggingface_hub import InferenceClient

from core.config import settings


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_text_from_bytes(
    file_bytes: bytes,
    filename: str
) -> str:

    file_stream = io.BytesIO(file_bytes)

    filename_lower = filename.lower()

    text = []

    if filename_lower.endswith(".pdf"):

        with pdfplumber.open(file_stream) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:

                    text.append(page_text)

    elif filename_lower.endswith(".docx"):

        document = Document(file_stream)

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                text.append(paragraph.text)

    else:

        raise ValueError(
            "Unsupported file format"
        )

    return "\n".join(text).strip()


# =========================================================
# EMBEDDING GENERATION
# =========================================================

def generate_embedding(
    text: str
) -> list[float]:

    if not text or not text.strip():

        raise ValueError(
            "Text cannot be empty"
        )

    client = InferenceClient(
        provider="hf-inference",
        api_key=settings.HF_TOKEN
    )

    result = client.feature_extraction(
        text[:12000],
        model=settings.HF_MODEL
    )

    # Convert numpy array → Python list
    embedding = result.tolist()

    # Sometimes the result can contain an extra dimension
    if (
        isinstance(embedding, list)
        and len(embedding) == 1
        and isinstance(embedding[0], list)
    ):

        embedding = embedding[0]

    return [
        float(value)
        for value in embedding
    ]