from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import HR
from core.security import get_current_hr
from services.resume_service import (
    upload_resume_service,
    download_resume_service,
    get_resumes_service,
    delete_resume_service
)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload Resume (Stored as BYTEA)
@router.post("/upload/{candidate_id}")
def upload_resume(
    candidate_id: int, 
    file: UploadFile = File(...), 
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return upload_resume_service(db, candidate_id, file)

# Download Original Resume (BYTEA -> File Stream)
@router.get("/download/{resume_id}")
def download_resume(
    resume_id: int, 
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return download_resume_service(db, resume_id)

# Get all resumes for a candidate
@router.get("/candidate/{candidate_id}")
def get_resumes(
    candidate_id: int, 
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return get_resumes_service(db, candidate_id)

# Delete a resume
@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int, 
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return delete_resume_service(db, resume_id)