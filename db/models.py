from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    dob = Column(String)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    filename = Column(String)
    is_active = Column(Integer)  # 1 or 0