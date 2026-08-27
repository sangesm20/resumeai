from db.models import Candidate


def create_candidate_service(
    db,
    first_name,
    last_name,
    phone,
    email,
    dob,
    experience_years,
    graduation_year
):

    existing = db.query(Candidate).filter(
        Candidate.email == email
    ).first()

    if existing:
        return {"error": "Candidate already exists"}

    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        dob=dob,
        experience_years=experience_years,
        graduation_year=graduation_year
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "message": "Candidate created",
        "candidate_id": candidate.id
    }


def get_all_candidates_service(db):

    candidates = db.query(Candidate).all()

    return candidates


def get_candidate_service(db, candidate_id):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    return candidate


def delete_candidate_service(db, candidate_id):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted"}