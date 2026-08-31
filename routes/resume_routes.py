from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from db.models import HR

from core.security import (
    get_current_hr,
    get_db
)

from services.resume_service import (
    upload_resume_service,
    download_resume_service,
    get_resumes_service,
    delete_resume_service
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


@router.post("/upload/{candidate_id}")
def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return upload_resume_service(
        db=db,
        hr_id=current_hr.id,
        candidate_id=candidate_id,
        file=file
    )


@router.get("/download/{resume_id}")
def download_resume(
    resume_id: int,
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return download_resume_service(
        db=db,
        hr_id=current_hr.id,
        resume_id=resume_id
    )


@router.get("/candidate/{candidate_id}")
def get_resumes(
    candidate_id: int,
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return get_resumes_service(
        db=db,
        hr_id=current_hr.id,
        candidate_id=candidate_id
    )


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_hr: HR = Depends(get_current_hr),
    db=Depends(get_db)
):

    return delete_resume_service(
        db=db,
        hr_id=current_hr.id,
        resume_id=resume_id
    )