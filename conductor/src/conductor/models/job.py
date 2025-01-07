"""Job ORM class."""

from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String
from starrynight.modules.schema import Container

from conductor.constants import JobType
from conductor.models.base import BaseSQLModel
from conductor.models.run import Run


class Job(BaseSQLModel):
    """Job table."""

    __tablename__ = "job"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    spec: Mapped[dict] = mapped_column(Container, nullable=False)
    outputs: Mapped[dict] = mapped_column(JSON)
    inputs: Mapped[dict] = mapped_column(JSON)
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id"), nullable=False)
    step = relationship("Step", back_populates="jobs")
    runs: Mapped[list[Run]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
