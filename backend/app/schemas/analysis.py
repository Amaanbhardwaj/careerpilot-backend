from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str
    resume_id: str
    extracted_text_length: int
    message: str


class AnalysisRequest(BaseModel):
    role: str = Field(..., min_length=1, examples=["Data Analyst"])
    resume_id: str | None = Field(
        default=None,
        description="Optional uploaded resume id. If omitted, the latest uploaded resume is used.",
    )


class AnalysisResponse(BaseModel):
    current_skills: list[str]
    missing_skills: list[str]
    recommended_projects: list[str]
    match_score: int
    ats_score: int
    certifications: list[str]
    career_advice: str
    ats_improvement_suggestions: list[str] = []
    resume_improvement_suggestions: list[str] = []
    additional_skills: list[str] = []
