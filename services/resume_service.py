from fastapi import HTTPException, Response

from db.models import Resume, Candidate


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}


def upload_resume_service(
    db,
    hr_id,
    candidate_id,
    file
):

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

    filename = file.filename or ""

    extension = ""

    if "." in filename:

        extension = (
            "." + filename.rsplit(".", 1)[1].lower()
        )

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
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

    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "candidate_id": candidate_id,
        "filename": resume.filename,
        "file_size_bytes": resume.file_size,
        "scan_status": resume.scan_status
    }


def download_resume_service(
    db,
    hr_id,
    resume_id
):

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
            "Content-Disposition":
                f'attachment; filename="{resume.filename}"'
        }
    )


def get_resumes_service(
    db,
    hr_id,
    candidate_id
):

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

    return (
        db.query(Resume)
        .filter(
            Resume.candidate_id == candidate_id
        )
        .order_by(
            Resume.created_at.desc()
        )
        .all()
    )


def delete_resume_service(
    db,
    hr_id,
    resume_id
):

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

    return {
        "message": "Resume deleted successfully"
    }