from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.scan_services import scan_resume_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/scan/{user_id}")
def scan(user_id: str, db: Session = Depends(get_db)):
    return scan_resume_service(db, user_id)