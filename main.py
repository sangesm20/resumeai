from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base
import db.models

from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.resume_routes import router as resume_router
from routes.scan_routes import router as scan_router
from routes.search_routes import router as search_router


app = FastAPI(
    title="AI Resume Analyzer API",
    description=(
        "AI-powered Resume Screening, "
        "Skill Extraction, Semantic Search "
        "and Candidate Ranking"
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    auth_router
)

app.include_router(
    user_router
)

app.include_router(
    resume_router
)

app.include_router(
    scan_router
)

app.include_router(
    search_router
)


@app.get("/")
def root():

    return {
        "message": "AI Resume Analyzer API is running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }