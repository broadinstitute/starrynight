"""Project route handlers."""

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    orm_project = Project(**project.model_dump(exclude={"id"}))
    with db_session() as session:
        session.add(orm_project)
        session.commit()
        project = PyProject.model_validate(orm_project)
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
        [TODO:description]

    """
    with db_session() as session:
        projects = session.scalars(select(Project).limit(limit).offset(offset)).all()
        projects = [PyProject.model_validate(project) for project in projects]
    return projects
