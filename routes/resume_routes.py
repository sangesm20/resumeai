from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.resume_service import (
    upload_resume_service,
    set_active_service,
    get_resumes_service,
    delete_resume_service
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload/{user_id}")
def upload(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return upload_resume_service(db, user_id, file)


@router.put("/set-active/{user_id}/{filename}")
def set_active(user_id: str, filename: str, db: Session = Depends(get_db)):
    return set_active_service(db, user_id, filename)


@router.get("/resumes/{user_id}")
def get_resumes(user_id: str, db: Session = Depends(get_db)):
    return get_resumes_service(db, user_id)


@router.delete("/delete/{user_id}/{filename}")
def delete_resume(user_id: str, filename: str, db: Session = Depends(get_db)):
    return delete_resume_service(db, user_id, filename)