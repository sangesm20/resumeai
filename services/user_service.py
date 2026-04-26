from db.models import User

def create_user_service(db, user_id, name, phone, email, dob):

    existing = db.query(User).filter(User.user_id == user_id).first()

    if existing:
        return {"error": "User already exists"}

    user = User(
        user_id=user_id,
        name=name,
        phone=phone,
        email=email,
        dob=dob
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}


def get_user_service(db, user_id):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"error": "User not found"}

    return user


def delete_user_service(db, user_id):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"error": "User not found"}

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}