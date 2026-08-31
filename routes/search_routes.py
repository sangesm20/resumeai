from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from db.models import HR

from core.security import (
    get_current_hr,
    get_db
)

from services.search_service import (
    search_candidates_service
)


router = APIRouter(
    prefix="/search",
    tags=["Candidate Search"]
)


class SearchQuery(BaseModel):

    job_description: str = Field(
        min_length=5
    )

    min_experience: int = Field(
        default=0,
        ge=0
    )

    graduation_year: Optional[int] = None

    top_k: int = Field(
        default=10,
        ge=1,
        le=50
    )


@router.post("")
def search_candidates(
    payload: SearchQuery,
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return search_candidates_service(
        db=db,
        hr_id=current_hr.id,
        job_description=payload.job_description,
        min_experience=payload.min_experience,
        graduation_year=payload.graduation_year,
        top_k=payload.top_k
    )