from app.models.role_skill import RoleSkill
from app.services.skill_extractor import split_skills


def role_required_skills(role_data: RoleSkill) -> list[str]:
    skills = set(split_skills(role_data.technical_skills))
    skills.update(split_skills(role_data.soft_skills))
    return sorted(skills)


def calculate_match_score(current_skills: list[str], required_skills: list[str]) -> int:
    if not required_skills:
        return 0
    current = {skill.lower() for skill in current_skills}
    required = {skill.lower() for skill in required_skills}
    matched_count = len(current.intersection(required))
    return round((matched_count / len(required)) * 100)


def find_missing_skills(current_skills: list[str], required_skills: list[str]) -> list[str]:
    current = {skill.lower() for skill in current_skills}
    return sorted(skill for skill in required_skills if skill.lower() not in current)


def recommended_projects(role_data: RoleSkill) -> list[str]:
    projects = [
        role_data.project_1,
        role_data.project_2,
        role_data.project_3,
        role_data.project_4,
    ]
    return [project.strip() for project in projects if project and project.strip()]
