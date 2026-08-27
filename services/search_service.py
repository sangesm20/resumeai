from db.models import Resume, Candidate, ResumeEmbedding
from services.ai_service import generate_embedding

def search_candidates_service(db, job_description: str, min_experience: int = 0, graduation_year: int = None):
    query_vector = generate_embedding(job_description)
    
    query = (
        db.query(
            Candidate,
            Resume,
            (1 - ResumeEmbedding.embedding.cosine_distance(query_vector)).label("similarity")
        )
        .join(Resume, Candidate.id == Resume.candidate_id)
        .join(ResumeEmbedding, Resume.id == ResumeEmbedding.resume_id)
        .filter(Candidate.experience_years >= min_experience, Resume.is_active == 1)
    )

    if graduation_year:
        query = query.filter(Candidate.graduation_year == graduation_year)

    results = query.order_by((1 - ResumeEmbedding.embedding.cosine_distance(query_vector)).desc()).all()

    ranked_candidates = []
    for cand, res, sim in results:
        match_percentage = max(0.0, min(100.0, round(float(sim) * 100, 2)))
        ranked_candidates.append({
            "candidate_id": cand.id,
            "name": f"{cand.first_name} {cand.last_name}",
            "email": cand.email,
            "experience_years": cand.experience_years,
            "graduation_year": cand.graduation_year,
            "match_percentage": match_percentage,
            "resume_id": res.id
        })

    return ranked_candidates