"""Run ORM class."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from conductor.models.base import BaseSQLModel


class Run(BaseSQLModel):
    """Run table."""

    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), nullable=False)
    job = relationship("Job", back_populates="runs")
