"""Project model test suite."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from conductor.constants import ParserType, ProjectType, StepType
from conductor.models.job import Job
from conductor.models.project import Project


def test_create_project(db: Session) -> None:
    project = Project(
        name="TestProject",
        dataset_uri="test-uri",
        workspace_uri="test-uri/workspace",
        storage_uri="test-uri/storage",
        description="A test project",
        type="randomproject",
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project)
    db.commit()
    assert project.id is not None


def test_unique_name(db: Session) -> None:
    project1 = Project(
        name="UniqueName",
        dataset_uri="test-uri-1",
        workspace_uri="test-uri/workspace",
        description="A test project 1",
        storage_uri="test-uri/storage",
        type="randomproject",
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project1)
    db.commit()

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        project2 = Project(
            name="UniqueName",
            dataset_uri="test-uri-2",
            workspace_uri="test-uri/workspace",
            storage_uri="test-uri/storage",
            description="A test project 2",
            type="randomproject",
            parser_type=ParserType.OPS_VINCENT,
        )
        db.add(project2)
        db.commit()


def test_relationship_jobs(db: Session) -> None:
    project = Project(
        name="TestProject",
        dataset_uri="test-uri",
        workspace_uri="test-uri/workspace",
        storage_uri="test-uri/storage",
        description="A test project",
        type="OPS GENERIC",
        parser_type=ParserType.OPS_VINCENT,
    )
    job1 = Job(
        name="test-job1",
        uid="Unique module name",
        description="This is a test job",
        spec={},
        inputs={},
        outputs={},
    )
    job2 = Job(
        name="Job 2",
        description="A step 2",
        uid="Unique module name",
        spec={},
        inputs={},
        outputs={},
    )

    project.jobs.append(job1)
    project.jobs.append(job2)

    db.add(project)
    db.commit()
    db.refresh(project)

    assert len(project.jobs) == 2


def test_invalid_parser_type(db: Session) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        project = Project(
            name="TestProject",
            dataset_uri="test-uri",
            workspace_uri="test-uri/workspace",
            storage_uri="test-uri/storage",
            description="A test project",
            type="randomproject",
            parser_type="InvalidParserType",
        )
        db.add(project)
        db.commit()
