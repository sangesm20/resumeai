from fastapi import Response, HTTPException, status
from db.models import Resume, Candidate


def upload_resume_service(db, candidate_id: int, file):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Read the raw binary directly into memory (stored solely in PostgreSQL BYTEA)
    raw_bytes = file.file.read()

    # Reset any previous active resume for this candidate
    db.query(Resume).filter(Resume.candidate_id == candidate_id).update({"is_active": 0})

    resume = Resume(
        candidate_id=candidate_id,
        filename=file.filename,
        file_type=file.content_type,
        file_size=len(raw_bytes),
        file_content=raw_bytes,  # BYTEA
        is_active=1,
        scan_status="Pending"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume stored in Supabase BYTEA successfully",
        "resume_id": resume.id,
        "filename": resume.filename,
        "file_size_bytes": resume.file_size
    }


def download_resume_service(db, resume_id: int):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume or not resume.file_content:
        raise HTTPException(status_code=404, detail="Resume file not found")

    return Response(
        content=resume.file_content,
        media_type=resume.file_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{resume.filename}"'}
    )


def get_resumes_service(db, candidate_id: int):
    return db.query(Resume).filter(Resume.candidate_id == candidate_id).all()


def delete_resume_service(db, resume_id: int):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}