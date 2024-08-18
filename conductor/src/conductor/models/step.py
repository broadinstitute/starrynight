"""Project ORM class."""

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from conductor.constants import StepType
from conductor.models.base import BaseSQLModel
from conductor.models.job import Job


class Step(BaseSQLModel):
    """Step table."""

    __tablename__ = "step"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    type = mapped_column(Enum(StepType), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    project = relationship("Project", back_populates="steps")
    jobs: Mapped[list[Job]] = relationship(back_populates="step")
