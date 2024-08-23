"""Step model test suite."""

import pytest
from conductor.constants import JobType, StepType, job_output_dict
from conductor.models.job import Job
from conductor.models.project import Project
from conductor.models.step import Step
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_create_step(db: Session, sample_project: Project) -> None:
    step = Step(
        name="TestStep",
        description="A test step",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    db.add(step)
    db.commit()
    assert step.id is not None


def test_unique_name(db: Session, sample_project: Project) -> None:
    step1 = Step(
        name="UniqueName",
        description="Description 1",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    db.add(step1)
    db.commit()

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        step2 = Step(
            name="UniqueName",
            description="Description 2",
            type=StepType.CP_ILLUM_CALC,
            project_id=sample_project.id,
        )
        db.add(step2)
        db.commit()


def test_relationship_project(db: Session, sample_project: Project) -> None:
    step = Step(
        name="TestStep",
        description="A test step",
        project_id=sample_project.id,
        type=StepType.CP_ILLUM_CALC,
    )
    db.add(step)
    db.commit()

    assert step.project.name == sample_project.name


def test_relationship_with_job(db: Session, sample_project: Project) -> None:
    step = Step(
        name="JobStep",
        description="A step with job",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    job = Job(
        name="TestJob",
        description="Test Job",
        outputs=job_output_dict[JobType.GEN_LOADDATA],
        inputs={},
        type=JobType.GEN_LOADDATA,
        step_id=step.id,
    )
    step.jobs.append(job)
    db.add(step)
    db.commit()
    db.refresh(step)
    db.refresh(job)
    assert len(step.jobs) == 1
    assert step.jobs[0].name == "TestJob"


def test_relationship_with_depends_on(db: Session, sample_project: Project) -> None:
    step1 = Step(
        name="Step1DependsOn",
        description="Step 1",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    step2 = Step(
        name="Step2DependsOn",
        description="Step 2",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    step1.depends_on.append(step2)
    db.add(step1)
    db.add(step2)
    db.commit()
    db.refresh(step1)
    db.refresh(step2)
    assert len(step1.depends_on) == 1
    assert step1.depends_on[0].name == "Step2DependsOn"
    assert step2.required_by[0].name == "Step1DependsOn"


def test_relationship_with_required_by(db: Session, sample_project: Project) -> None:
    step1 = Step(
        name="Step1RequiredBy",
        description="Step 1",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    step2 = Step(
        name="Step2RequiredBy",
        description="Step 2",
        type=StepType.CP_ILLUM_CALC,
        project_id=sample_project.id,
    )
    step2.required_by.append(step1)
    db.add(step1)
    db.add(step2)
    db.commit()
    db.refresh(step1)
    db.refresh(step2)
    assert len(step2.required_by) == 1
    assert step2.required_by[0].name == "Step1RequiredBy"
    assert step1.depends_on[0].name == "Step2RequiredBy"


def test_invalid_type(db: Session, sample_project: Project) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        step = Step(
            name="TestStep",
            description="TestStep",
            project_id=sample_project.id,
            type="InvalidType",
        )
        db.add(step)
        db.commit()


def test_invalid_project(db: Session) -> None:
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        step = Step(
            name="TestStep",
            description="TestStep",
            project_id=290348,
            type=StepType.CP_ILLUM_CALC,
        )
        db.add(step)
        db.commit()
