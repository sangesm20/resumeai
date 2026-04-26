from db.models import Resume
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def upload_resume_service(db, user_id, file):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    resume = Resume(
        user_id=user_id,
        filename=file.filename,
        is_active=0
    )

    db.add(resume)
    db.commit()

    return {"message": "Resume uploaded"}


def set_active_service(db, user_id, filename):

    db.query(Resume).filter(Resume.user_id == user_id).update({"is_active": 0})

    db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.filename == filename
    ).update({"is_active": 1})

    db.commit()

    return {"message": "Active resume set"}


def get_resumes_service(db, user_id):
    resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
    return resumes


def delete_resume_service(db, user_id, filename):

    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.filename == filename
    ).first()

    if not resume:
        return {"error": "Resume not found"}

    # delete file also
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(resume)
    db.commit()

    return {"message": "Resume deleted"}