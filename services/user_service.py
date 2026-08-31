from fastapi import HTTPException

from db.models import Candidate


def create_candidate_service(
    db,
    hr_id,
    first_name,
    last_name,
    phone,
    email,
    dob,
    experience_years,
    graduation_year
):

    existing = (
        db.query(Candidate)
        .filter(
            Candidate.hr_id == hr_id,
            Candidate.email == email
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Candidate already exists for this HR"
        )

    candidate = Candidate(
        hr_id=hr_id,
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
        "message": "Candidate created successfully",
        "candidate_id": candidate.id
    }


def get_hr_candidates_service(
    db,
    hr_id
):

    return (
        db.query(Candidate)
        .filter(
            Candidate.hr_id == hr_id
        )
        .all()
    )


def get_candidate_service(
    db,
    hr_id,
    candidate_id
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.hr_id == hr_id
        )
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate


def delete_candidate_service(
    db,
    hr_id,
    candidate_id
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.hr_id == hr_id
        )
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)
    db.commit()

    return {
        "message": "Candidate deleted successfully"
    }