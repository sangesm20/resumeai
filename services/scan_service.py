import re
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
    # Tech / Programming Skills
    "Python", "FastAPI", "PostgreSQL", "SQL", "Docker", "Java", "JavaScript", 
    "React", "Git", "Machine Learning", "Artificial Intelligence", "C++", "AWS", 
    "HTML", "CSS", "Node.js", "Django", "MongoDB", "TypeScript", "C", 
    "Spring Boot", "Kubernetes", "Agile Development", "Cloud Management", 
    "Data Synchronization", "UI/UX", "UI / UX", "Devops Debugger",
    
    # Graphic Design Skills (Exact names from resume)
    "Adobe InDesign",
    "InDesign",
    "Adobe Illustrator",
    "Illustrator",
    "Adobe Photoshop",
    "Photoshop",
    "Figma",
    "Blender",
    "Sketchbook",
    "Affinity Designer",
    "Canva"
]


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


def scan_resume_service(
    db: Session,
    hr_id: int,
    resume_id: int
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
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.file_content:
        raise HTTPException(status_code=400, detail="Resume BYTEA content is empty")

    try:
        resume.scan_status = "Processing"
        db.commit()

        # 1. Extract text from resume using ai_service (forces full OCR/multi-page processing)
        text = extract_text_from_bytes(
            resume.file_content,
            resume.filename
        )

        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")

        # Debugging: Print extracted text length and sample snippet to verify complete text reading
        print(f"--- SCAN SERVICE TEXT LENGTH: {len(text)} ---")
        print(text[:400])
        print("---------------------------------------")

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

        # 3. Fast & Accurate Skill Detection with Strict Boundaries & Contextual Filtering
        found_skills = []
        for skill_name in SUPPORTED_SKILLS:
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

        # 4. Generate and store full resume embedding for semantic search
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

        return {
            "message": "Resume scanned successfully with full OCR text extraction and design skills",
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