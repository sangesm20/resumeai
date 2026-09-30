import io
import logging
from PIL import Image
import pytesseract
from pypdf import PdfReader  # PyPDF2 ku bathila pypdf use panrom
from docx import Document

# Set up the logger for this file
logger = logging.getLogger(__name__)

# NOTE: Render (Linux) deployment-kku Tesseract path thevaiyilla (Linux automatic-a path eduthukkum)
# Local Windows-kku mattum inga irukkatum, illana comment pannidalam.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from huggingface_hub import InferenceClient
from core.config import settings

# =========================================================
# ROBUST EXTRACTION FOR MULTI-PAGE DOCX AND PDF RESUMES
# =========================================================

def extract_text_from_bytes(
    file_bytes: bytes,
    filename: str
) -> str:
    filename_lower = filename.lower()
    text_list = []

    if filename_lower.endswith(".pdf"):
        logger.info(f"--- EXTRACTING TEXT FROM PDF USING pypdf: {filename} ---")
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_list.append(page_text)
        except Exception as e:
            logger.error(f"PDF Extraction Error processing {filename}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to parse PDF document: {filename}")

    elif filename_lower.endswith(".docx"):
        logger.info(f"--- EXTRACTING FULL DOCX CONTENT: {filename} ---")
        try:
            doc = Document(io.BytesIO(file_bytes))
            
            # 1. Extract from all paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_list.append(para.text)
            
            # 2. Extract from tables (since modern resume templates use tables/columns)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_list.append(cell.text)
                            
        except Exception as e:
            logger.error(f"DOCX Extraction Error processing {filename}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to parse DOCX document: {filename}")

    elif filename_lower.endswith((".png", ".jpg", ".jpeg")):
        logger.info(f"--- EXTRACTING TEXT FROM IMAGE: {filename} ---")
        try:
            image = Image.open(io.BytesIO(file_bytes))
            ocr_text = pytesseract.image_to_string(image)
            if ocr_text.strip():
                text_list.append(ocr_text)
        except Exception as e:
            logger.error(f"Image OCR Error processing {filename}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to parse Image document: {filename}")

    else:
        logger.warning(f"Unsupported file format attempted: {filename}")
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or Image.")

    final_text = "\n".join(text_list).strip()
    logger.info(f"--- FINAL EXTRACTED TEXT LENGTH FOR {filename}: {len(final_text)} ---")
    return final_text

# =========================================================
# EMBEDDING GENERATION
# =========================================================

def generate_embedding(
    text: str
) -> list[float]:
    if not text or not text.strip():
        logger.warning("Attempted to generate embedding for empty text")
        raise ValueError("Text cannot be empty for embedding generation")

    try:
        logger.debug("Calling HuggingFace Inference API for embeddings")
        client = InferenceClient(
            provider="hf-inference",
            api_key=settings.HF_TOKEN
        )

        result = client.feature_extraction(
            text[:12000],
            model=settings.HF_MODEL
        )

        embedding = result.tolist()

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
    except Exception as e:
        logger.error(f"HuggingFace API Integration Error: {str(e)}", exc_info=True)
        raise Exception("Failed to generate AI embeddings due to an external service error.")