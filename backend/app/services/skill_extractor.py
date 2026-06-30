import re


SKILL_KEYWORDS = {
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "statistics",
    "machine learning",
    "data analysis",
    "data visualization",
    "pandas",
    "numpy",
    "scikit-learn",
    "r",
    "java",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "postgresql",
    "mysql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "communication",
    "leadership",
    "problem solving",
    "teamwork",
    "stakeholder management",
    "project management",
    "critical thinking",
}


SEPARATORS = re.compile(r"[,;/|•\n\r\t]+")


def normalize_skill(skill: str) -> str:
    skill = re.sub(r"\s+", " ", skill.strip().lower())
    aliases = {
        "powerbi": "power bi",
        "nodejs": "node.js",
        "postgres": "postgresql",
        "ms excel": "excel",
    }
    return aliases.get(skill, skill)


def split_skills(value: str | None) -> list[str]:
    if not value:
        return []
    skills = {normalize_skill(part) for part in SEPARATORS.split(value) if normalize_skill(part)}
    return sorted(skills)


def extract_skills_from_text(text: str) -> list[str]:
    normalized_text = normalize_skill(text)
    found: set[str] = set()

    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9+#.-])" + re.escape(skill) + r"(?![a-z0-9+#.-])"
        if re.search(pattern, normalized_text):
            found.add(skill)

    explicit_sections = re.findall(
        r"(?:skills|technical skills|core competencies)\s*[:\-]\s*(.{1,500})",
        text,
        flags=re.IGNORECASE,
    )
    for section in explicit_sections:
        for skill in split_skills(section):
            if len(skill) <= 40:
                found.add(skill)

    return sorted(found)
