import numpy as np
import requests
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any

from db.models import Resume
from core.config import settings


def generate_embedding(text: str) -> List[float]:
    """Generates an embedding dynamically via the configured API URL without hardcoded values."""
    if not text or not text.strip():
        return [0.0] * 384

    try:
        response = requests.post(
            settings.HF_API_URL,
            headers={"Content-Type": "application/json"},
            json={"inputs": text[:500], "options": {"wait_for_model": True}},
            timeout=10,
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    return result[0]
                return result
    except Exception:
        pass

    return [0.0] * 384


def search_resumes_semantic(
    db: Session,
    query_text: str,
    top_k: int = None,
    threshold: float = None
) -> List[Dict[str, Any]]:
    """Performs semantic similarity search using settings-defined thresholds and limits."""
    top_k = top_k or settings.DEFAULT_TOP_K
    threshold = threshold if threshold is not None else settings.DEFAULT_SIMILARITY_THRESHOLD

    query_vector = generate_embedding(query_text)

    # 1. pgvector native cosine search
    try:
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

        matched = []
        for resume, score in results:
            sim_score = float(score) if score is not None else 0.0
            if sim_score >= threshold:
                matched.append({
                    "id": str(resume.id),
                    "filename": resume.filename,
                    "candidate_name": getattr(resume, "candidate_name", None),
                    "email": getattr(resume, "email", None),
                    "similarity_score": round(sim_score * 100, 2),
                    "uploaded_at": resume.uploaded_at.isoformat() if getattr(resume, "uploaded_at", None) else None
                })
        return matched

    except Exception:
        # 2. In-memory fallback via NumPy
        resumes = db.query(Resume).filter(Resume.embedding.isnot(None)).all()
        scored = []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)

        for res in resumes:
            if res.embedding is None:
                continue
            r_vec = np.array(res.embedding, dtype=np.float32)
            r_norm = np.linalg.norm(r_vec)

            sim = float(np.dot(q_vec, r_vec) / (q_norm * r_norm)) if (q_norm > 0 and r_norm > 0) else 0.0

            if sim >= threshold:
                scored.append({
                    "id": str(res.id),
                    "filename": res.filename,
                    "candidate_name": getattr(res, "candidate_name", None),
                    "email": getattr(res, "email", None),
                    "similarity_score": round(sim * 100, 2),
                    "uploaded_at": res.uploaded_at.isoformat() if getattr(res, "uploaded_at", None) else None,
                    "_raw_score": sim
                })

        scored.sort(key=lambda x: x["_raw_score"], reverse=True)
        for item in scored:
            item.pop("_raw_score", None)

        return scored[:top_k]