from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from db.database import SessionLocal
from db.models import HR
from core.security import get_current_hr
from services.search_service import search_candidates_service

router = APIRouter(prefix="/search", tags=["Search Candidates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SearchQuery(BaseModel):
    job_description: str
    min_experience: Optional[int] = 0
    graduation_year: Optional[int] = None

@router.post("")
def search_candidates(
    payload: SearchQuery,
    current_hr: HR = Depends(get_current_hr),
    db: Session = Depends(get_db)
):
    return search_candidates_service(
        db=db, 
        job_description=payload.job_description, 
        min_experience=payload.min_experience,
        graduation_year=payload.graduation_year
    )