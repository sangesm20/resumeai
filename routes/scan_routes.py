from fastapi import APIRouter, Depends

from db.models import HR

from core.security import (
    get_current_hr,
    get_db
)

from services.scan_service import (
    scan_resume_service
)


router = APIRouter(
    prefix="/scan",
    tags=["Scan & AI"]
)


@router.post("/{resume_id}")
def scan_resume(
    resume_id: int,
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return scan_resume_service(
        db=db,
        hr_id=current_hr.id,
        resume_id=resume_id
    )