from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.models import RoleSkill, User
from app.routes import analysis, auth, resume


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(
    title="CareerPilot AI Backend",
    version="1.0.0",
    description="Resume analysis backend powered by FastAPI, PostgreSQL, SQLAlchemy, and OpenRouter.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api", tags=["Resume"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_model=None)
def root():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "CareerPilot AI backend is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.on_event("startup")
def create_database_tables() -> None:
    Base.metadata.create_all(bind=engine)
