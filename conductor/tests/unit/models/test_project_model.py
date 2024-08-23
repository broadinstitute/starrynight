"""Project model test suite."""

import pytest
from conductor.constants import ParserType, ProjectType, StepType
from conductor.models.project import Project
from conductor.models.step import Step
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_create_project(db: Session) -> None:
    project = Project(
        name="TestProject",
        dataset_uri="test-uri",
        description="A test project",
        type=ProjectType.OPS_GENERIC,
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project)
    db.commit()
    assert project.id is not None


def test_unique_name(db: Session) -> None:
    project1 = Project(
        name="UniqueName",
        dataset_uri="test-uri-1",
        description="A test project 1",
        type=ProjectType.OPS_GENERIC,
        parser_type=ParserType.OPS_VINCENT,
    )
    db.add(project1)
    db.commit()

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        project2 = Project(
            name="UniqueName",
            dataset_uri="test-uri-2",
            description="A test project 2",
            type=ProjectType.OPS_GENERIC,
            parser_type=ParserType.OPS_VINCENT,
        )
        db.add(project2)
        db.commit()


def test_relationship_steps(db: Session) -> None:
    project = Project(
        name="TestProject",
        dataset_uri="test-uri",
        description="A test project",
        type=ProjectType.OPS_GENERIC,
        parser_type=ParserType.OPS_VINCENT,
    )
    step1 = Step(
        name="Step 1",
        description="A step 1",
        type=StepType.CP_ILLUM_CALC,
    )
    step2 = Step(
        name="Step 2",
        description="A step 2",
        type=StepType.CP_ILLUM_CALC,
    )

    project.steps.append(step1)
    project.steps.append(step2)

    db.add(project)
    db.commit()
    db.refresh(project)

    assert len(project.steps) == 2


def test_invalid_type(db: Session) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        project = Project(
            name="TestProject",
            dataset_uri="test-uri",
            description="A test project",
            type="InvalidType",
            parser_type=ParserType.OPS_VINCENT,
        )
        db.add(project)
        db.commit()


def test_invalid_parser_type(db: Session) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        project = Project(
            name="TestProject",
            dataset_uri="test-uri",
            description="A test project",
            type=ProjectType.OPS_GENERIC,
            parser_type="InvalidParserType",
        )
        db.add(project)
        db.commit()
