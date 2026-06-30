import json

import httpx

from app.core.config import settings


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _fallback_guidance(missing_skills: list[str], role: str) -> dict:
    top_missing = missing_skills[:6]
    return {
        "ats_improvement_suggestions": [
            "Add measurable impact statements with metrics for your strongest projects.",
            "Mirror important role keywords naturally in your skills and experience sections.",
            "Use clear section headings such as Experience, Projects, Skills, and Education.",
        ],
        "certifications": [
            f"{role} professional certificate",
            "SQL or database fundamentals certification",
            "Cloud or analytics platform certification",
        ],
        "resume_improvement_suggestions": [
            "Move the most role-relevant skills into the top third of the resume.",
            "Rewrite project bullets to show tools used, actions taken, and outcomes achieved.",
        ],
        "additional_skills": top_missing,
        "career_advice": (
            f"Focus on closing the highest-impact gaps for {role}: "
            f"{', '.join(top_missing) if top_missing else 'deeper project evidence and measurable outcomes'}."
        ),
    }


async def generate_ai_recommendations(
    *,
    role: str,
    current_skills: list[str],
    missing_skills: list[str],
    match_score: int,
    ats_score: int,
) -> dict:
    if not settings.openrouter_api_key:
        return _fallback_guidance(missing_skills, role)

    prompt = {
        "role": role,
        "current_skills": current_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "ats_score": ats_score,
        "task": (
            "Return strict JSON with keys: ats_improvement_suggestions, certifications, "
            "resume_improvement_suggestions, additional_skills, career_advice."
        ),
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a career coach. Respond only with valid compact JSON.",
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception:
        return _fallback_guidance(missing_skills, role)
