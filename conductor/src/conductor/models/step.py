"""Project ORM class."""

from sqlalchemy import Column, Enum, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from conductor.constants import StepType
from conductor.models.base import BaseSQLModel
from conductor.models.job import Job

step_step_association_table = Table(
    "step_step_association_table",
    BaseSQLModel.metadata,
    Column("step_id", ForeignKey("step.id"), primary_key=True),
    Column("depend_on_id", ForeignKey("step.id"), primary_key=True),
)


class Step(BaseSQLModel):
    """Step table."""

    __tablename__ = "step"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    type = mapped_column(Enum(StepType, create_constraint=True), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    project = relationship("Project", back_populates="steps")
    jobs: Mapped[list[Job]] = relationship(
        back_populates="step", cascade="all, delete-orphan"
    )
    depends_on = relationship(
        "Step",
        secondary=step_step_association_table,
        back_populates="required_by",
        primaryjoin=step_step_association_table.c.step_id == id,
        secondaryjoin=step_step_association_table.c.depend_on_id == id,
    )
    required_by = relationship(
        "Step",
        secondary=step_step_association_table,
        back_populates="depends_on",
        primaryjoin=step_step_association_table.c.depend_on_id == id,
        secondaryjoin=step_step_association_table.c.step_id == id,
    )
