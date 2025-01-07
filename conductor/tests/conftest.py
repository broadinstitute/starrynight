"""Test configurations."""

from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from conductor.constants import (
    ParserType,
    ProjectType,
)
from conductor.models.base import BaseSQLModel
from conductor.models.job import Job
from conductor.models.project import Project

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
        storage_uri="test-uri/workspace",
        description="This is a test project",
        type="randomproject",
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project)
    db.commit()
    return project


@pytest.fixture(scope="function")
def sample_job(db: Session, sample_project: Project) -> Job:
    job = Job(
        name="test-job",
        uid="Unique module name",
        description="This is a test job",
        project_id=sample_project.id,
        spec={},
        inputs={},
        outputs={},
    )
    db.add(job)
    db.commit()
    return job
