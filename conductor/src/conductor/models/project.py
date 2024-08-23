"""Project ORM class."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum, String

from conductor.constants import ParserType, ProjectType
from conductor.models.base import BaseSQLModel
from conductor.models.step import Step


class Project(BaseSQLModel):
    """Project table."""

    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    dataset_uri: Mapped[str] = mapped_column()
    img_uri: Mapped[str | None] = mapped_column()
    description: Mapped[str] = mapped_column()
    type = mapped_column(Enum(ProjectType, create_constraint=True), nullable=False)
    parser_type = mapped_column(
        Enum(ParserType, create_constraint=True), nullable=False
    )
    steps: Mapped[list[Step]] = relationship(back_populates="project")
