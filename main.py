from fastapi import FastAPI
from db.database import engine
from db.models import Base
from routes.user_routes import router as user_router
from routes.resume_routes import router as resume_router
from routes.scan_routes import router as scan_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(resume_router)
app.include_router(scan_router)