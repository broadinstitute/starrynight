"""Project ORM class."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum, String

from conductor.constants import ParserType
from conductor.models.base import BaseSQLModel
from conductor.models.job import Job


class Project(BaseSQLModel):
    """Project table."""

    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    dataset_uri: Mapped[str] = mapped_column()
    workspace_uri: Mapped[str] = mapped_column()
    storage_uri: Mapped[str] = mapped_column()
    img_uri: Mapped[str | None] = mapped_column()
    is_configured: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    parser_type = mapped_column(
        Enum(ParserType, create_constraint=True), nullable=False
    )
    jobs: Mapped[list[Job]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
