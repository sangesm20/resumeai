import logging
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from db.models import Candidate

# Logger setup
logger = logging.getLogger(__name__)


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
    try:
        existing = (
            db.query(Candidate)
            .filter(
                Candidate.hr_id == hr_id,
                Candidate.email == email
            )
            .first()
        )

        if existing:
            logger.warning(f"Attempted to create duplicate candidate with email {email} for HR {hr_id}")
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

        logger.info(f"Successfully created candidate {candidate.id} for HR {hr_id}")
        return {
            "message": "Candidate created successfully",
            "candidate_id": candidate.id
        }

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        db.rollback()
        logger.error(f"Database error while creating candidate {email}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while creating the candidate.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating candidate {email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def get_hr_candidates_service(
    db,
    hr_id
):
    try:
        candidates = (
            db.query(Candidate)
            .filter(
                Candidate.hr_id == hr_id
            )
            .all()
        )
        return candidates

    except SQLAlchemyError as db_err:
        logger.error(f"Database error fetching candidates for HR {hr_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while fetching candidates.")
    except Exception as e:
        logger.error(f"Unexpected error fetching candidates for HR {hr_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def get_candidate_service(
    db,
    hr_id,
    candidate_id
):
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not candidate:
            logger.warning(f"Candidate {candidate_id} not found for HR {hr_id}")
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        return candidate

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error fetching candidate {candidate_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while fetching the candidate.")
    except Exception as e:
        logger.error(f"Unexpected error fetching candidate {candidate_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")


def delete_candidate_service(
    db,
    hr_id,
    candidate_id
):
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.hr_id == hr_id
            )
            .first()
        )

        if not candidate:
            logger.warning(f"Attempted to delete non-existent candidate {candidate_id} for HR {hr_id}")
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        db.delete(candidate)
        db.commit()

        logger.info(f"Successfully deleted candidate {candidate_id} for HR {hr_id}")
        return {
            "message": "Candidate deleted successfully"
        }

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        db.rollback()
        logger.error(f"Database error deleting candidate {candidate_id}: {str(db_err)}")
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the candidate.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting candidate {candidate_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")