"""Project route handlers."""

import json
from collections.abc import Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starrynight.experiments.registry import EXPERIMENT_REGISTRY
from starrynight.modules.common import SpecContainer

from conductor.constants import ExecutorType, ParserType
from conductor.handlers.execute import submit_project
from conductor.handlers.job import (
    create_indexing_jobs_for_project,
    create_pipeline_jobs_for_project,
)
from conductor.models.job import Job
from conductor.models.project import Project
from conductor.models.run import Run
from conductor.validators.project import Project as PyProject
from conductor.validators.run import Run as PyRun


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
    orm_jobs = create_indexing_jobs_for_project(orm_object)
    orm_object.jobs = orm_jobs
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        project = PyProject.model_validate(orm_object)
    return project


def update_project(db_session: Callable[[], Session], project: PyProject) -> PyProject:
    """Update project.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    project : PyProject
        Project instance.

    Returns
    -------
    PyProject
        Updated project.

    """
    orm_object = Project(**project.model_dump())
    with db_session() as session:
        session.merge(orm_object)
        session.commit()
        project = PyProject.model_validate(orm_object)
    return project


def configure_project(db_session: Callable[[], Session], project_id: int) -> PyProject:
    """Create project.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    project_id : int
        Project id.

    Returns
    -------
    PyProject
        Created project.

    """
    with db_session() as session:
        orm_project = session.scalar(select(Project).where(Project.id == project_id))
        # extract project index path from project generate_index most recent run object
        orm_job = session.scalar(
            select(Job)
            .where(Job.project_id == project_id)
            .where(Job.uid == "generate_index")
        )
        orm_run = session.scalar(select(Run).where(Run.job_id == orm_job.id))
        index_path = (
            SpecContainer.model_validate(orm_run.spec)
            .outputs["project_index_path"]
            .value
        )
        orm_jobs, experiment = create_pipeline_jobs_for_project(
            orm_project, index_path, orm_project.experiment
        )
        if len(orm_jobs) == 2:
            orm_project.jobs = orm_project.jobs + orm_jobs
        else:
            orm_project.jobs = orm_project.jobs[0:2] + orm_jobs
        orm_project.is_configured = True
        orm_project.experiment = json.loads(experiment.model_dump_json())
        session.add(orm_project)
        session.commit()
        project = PyProject.model_validate(orm_project)
    return project


def delete_project(db_session: Callable[[], Session], project_id: int) -> PyProject:
    """Delete project.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    project_id : int
        Project Id.

    Returns
    -------
    PyProject
        Deleted project.

    """
    with db_session() as session:
        orm_object = session.scalar(select(Project).where(Project.id == project_id))
        project = PyProject.model_validate(orm_object)
        session.delete(orm_object)
        session.commit()
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
    project_types = [key for key, value in EXPERIMENT_REGISTRY.items()]
    return project_types


def fetch_project_details_by_type(project_type: str) -> dict | None:
    """Fetch project details by project type.

    Returns
    -------
    dict | None
        Experiment init spec.

    """
    experiment = EXPERIMENT_REGISTRY.get(project_type, None)
    if experiment is not None:
        experiment = experiment.construct()
        schema = experiment.model_json_schema()
        init_schema = schema["properties"]["init_config_"]["anyOf"][0]["$ref"].split(
            "/"
        )[-1]
        init_schema = schema["$defs"][init_schema]["properties"]
    return init_schema


def fetch_all_parser_types() -> list[str]:
    """Fetch all parser types.

    Returns
    -------
    list[str]
        List of parser types.

    """
    parser_types = [pt.value for pt in ParserType]
    return parser_types


def execute_project(
    db_session: Callable[[], Session],
    project_id: int,
    executor_type: ExecutorType = ExecutorType.LOCAL,
) -> list[PyRun]:
    """Execute job.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    project_id : int
        ID of the project to execute.
    executor_type : ExecutorType
        Type to executor to use.

    Returns
    -------
    list[PyRun]
        list of PyRun

    """
    run_list = submit_project(db_session, project_id, executor_type)
    return run_list
