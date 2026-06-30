import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.config import settings
from app.models.user import User
from app.schemas.analysis import UploadResponse
from app.services.auth_service import get_current_user
from app.services.resume_parser import extract_resume_text, validate_resume_file


router = APIRouter()


def _manifest_path() -> Path:
    return settings.upload_dir / "manifest.json"


def _load_manifest() -> dict:
    path = _manifest_path()
    if not path.exists():
        return {"latest_resume_id": None, "resumes": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict) -> None:
    _manifest_path().write_text(json.dumps(manifest, indent=2), encoding="utf-8")


@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    extension = validate_resume_file(file)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    resume_id = str(uuid4())
    original_filename = Path(file.filename or f"resume{extension}").name
    stored_filename = f"{resume_id}{extension}"
    stored_path = settings.upload_dir / stored_filename

    content = await file.read()
    stored_path.write_bytes(content)

    resume_text = extract_resume_text(stored_path)
    text_path = settings.upload_dir / f"{resume_id}.txt"
    text_path.write_text(resume_text, encoding="utf-8")
    (settings.upload_dir / "latest_resume.txt").write_text(resume_text, encoding="utf-8")

    manifest = _load_manifest()
    manifest["latest_resume_id"] = resume_id
    manifest.setdefault("resumes", {})[resume_id] = {
        "filename": original_filename,
        "stored_file": stored_filename,
        "text_file": text_path.name,
    }
    _save_manifest(manifest)

    return UploadResponse(
        filename=original_filename,
        resume_id=resume_id,
        extracted_text_length=len(resume_text),
        message="Resume uploaded and parsed successfully.",
    )
