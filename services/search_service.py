import re
import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.models import (
    Candidate,
    Resume,
    ResumeEmbedding,
    Skill,
    CandidateSkill
)

from services.ai_service import (
    generate_embedding
)

from core.config import settings

# Logger setup
logger = logging.getLogger(__name__)


def extract_required_skills(
    job_description: str,
    db: Session
) -> list[str]:

    text = job_description.lower()
    text = re.sub(r'\bjs\b', 'javascript', text)
    found = []

    # Get skills directly from the database instead of hardcoded list
    all_skills = db.query(Skill.skill_name).all()
    db_skill_names = [row[0] for row in all_skills]

    for skill in db_skill_names:
        skill_lower = skill.lower()
        
        # BUG FIX: Special condition to prevent 'C' from falsely matching inside 'C++' or 'C#'
        if skill_lower == "c":
            pattern = r'(?<![a-z0-9])c(?![a-z0-9+#])'
        else:
            # Exact word match panra Regex pattern
            pattern = r'(?<![a-z0-9])' + re.escape(skill_lower) + r'(?![a-z0-9])'
        
        if re.search(pattern, text):
            found.append(skill)

    return found


def calculate_skill_score(
    candidate_skill_names: list[str],
    required_skills: list[str]
) -> float:

    if not required_skills:
        return 0.0

    candidate_skills = {
        skill.lower()
        for skill in candidate_skill_names
    }

    required = {
        skill.lower()
        for skill in required_skills
    }

    matched = candidate_skills.intersection(
        required
    )

    return (
        len(matched)
        / len(required)
    ) * 100


def calculate_experience_score(
    candidate_experience: int,
    minimum_experience: int
) -> float:

    if minimum_experience <= 0:
        return 100.0

    if candidate_experience >= minimum_experience:
        return 100.0

    return (
        candidate_experience
        / minimum_experience
    ) * 100


def search_candidates_service(
    db: Session,
    hr_id: int,
    job_description: str,
    min_experience: int = 0,
    graduation_year: Optional[int] = None,
    top_k: Optional[int] = None
):

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    try:
        # -----------------------------------------------------
        # 1. Generate job embedding
        # -----------------------------------------------------
        logger.info(f"Starting semantic search for HR {hr_id}")
        
        query_vector = generate_embedding(
            job_description
        )

        required_skills = extract_required_skills(
            job_description,
            db
        )
        
        if not required_skills:
            logger.warning("No valid skills detected in the job description")
            raise HTTPException(
                status_code=400,
                detail="No valid skills detected! Please check for typos or use standard skill names."
            )
            
        top_k = (
            top_k
            or settings.DEFAULT_TOP_K
        )

        # -----------------------------------------------------
        # 2. Get resumes belonging to this HR
        # -----------------------------------------------------
        
        stmt = (
            select(
                Resume,
                Candidate,
                ResumeEmbedding
            )
            .join(
                Candidate,
                Resume.candidate_id == Candidate.id
            )
            .join(
                ResumeEmbedding,
                ResumeEmbedding.resume_id == Resume.id
            )
            .where(
                Candidate.hr_id == hr_id,
                Resume.is_active == 1,
                ResumeEmbedding.embedding.isnot(None)
            )
        )

        if min_experience is not None:
            stmt = stmt.where(
                Candidate.experience_years
                >= min_experience
            )

        if graduation_year is not None:
            stmt = stmt.where(
                Candidate.graduation_year
                >= graduation_year
            )

        results = db.execute(stmt).all()

        candidates = []

        # -----------------------------------------------------
        # 3. Calculate similarity
        # -----------------------------------------------------

        for resume, candidate, embedding_record in results:

            # SQLAlchemy expression cannot be directly
            # evaluated here, so calculate using Python.
            resume_vector = list(
                embedding_record.embedding
            )

            dot_product = sum(
                a * b
                for a, b in zip(
                    query_vector,
                    resume_vector
                )
            )

            query_norm = sum(
                value * value
                for value in query_vector
            ) ** 0.5

            resume_norm = sum(
                value * value
                for value in resume_vector
            ) ** 0.5

            if query_norm == 0 or resume_norm == 0:
                semantic_similarity = 0.0
            else:
                semantic_similarity = (
                    dot_product
                    / (query_norm * resume_norm)
                )

            semantic_similarity = max(
                0.0,
                min(
                    1.0,
                    semantic_similarity
                )
            )

            semantic_score = (
                semantic_similarity * 100
            )

            # -------------------------------------------------
            # 4. Candidate skills
            # -------------------------------------------------

            skill_rows = (
                db.query(Skill.skill_name)
                .join(
                    CandidateSkill,
                    CandidateSkill.skill_id
                    == Skill.skill_id
                )
                .filter(
                    CandidateSkill.resume_id
                    == resume.id
                )
                .all()
            )

            candidate_skill_names = [
                row[0]
                for row in skill_rows
            ]

            # -------------------------------------------------
            # 5. Skill score
            # -------------------------------------------------

            skill_score = calculate_skill_score(
                candidate_skill_names,
                required_skills
            )
            if required_skills and skill_score == 0:
                continue

            # -------------------------------------------------
            # 6. Experience score
            # -------------------------------------------------

            experience_score = calculate_experience_score(
                candidate.experience_years,
                min_experience
            )

            # -------------------------------------------------
            # 7. Final match percentage
            #
            # Semantic similarity = 60%
            # Skill match         = 25%
            # Experience          = 15%
            # -------------------------------------------------

            final_score = (
                semantic_score * settings.SEMANTIC_WEIGHT
            + skill_score * settings.SKILL_WEIGHT
            + experience_score * settings.EXPERIENCE_WEIGHT
            )

            if final_score < (
                settings.DEFAULT_SIMILARITY_THRESHOLD * 100
            ):
                continue

            candidates.append({
                "candidate_id": candidate.id,
                "resume_id": resume.id,
                "candidate_name": (
                    f"{candidate.first_name} "
                    f"{candidate.last_name}"
                ),
                "email": candidate.email,
                "experience_years": (
                    candidate.experience_years
                ),
                "graduation_year": (
                    candidate.graduation_year
                ),
                "skills": candidate_skill_names,
                "required_skills": required_skills,
                "semantic_score": round(
                    semantic_score,
                    2
                ),
                "skill_score": round(
                    skill_score,
                    2
                ),
                "experience_score": round(
                    experience_score,
                    2
                ),
                "match_percentage": round(
                    final_score,
                    2
                ),
                "resume_filename": resume.filename,
                "uploaded_at": (
                    resume.created_at.isoformat()
                    if resume.created_at
                    else None
                )
            })

        # -----------------------------------------------------
        # 8. Rank candidates
        # -----------------------------------------------------

        candidates.sort(
            key=lambda item: item["match_percentage"],
            reverse=True
        )

        logger.info(f"Search completed. Returning {len(candidates[:top_k])} matching candidates.")
        
        return {
            "job_description": job_description,
            "required_skills": required_skills,
            "filters": {
                "minimum_experience": min_experience,
                "graduation_year": graduation_year
            },
            "total_matches": len(candidates),
            "results": candidates[:top_k]
        }

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during semantic search: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while searching for candidates.")
    except Exception as e:
        logger.error(f"Unexpected error during semantic search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")