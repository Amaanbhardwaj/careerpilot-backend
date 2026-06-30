from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RoleSkill(Base):
    __tablename__ = "roles_skills_matrix"

    candidate: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    job_role: Mapped[str | None] = mapped_column(Text, index=True)
    category: Mapped[str | None] = mapped_column(Text)
    technical_skills: Mapped[str | None] = mapped_column(Text)
    soft_skills: Mapped[str | None] = mapped_column(Text)
    experience_level: Mapped[str | None] = mapped_column(Text)
    project_1: Mapped[str | None] = mapped_column(Text)
    project_2: Mapped[str | None] = mapped_column(Text)
    project_3: Mapped[str | None] = mapped_column(Text)
    project_4: Mapped[str | None] = mapped_column(Text)
