from fastapi import APIRouter, Depends

from db.models import HR

from core.security import (
    get_current_hr,
    get_db
)

# Namma puthu service function-a import pandrom
from services.scan_service import (
    scan_active_resume_service
)


router = APIRouter(
    prefix="/scan",
    tags=["Scan & AI"]
)


# Route-a "/candidate/{candidate_id}" nu maathiyachu
@router.post("/candidate/{candidate_id}")
def scan_resume(
    candidate_id: int, # resume_id kku bathila candidate_id ulla vaangurom
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    # Puthu service function-kku candidate_id pass pandrom
    return scan_active_resume_service(
        db=db,
        hr_id=current_hr.id,
        candidate_id=candidate_id
    )