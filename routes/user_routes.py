from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, EmailStr

from db.database import SessionLocal
from db.models import Candidate, HR
from core.security import get_current_hr

router = APIRouter(prefix="/candidates", tags=["Candidates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    dob: date
    experience_years: int = 0
    graduation_year: int

@router.post("")
def create_candidate(
    payload: CandidateCreate,
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    if db.query(Candidate).filter(Candidate.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Candidate with this email already exists")

    candidate = Candidate(
        hr_id=current_hr.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        email=payload.email,
        dob=payload.dob,
        experience_years=payload.experience_years,
        graduation_year=payload.graduation_year
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return {"message": "Candidate created", "candidate_id": candidate.id}

@router.get("")
def get_hr_candidates(
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    # Returns candidates belonging to the logged-in HR
    return db.query(Candidate).filter(Candidate.hr_id == current_hr.id).all()