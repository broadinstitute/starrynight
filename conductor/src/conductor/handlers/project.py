"""Project route handlers."""

from collections.abc import Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from conductor.constants import ParserType, ProjectType
from conductor.handlers.step import create_steps_for_project
from conductor.models.project import Project
from conductor.validators.project import Project as PyProject


def create_project(db_session: Callable[[], Session], project: PyProject) -> PyProject:
    """Create project.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    project : PyProject
        Project instance.

    Returns
    -------
    PyProject
        Created project.

    """
    orm_object = Project(**project.model_dump(exclude={"id"}))
    orm_steps = create_steps_for_project(orm_object.type)
    orm_object.steps = orm_steps
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        project = PyProject.model_validate(orm_object)
    return project


def fetch_all_projects(
    db_session: Callable[[], Session], limit: int = 10, offset: int = 0
) -> list[PyProject]:
    """Fetch all projects.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    limit: int
        Number of results to return.
    offset: int
        Offset value to use for fetch.

    Returns
    -------
    list[PyProject]
        List of projects.

    """
    with db_session() as session:
        projects = session.scalars(select(Project).limit(limit).offset(offset)).all()
        projects = [PyProject.model_validate(project) for project in projects]
    return projects


def fetch_project_by_id(
    db_session: Callable[[], Session], project_id: int
) -> PyProject:
    """Fetch all projects.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    project_id: int
        Project id to use as filter.

    Returns
    -------
    PyProject
        Pyproject instance.

    """
    with db_session() as session:
        project = session.scalar(select(Project).where(Project.id == project_id))
        project = PyProject.model_validate(project)
    return project


def fetch_project_count(db_session: Callable[[], Session]) -> int:
    """Fetch project count.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.

    Returns
    -------
    int
        Project count

    """
    with db_session() as session:
        count = session.scalar(select(func.count()).select_from(Project))
        assert type(count) is int
    return count


def fetch_all_project_types() -> list[str]:
    """Fetch all project types.

    Returns
    -------
    list[str]
        List of project types.

    """
    project_types = [pt.value for pt in ProjectType]
    return project_types


def fetch_all_parser_types() -> list[str]:
    """Fetch all parser types.

    Returns
    -------
    list[str]
        List of parser types.

    """
    parser_types = [pt.value for pt in ParserType]
    return parser_types
