import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any

from db.models import Resume

# Lazy-loaded singleton model to prevent Render startup memory spikes & timeouts
_model = None


def get_embedding_model():
    """Lazily loads and returns the SentenceTransformer model singleton."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # Lightweight 384-dimensional embedding model
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generates a normalized 384-dimensional vector embedding for a given text."""
    if not text or not text.strip():
        return [0.0] * 384
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()


def search_resumes_semantic(
    db: Session,
    query_text: str,
    top_k: int = 10,
    threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """Performs cosine semantic similarity search over stored resumes using pgvector / numpy fallback."""
    query_vector = generate_embedding(query_text)

    # Attempt native pgvector cosine distance search via SQL
    try:
        # pgvector uses cosine_distance (<=> operator)
        # cosine_similarity = 1 - cosine_distance
        stmt = (
            select(
                Resume,
                (1 - Resume.embedding.cosine_distance(query_vector)).label("similarity")
            )
            .where(Resume.embedding.isnot(None))
            .order_by(Resume.embedding.cosine_distance(query_vector))
            .limit(top_k)
        )
        results = db.execute(stmt).all()

        matched_resumes = []
        for resume, score in results:
            sim_score = float(score) if score is not None else 0.0
            if sim_score >= threshold:
                matched_resumes.append({
                    "id": str(resume.id),
                    "filename": resume.filename,
                    "candidate_name": getattr(resume, "candidate_name", None),
                    "email": getattr(resume, "email", None),
                    "similarity_score": round(sim_score * 100, 2),
                    "uploaded_at": resume.uploaded_at.isoformat() if getattr(resume, "uploaded_at", None) else None
                })
        return matched_resumes

    except Exception:
        # Fallback: In-memory cosine similarity calculation using NumPy
        resumes = db.query(Resume).filter(Resume.embedding.isnot(None)).all()
        scored_resumes = []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)

        for res in resumes:
            if res.embedding is None:
                continue
            r_vec = np.array(res.embedding, dtype=np.float32)
            r_norm = np.linalg.norm(r_vec)

            if q_norm > 0 and r_norm > 0:
                sim = float(np.dot(q_vec, r_vec) / (q_norm * r_norm))
            else:
                sim = 0.0

            if sim >= threshold:
                scored_resumes.append({
                    "id": str(res.id),
                    "filename": res.filename,
                    "candidate_name": getattr(res, "candidate_name", None),
                    "email": getattr(res, "email", None),
                    "similarity_score": round(sim * 100, 2),
                    "uploaded_at": res.uploaded_at.isoformat() if getattr(res, "uploaded_at", None) else None,
                    "_raw_score": sim
                })

        scored_resumes.sort(key=lambda x: x["_raw_score"], reverse=True)
        for item in scored_resumes:
            item.pop("_raw_score", None)

        return scored_resumes[:top_k]