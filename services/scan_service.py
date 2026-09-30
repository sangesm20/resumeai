import re
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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

# Logger setup
logger = logging.getLogger(__name__)


def contains_skill(text: str, skill: str) -> bool:
    text_lower = text.lower()
    skill_lower = skill.lower()

    # Special handling for C++ so it doesn't strip '+' into a single 'c'
    if skill_lower == "c++":
        pattern = r'\bc\+\+\b'
        return bool(re.search(pattern, text_lower))

    # Multi-word skills-ku normalized check use pannum
    if any(c in skill for c in [' ', '/', '.', '-']):
        clean_text = re.sub(r'[\s/,\-_.]+', '', text_lower)
        clean_skill = re.sub(r'[\s/,\-_.]+', '', skill_lower)
        return clean_skill in clean_text

    # Single-word skills-ku strict word boundary
    pattern = r'\b' + re.escape(skill_lower) + r'\b'
    matches = list(re.finditer(pattern, text_lower))

    if not matches:
        return False

    for match in matches:
        end_pos = match.end()
        context_after = text_lower[end_pos:end_pos + 40]

        # Negative pattern check for AWS location
        if skill_lower == "aws":
            location_pattern = r'^\s*,\s*[a-z\s]+,\s*[a-z]{2}\b'
            if re.match(location_pattern, context_after):
                continue

        return True

    return False


# ==========================================
# SCAN ACTIVE RESUME SERVICE
# ==========================================
def scan_active_resume_service(
    db: Session,
    hr_id: int,
    candidate_id: int
):
    try:
        # Active resume (is_active == 1) mattum thedi edukkura query - Ippo safe zone-la irukku!
        resume = (
            db.query(Resume)
            .join(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.hr_id == hr_id,
                Resume.is_active == 1
            )
            .first()
        )

        if not resume:
            logger.warning(f"No active resume found for candidate {candidate_id}")
            raise HTTPException(
                status_code=404, 
                detail="No active resume found for this candidate"
            )

        if not resume.file_content:
            logger.error(f"Resume BYTEA content is empty for resume {resume.id}")
            raise HTTPException(status_code=400, detail="Resume BYTEA content is empty")

        resume.scan_status = "Processing"
        db.commit()

        # 1. Extract text from resume using ai_service
        logger.info(f"Starting AI text extraction for resume {resume.id}")
        text = extract_text_from_bytes(
            resume.file_content,
            resume.filename
        )

        if not text:
            logger.error(f"Text extraction failed for resume {resume.id}")
            raise HTTPException(status_code=400, detail="Could not extract text from resume")

        logger.info(f"--- SCAN SERVICE TEXT LENGTH: {len(text)} ---")
        logger.debug(f"Extracted text preview: {text[:400]}")

        text_lower = text.lower()

        # 2. Remove old skill mappings
        (
            db.query(CandidateSkill)
            .filter(
                CandidateSkill.resume_id == resume.id
            )
            .delete(
                synchronize_session=False
            )
        )

        # 3. Fast & Accurate Skill Detection (Database Driven)
        all_db_skills = db.query(Skill).all()
        supported_skills_from_db = [skill.skill_name for skill in all_db_skills]

        found_skills = []
        for skill_name in supported_skills_from_db:
            if contains_skill(text_lower, skill_name):
                normalized_name = skill_name.replace("UI / UX", "UI/UX")
                if normalized_name in found_skills:
                    continue

                skill = (
                    db.query(Skill)
                    .filter(
                        Skill.skill_name.ilike(normalized_name)
                    )
                    .first()
                )

                if not skill:
                    skill = Skill(skill_name=normalized_name)
                    db.add(skill)
                    db.flush()

                candidate_skill = CandidateSkill(
                    resume_id=resume.id,
                    skill_id=skill.skill_id,
                    candidate_id=resume.candidate_id,
                    experience_years=resume.candidate.experience_years
                )
                db.add(candidate_skill)
                found_skills.append(normalized_name)

        # 4. Generate and store full resume embedding
        logger.info(f"Generating embeddings for resume {resume.id}")
        embedding_vector = generate_embedding(text)

        embedding_record = (
            db.query(ResumeEmbedding)
            .filter(
                ResumeEmbedding.resume_id == resume.id
            )
            .first()
        )

        if embedding_record:
            embedding_record.embedding = embedding_vector
        else:
            embedding_record = ResumeEmbedding(
                resume_id=resume.id,
                embedding=embedding_vector
            )
            db.add(embedding_record)

        resume.scan_status = "Completed"
        db.commit()
        
        logger.info(f"Successfully scanned resume {resume.id} for candidate {candidate_id}")

        return {
            "message": "Active resume scanned successfully with full OCR text extraction",
            "resume_id": resume.id,
            "candidate_id": resume.candidate_id,
            "skills": found_skills,
            "experience_years": resume.candidate.experience_years,
            "graduation_year": resume.candidate.graduation_year,
            "skill_count": len(found_skills),
            "embedding_generated": True,
            "scan_status": resume.scan_status
        }

    except HTTPException as http_exc:
        # FastAPI errors-a apdiye anuppidalam, aana fail aana status update pannanum
        if 'resume' in locals() and resume and http_exc.status_code != 404:
            resume.scan_status = "Failed"
            db.commit()
        raise

    except SQLAlchemyError as db_err:
        db.rollback()
        logger.error(f"Database error during scan for candidate {candidate_id}: {str(db_err)}")
        if 'resume' in locals() and resume:
            try:
                resume.scan_status = "Failed"
                db.commit()
            except:
                pass
        raise HTTPException(status_code=500, detail="Database error occurred during resume scanning.")

    except Exception as exc:
        db.rollback()
        logger.error(f"Unexpected error during resume scan for candidate {candidate_id}: {str(exc)}", exc_info=True)
        if 'resume' in locals() and resume:
            try:
                resume.scan_status = "Failed"
                db.commit()
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Resume scanning failed due to an internal error."
        )