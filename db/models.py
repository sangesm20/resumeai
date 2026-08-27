from sqlalchemy import Column, Integer, String, Date, BigInteger, LargeBinary, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from db.database import Base


# -------------------------
# HR TABLE
# -------------------------
class HR(Base):
    __tablename__ = "hr"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # One HR can manage multiple candidates
    candidates = relationship(
        "Candidate",
        back_populates="hr",
        cascade="all, delete-orphan"
    )


# -------------------------
# CANDIDATES TABLE
# -------------------------
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    hr_id = Column(
        Integer,
        ForeignKey("hr.id", ondelete="CASCADE"),
        nullable=False
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    experience_years = Column(Integer, default=0)
    graduation_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    hr = relationship("HR", back_populates="candidates")
    resumes = relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )
    candidate_skills = relationship(
        "CandidateSkill",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )


# -------------------------
# RESUMES TABLE
# -------------------------
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )
    filename = Column(String, nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_content = Column(LargeBinary, nullable=True)  # BYTEA
    is_active = Column(Integer, default=0)
    scan_status = Column(String(20), default="Pending")
    created_at = Column(DateTime, server_default=func.now())

    candidate = relationship("Candidate", back_populates="resumes")
    candidate_skills = relationship(
        "CandidateSkill",
        back_populates="resume",
        cascade="all, delete-orphan"
    )
    embedding = relationship(
        "ResumeEmbedding",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan"
    )


# -------------------------
# SKILLS TABLE
# -------------------------
class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), unique=True, nullable=False)

    candidate_skills = relationship("CandidateSkill", back_populates="skill")


# -------------------------
# CANDIDATE_SKILLS TABLE
# -------------------------
class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True
    )
    skill_id = Column(
        Integer,
        ForeignKey("skills.skill_id", ondelete="CASCADE"),
        primary_key=True
    )
    experience_years = Column(Integer, default=0)
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )

    candidate = relationship("Candidate", back_populates="candidate_skills")
    skill = relationship("Skill", back_populates="candidate_skills")
    resume = relationship("Resume", back_populates="candidate_skills")


# -------------------------
# RESUME_EMBEDDINGS TABLE
# -------------------------
class ResumeEmbedding(Base):
    __tablename__ = "resume_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )
    embedding = Column(Vector(384), nullable=True)  # MiniLM dimension
    created_at = Column(DateTime, server_default=func.now())

    resume = relationship("Resume", back_populates="embedding")