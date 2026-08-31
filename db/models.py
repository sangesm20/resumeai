from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    BigInteger,
    LargeBinary,
    ForeignKey,
    DateTime,
    UniqueConstraint
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pgvector.sqlalchemy import Vector

from db.database import Base


# =========================================================
# HR
# =========================================================

class HR(Base):

    __tablename__ = "hr"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    candidates = relationship(
        "Candidate",
        back_populates="hr",
        cascade="all, delete-orphan"
    )


# =========================================================
# CANDIDATES
# =========================================================

class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hr_id = Column(
        Integer,
        ForeignKey(
            "hr.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    first_name = Column(
        String,
        nullable=False
    )

    last_name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    dob = Column(
        Date,
        nullable=False
    )

    experience_years = Column(
        Integer,
        default=0
    )

    graduation_year = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    hr = relationship(
        "HR",
        back_populates="candidates"
    )

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


# =========================================================
# RESUMES
# =========================================================

class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "candidates.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    file_type = Column(
        String(100),
        nullable=True
    )

    file_size = Column(
        BigInteger,
        nullable=True
    )

    file_content = Column(
        LargeBinary,
        nullable=False
    )

    is_active = Column(
        Integer,
        default=1
    )

    scan_status = Column(
        String(20),
        default="Pending"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    candidate = relationship(
        "Candidate",
        back_populates="resumes"
    )

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


# =========================================================
# SKILLS
# =========================================================

class Skill(Base):

    __tablename__ = "skills"

    skill_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    skill_name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    candidate_skills = relationship(
        "CandidateSkill",
        back_populates="skill"
    )


# =========================================================
# CANDIDATE SKILLS
# =========================================================

class CandidateSkill(Base):

    __tablename__ = "candidate_skills"

    resume_id = Column(
        Integer,
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    skill_id = Column(
        Integer,
        ForeignKey(
            "skills.skill_id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "candidates.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    experience_years = Column(
        Integer,
        default=0
    )

    candidate = relationship(
        "Candidate",
        back_populates="candidate_skills"
    )

    skill = relationship(
        "Skill",
        back_populates="candidate_skills"
    )

    resume = relationship(
        "Resume",
        back_populates="candidate_skills"
    )


# =========================================================
# RESUME EMBEDDINGS
# =========================================================

class ResumeEmbedding(Base):

    __tablename__ = "resume_embeddings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    resume_id = Column(
        Integer,
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    embedding = Column(
        Vector(384),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    resume = relationship(
        "Resume",
        back_populates="embedding"
    )