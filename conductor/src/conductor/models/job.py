"""Job ORM class."""

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from conductor.constants import JobType
from conductor.models.base import BaseSQLModel
from conductor.models.run import Run


class Job(BaseSQLModel):
    """Job table."""

    __tablename__ = "job"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    type = mapped_column(Enum(JobType), nullable=False)
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id"), nullable=False)
    step = relationship("Step", back_populates="jobs")
    runs: Mapped[list[Run]] = relationship(back_populates="job")
