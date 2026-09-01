from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db.models import HR
from core.security import get_current_hr, get_db

from services.user_service import (
    create_candidate_service,
    get_hr_candidates_service,
    get_candidate_service,
    delete_candidate_service
)


router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    dob: date
    experience_years: int = 0
    graduation_year: int


@router.post("", summary="Create Candidate")
def create_candidate(
    payload: CandidateCreate,
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return create_candidate_service(
        db=db,
        hr_id=current_hr.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        email=payload.email,
        dob=payload.dob,
        experience_years=payload.experience_years,
        graduation_year=payload.graduation_year
    )


@router.get("", summary="Get Candidate List")
def get_candidate_list(
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return get_hr_candidates_service(
        db,
        current_hr.id
    )


@router.get("/{candidate_id}", summary="Get Candidate")
def get_candidate(
    candidate_id: int,
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return get_candidate_service(
        db,
        current_hr.id,
        candidate_id
    )


@router.delete("/{candidate_id}", summary="Delete Candidate")
def delete_candidate(
    candidate_id: int,
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return delete_candidate_service(
        db,
        current_hr.id,
        candidate_id
    )