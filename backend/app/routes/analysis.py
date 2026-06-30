import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.role_skill import RoleSkill
from app.models.user import User
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.ats_engine import calculate_ats_score
from app.services.gap_analyzer import (
    calculate_match_score,
    find_missing_skills,
    recommended_projects,
    role_required_skills,
)
from app.services.openrouter_service import generate_ai_recommendations
from app.services.auth_service import get_current_user
from app.services.skill_extractor import extract_skills_from_text


router = APIRouter()


def _read_resume_text(resume_id: str | None = None) -> str:
    if resume_id:
        manifest_path = settings.upload_dir / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No uploaded resumes were found.",
            )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        resume = manifest.get("resumes", {}).get(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume id was not found.",
            )
        text_path = settings.upload_dir / resume["text_file"]
    else:
        text_path = settings.upload_dir / "latest_resume.txt"

    if not text_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload a resume before running analysis.",
        )
    return text_path.read_text(encoding="utf-8")


def _fetch_role_data(db: Session, role: str) -> RoleSkill:
    normalized_role = role.strip().lower()
    statement = (
        select(RoleSkill)
        .where(func.lower(RoleSkill.job_role) == normalized_role)
        .limit(1)
    )
    role_data = db.execute(statement).scalars().first()

    if role_data:
        return role_data

    fuzzy_statement = (
        select(RoleSkill)
        .where(RoleSkill.job_role.ilike(f"%{role.strip()}%"))
        .limit(1)
    )
    role_data = db.execute(fuzzy_statement).scalars().first()
    if not role_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No role data found for '{role}'.",
        )
    return role_data


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    resume_text = _read_resume_text(payload.resume_id)
    role_data = _fetch_role_data(db, payload.role)

    current_skills = extract_skills_from_text(resume_text)
    required_skills = role_required_skills(role_data)
    missing_skills = find_missing_skills(current_skills, required_skills)
    match_score = calculate_match_score(current_skills, required_skills)
    ats_score = calculate_ats_score(resume_text, current_skills, required_skills)
    projects = recommended_projects(role_data)

    ai = await generate_ai_recommendations(
        role=payload.role,
        current_skills=current_skills,
        missing_skills=missing_skills,
        match_score=match_score,
        ats_score=ats_score,
    )

    return AnalysisResponse(
        current_skills=current_skills,
        missing_skills=missing_skills,
        recommended_projects=projects,
        match_score=match_score,
        ats_score=ats_score,
        certifications=ai.get("certifications", []),
        career_advice=ai.get("career_advice", ""),
        ats_improvement_suggestions=ai.get("ats_improvement_suggestions", []),
        resume_improvement_suggestions=ai.get("resume_improvement_suggestions", []),
        additional_skills=ai.get("additional_skills", []),
    )


@router.get("/roles", response_model=list[str])
def list_job_roles(db: Session = Depends(get_db)) -> list[str]:
    statement = (
        select(RoleSkill.job_role)
        .where(RoleSkill.job_role.is_not(None))
        .distinct()
        .order_by(RoleSkill.job_role)
    )
    return [role for role in db.execute(statement).scalars().all() if role]
