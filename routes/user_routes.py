from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.user_service import (
    create_user_service,
    get_user_service,
    delete_user_service
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users")
def create_user(user_id: str, name: str, phone: str, email: str, dob: str, db: Session = Depends(get_db)):
    return create_user_service(db, user_id, name, phone, email, dob)


@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    return get_user_service(db, user_id)


@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    return delete_user_service(db, user_id)