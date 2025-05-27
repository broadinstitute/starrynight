"""Run ORM class."""

from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String
from starrynight.modules.schema import SpecContainer

from conductor.constants import ExecutorType, RunStatus
from conductor.models.base import BaseSQLModel


class Run(BaseSQLModel):
    """Run table."""

    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    log_path: Mapped[str | None] = mapped_column()
    run_status = mapped_column(Enum(RunStatus, create_constraint=True), nullable=False)
    outputs: Mapped[dict] = mapped_column(JSON)
    inputs: Mapped[dict] = mapped_column(JSON)
    backend_run: Mapped[dict] = mapped_column(JSON)
    spec: Mapped[SpecContainer] = mapped_column(JSON, nullable=False)
    executor_type = mapped_column(
        Enum(ExecutorType, create_constraint=True), nullable=False
    )
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), nullable=False)
    job = relationship("Job", back_populates="runs")
