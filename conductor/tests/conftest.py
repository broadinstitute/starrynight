"""Test configurations."""

from collections.abc import Generator

import pytest
from conductor.constants import (
    JobType,
    ParserType,
    ProjectType,
    StepType,
    job_output_dict,
)
from conductor.models.base import BaseSQLModel
from conductor.models.job import Job
from conductor.models.project import Project
from conductor.models.step import Step
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = (
    "sqlite+pysqlite:///:memory:"  # Use an in-memory SQLite database for testing
)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Db session fixture.

    Generator[Session, None, None]
        Db session.

    """
    if "sqlite" in DATABASE_URL:
        event.listen(
            Engine, "connect", lambda c, _: c.execute("pragma foreign_keys=on")
        )
    engine = create_engine(DATABASE_URL, echo=True)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    BaseSQLModel.metadata.create_all(bind=engine)
    session = session_local()
    yield session
    session.close()


@pytest.fixture(scope="function")
def sample_project(db: Session) -> Project:
    project = Project(
        name="test-project",
        dataset_uri="s3://test-project",
        workspace_uri="test-uri/workspace",
        description="This is a test project",
        type=ProjectType.OPS_GENERIC,
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project)
    db.commit()
    return project


@pytest.fixture(scope="function")
def sample_step(db: Session, sample_project: Project) -> Step:
    step = Step(
        name="test-step",
        description="This is a test step",
        project_id=sample_project.id,
        type=StepType.CP_ILLUM_CALC,
    )
    db.add(step)
    db.commit()
    return step


@pytest.fixture(scope="function")
def sample_job(db: Session, sample_step: Step) -> Job:
    job = Job(
        name="test-job",
        description="This is a test job",
        step_id=sample_step.id,
        type=JobType.GEN_LOADDATA,
        inputs={},
        outputs=job_output_dict[JobType.GEN_LOADDATA],
    )
    db.add(job)
    db.commit()
    return job
