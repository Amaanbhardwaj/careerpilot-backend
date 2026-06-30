import re


def calculate_ats_score(resume_text: str, current_skills: list[str], required_skills: list[str]) -> int:
    text = resume_text.lower()
    score = 0

    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text, re.IGNORECASE):
        score += 10
    if re.search(r"\+?\d[\d\s().-]{8,}\d", resume_text):
        score += 10

    sections = ["experience", "education", "skills", "projects"]
    score += sum(10 for section in sections if section in text)

    action_verbs = ["built", "created", "developed", "improved", "analyzed", "managed", "designed"]
    score += min(15, sum(3 for verb in action_verbs if verb in text))

    if re.search(r"\d+%|\b\d+\s*(users|clients|projects|reports|dashboards|models)\b", text):
        score += 10

    required = {skill.lower() for skill in required_skills}
    current = {skill.lower() for skill in current_skills}
    if required:
        score += round((len(current.intersection(required)) / len(required)) * 15)

    return max(0, min(100, score))
