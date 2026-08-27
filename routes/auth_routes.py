from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from db.database import SessionLocal
from db.models import HR
from core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class HRRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.post("/register")
def register_hr(payload: HRRegisterSchema, db: Session = Depends(get_db)):
    if db.query(HR).filter(HR.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_hr = HR(
        name=payload.name,
        email=payload.email,
        password=get_password_hash(payload.password)
    )
    db.add(new_hr)
    db.commit()
    return {"message": "HR account created successfully"}

@router.post("/login")
def login_hr(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    hr = db.query(HR).filter(HR.email == form_data.username).first()
    if not hr or not verify_password(form_data.password, hr.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(data={"sub": hr.email})
    return {"access_token": token, "token_type": "bearer", "hr_id": hr.id}