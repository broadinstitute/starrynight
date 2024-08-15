"""Project ORM class."""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from conductor.models.base import BaseSQLModel


class Project(BaseSQLModel):
    """Project table."""

    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
