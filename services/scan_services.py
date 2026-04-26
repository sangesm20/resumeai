from db.models import Resume
from PyPDF2 import PdfReader
import os

def scan_resume_service(db, user_id):

    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == 1
    ).first()

    if not resume:
        return {"error": "No active resume"}

    path = os.path.join("uploads", resume.filename)

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    skills = ["python", "java", "sql"]

    found = [s for s in skills if s in text.lower()]
    percent = (len(found) / len(skills)) * 100

    return {"skills": found, "match": percent}