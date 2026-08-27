from fastapi import FastAPI
from db.database import engine, Base
import db.models

from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.resume_routes import router as resume_router
from routes.scan_routes import router as scan_router
from routes.search_routes import router as search_router

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Automated Resume Screening, Skill Extraction, and Semantic Candidate Ranking",
    version="1.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(scan_router)
app.include_router(search_router)