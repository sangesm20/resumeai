import logging
from fastapi import HTTPException, Response
from sqlalchemy.exc import SQLAlchemyError
from db.models import Resume, Candidate

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg"
}


def upload_resume_service(
    db,
    hr_id,
    candidate_id,
    file
):
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        # ==========================================
        # ENFORCE 5-RESUME LIMIT
        # ==========================================
        resume_count = (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .count()
        )
        
        if resume_count >= 5:
            raise HTTPException(
                status_code=400,
                detail="Resume limit exceeded. A candidate can only have a maximum of 5 resumes."
            )
        # ==========================================

        filename = file.filename or ""
        extension = ""

        if "." in filename:
            extension = "." + filename.rsplit(".", 1)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX, and Image files are supported"
            )

        raw_bytes = file.file.read()

        if not raw_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Deactivate previous resumes
        (
            db.query(Resume)
            .filter(
                Resume.candidate_id == candidate_id
            )
            .update({
                "is_active": 0
            })
        )

        resume = Resume(
            candidate_id=candidate_id,
            filename=filename,
            file_type=file.content_type,
            file_size=len(raw_bytes),
            file_content=raw_bytes,
            is_active=1,
            scan_status="Pending"
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        logger.info(f"Successfully uploaded resume {resume.id} for candidate {candidate_id}")
        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume.id,
            "candidate_id": candidate_id,
            "filename": resume.filename,
            "file_size_bytes": resume.file_size,
            "scan_status": resume.scan_status
        }

    except HTTPException:
        # Re-raise intended HTTP errors (like 400 or 404) so they reach the frontend
        raise
    except SQLAlchemyError as db_err:
        db.rollback()  # Crucial: rollback the transaction if DB fails
        logger.error(f"Database error during resume upload for candidate {candidate_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while uploading the resume.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during resume upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def download_resume_service(
    db,
    hr_id,
    resume_id
):
    try:
        resume = (
            db.query(Resume)
            .join(Candidate)
            .filter(
                Resume.id == resume_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not resume or not resume.file_content:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        return Response(
            content=resume.file_content,
            media_type=(
                resume.file_type
                or "application/octet-stream"
            ),
            headers={
                "Content-Disposition": f'attachment; filename="{resume.filename}"'
            }
        )

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during resume download for resume {resume_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while retrieving the resume.")
    except Exception as e:
        logger.error(f"Unexpected error during resume download: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def get_resumes_service(
    db,
    hr_id,
    candidate_id
):
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        resumes = (
            db.query(Resume)
            .filter(
                Resume.candidate_id == candidate_id
            )
            .order_by(
                Resume.created_at.desc()
            )
            .all()
        )

        return [
            {
                "id": r.id,
                "candidate_id": r.candidate_id,
                "filename": r.filename,
                "file_type": r.file_type,
                "file_size": r.file_size,
                "is_active": r.is_active,
                "scan_status": r.scan_status,
                "created_at": str(r.created_at) if r.created_at else None
            }
            for r in resumes
        ]

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error fetching resumes for candidate {candidate_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while fetching resumes.")
    except Exception as e:
        logger.error(f"Unexpected error fetching resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def delete_resume_service(
    db,
    hr_id,
    resume_id
):
    try:
        resume = (
            db.query(Resume)
            .join(Candidate)
            .filter(
                Resume.id == resume_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        db.delete(resume)
        db.commit()

        logger.info(f"Successfully deleted resume {resume_id}")
        return {
            "message": "Resume deleted successfully"
        }

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        db.rollback()  # Crucial for delete operations
        logger.error(f"Database error deleting resume {resume_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the resume.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting resume {resume_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")