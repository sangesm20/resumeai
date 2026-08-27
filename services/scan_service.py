from fastapi import HTTPException
from db.models import Resume, Skill, CandidateSkill, ResumeEmbedding
from services.ai_service import extract_text_from_bytes, generate_embedding

DEFAULT_SKILLS = [
    "Python", "FastAPI", "PostgreSQL", "SQL", "Docker",
    "Java", "JavaScript", "React", "Git", "Machine Learning",
    "C++", "AWS", "HTML", "CSS", "Node.js"
]

def scan_resume_service(db, resume_id: int):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume or not resume.file_content:
        raise HTTPException(status_code=404, detail="Resume not found or BYTEA content is empty")

    # 1. Read binary from DB without saving to disk
    text = extract_text_from_bytes(resume.file_content, resume.filename)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from BYTEA content")

    text_lower = text.lower()
    found_skills = []

    # 2. Skill detection & DB linking
    for skill_name in DEFAULT_SKILLS:
        if skill_name.lower() in text_lower:
            skill = db.query(Skill).filter(Skill.skill_name.ilike(skill_name)).first()
            if not skill:
                skill = Skill(skill_name=skill_name)
                db.add(skill)
                db.commit()
                db.refresh(skill)

            mapping = db.query(CandidateSkill).filter(
                CandidateSkill.candidate_id == resume.candidate_id,
                CandidateSkill.skill_id == skill.skill_id
            ).first()

            if not mapping:
                cand_skill = CandidateSkill(
                    candidate_id=resume.candidate_id,
                    skill_id=skill.skill_id,
                    resume_id=resume.id,
                    experience_years=resume.candidate.experience_years
                )
                db.add(cand_skill)

            found_skills.append(skill_name)

    # 3. Vector Embedding
    vector = generate_embedding(text)
    emb_record = db.query(ResumeEmbedding).filter(ResumeEmbedding.resume_id == resume.id).first()
    if emb_record:
        emb_record.embedding = vector
    else:
        new_emb = ResumeEmbedding(resume_id=resume.id, embedding=vector)
        db.add(new_emb)

    resume.scan_status = "Completed"
    db.commit()

    return {
        "message": "Resume parsed and embedded successfully from BYTEA",
        "skills_found": found_skills
    }