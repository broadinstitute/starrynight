"""Project ORM class."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from conductor.models.base import BaseSQLModel


class Step(BaseSQLModel):
    """Step table."""

    __tablename__ = "step"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
