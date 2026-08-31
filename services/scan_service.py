from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import (
    Resume,
    Candidate,
    Skill,
    CandidateSkill,
    ResumeEmbedding
)

from services.ai_service import (
    extract_text_from_bytes,
    generate_embedding
)


SUPPORTED_SKILLS = [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "SQL",
    "Docker",
    "Java",
    "JavaScript",
    "React",
    "Git",
    "Machine Learning",
    "Artificial Intelligence",
    "C++",
    "AWS",
    "HTML",
    "CSS",
    "Node.js",
    "Django",
    "MongoDB",
    "TypeScript",
    "C",
    "Spring Boot",
    "Kubernetes"
]


def contains_skill(
    text: str,
    skill: str
) -> bool:

    return skill.lower() in text.lower()


def scan_resume_service(
    db: Session,
    hr_id: int,
    resume_id: int
):

    # -----------------------------------------------------
    # 1. Get resume and verify HR ownership
    # -----------------------------------------------------

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

    if not resume.file_content:

        raise HTTPException(
            status_code=400,
            detail="Resume BYTEA content is empty"
        )

    try:

        resume.scan_status = "Processing"
        db.commit()

        # -------------------------------------------------
        # 2. Extract text from BYTEA
        # -------------------------------------------------

        text = extract_text_from_bytes(
            resume.file_content,
            resume.filename
        )

        if not text:

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume"
            )

        text_lower = text.lower()

        # -------------------------------------------------
        # 3. Remove old skill mappings for this resume
        # -------------------------------------------------

        (
            db.query(CandidateSkill)
            .filter(
                CandidateSkill.resume_id == resume.id
            )
            .delete(
                synchronize_session=False
            )
        )

        # -------------------------------------------------
        # 4. Detect skills
        # -------------------------------------------------

        found_skills = []

        for skill_name in SUPPORTED_SKILLS:

            if not contains_skill(
                text_lower,
                skill_name
            ):
                continue

            skill = (
                db.query(Skill)
                .filter(
                    Skill.skill_name.ilike(skill_name)
                )
                .first()
            )

            if not skill:

                skill = Skill(
                    skill_name=skill_name
                )

                db.add(skill)
                db.flush()

            candidate_skill = CandidateSkill(
                resume_id=resume.id,
                skill_id=skill.skill_id,
                candidate_id=resume.candidate_id,
                experience_years=(
                    resume.candidate.experience_years
                )
            )

            db.add(candidate_skill)

            found_skills.append(
                skill_name
            )

        # -------------------------------------------------
        # 5. Generate embedding
        # -------------------------------------------------

        embedding_vector = generate_embedding(
            text
        )

        # -------------------------------------------------
        # 6. Store / update embedding
        # -------------------------------------------------

        embedding_record = (
            db.query(ResumeEmbedding)
            .filter(
                ResumeEmbedding.resume_id == resume.id
            )
            .first()
        )

        if embedding_record:

            embedding_record.embedding = (
                embedding_vector
            )

        else:

            embedding_record = ResumeEmbedding(
                resume_id=resume.id,
                embedding=embedding_vector
            )

            db.add(embedding_record)

        # -------------------------------------------------
        # 7. Update status
        # -------------------------------------------------

        resume.scan_status = "Completed"

        db.commit()

        return {
            "message": "Resume scanned successfully",
            "resume_id": resume.id,
            "candidate_id": resume.candidate_id,
            "skills_found": found_skills,
            "skill_count": len(found_skills),
            "embedding_generated": True,
            "scan_status": resume.scan_status
        }

    except HTTPException:

        resume.scan_status = "Failed"
        db.commit()

        raise

    except Exception as exc:

        db.rollback()

        resume.scan_status = "Failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Resume scanning failed: {str(exc)}"
        )