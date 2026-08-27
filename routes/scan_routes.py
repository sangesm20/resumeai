from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import HR
from core.security import get_current_hr
from services.scan_service import scan_resume_service

router = APIRouter(prefix="/scan", tags=["Scan & AI"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{resume_id}")
def scan_resume(
    resume_id: int, 
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return scan_resume_service(db, resume_id)