"""Run model test suite."""

import pytest
from conductor.constants import ExecutorType, RunStatus
from conductor.models.job import Job
from conductor.models.run import Run
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_create_run(db: Session, sample_job: Job) -> None:
    run = Run(
        name="TestRun",
        job_id=sample_job.id,
        run_status=RunStatus.PENDING,
        executor_type=ExecutorType.LOCAL,
        inputs={},
        outputs={},
    )
    db.add(run)
    db.commit()
    assert run.id is not None


def test_unique_name(db: Session, sample_job: Job) -> None:
    run1 = Run(
        name="UniqueName",
        job_id=sample_job.id,
        run_status=RunStatus.PENDING,
        executor_type=ExecutorType.LOCAL,
        inputs={},
        outputs={},
    )
    db.add(run1)
    db.commit()

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        run2 = Run(
            name="UniqueName",
            job_id=sample_job.id,
            run_status=RunStatus.PENDING,
            executor_type=ExecutorType.LOCAL,
            inputs={},
            outputs={},
        )
        db.add(run2)
        db.commit()


def test_relationship_with_job(db: Session, sample_job: Job) -> None:
    run = Run(
        name="TestRun",
        job_id=sample_job.id,
        run_status=RunStatus.PENDING,
        executor_type=ExecutorType.LOCAL,
        inputs={},
        outputs={},
    )
    db.add(run)
    db.commit()
    db.refresh(sample_job)

    assert len(sample_job.runs) == 1
    assert sample_job.runs[0].name == "TestRun"
    assert run.job.name == sample_job.name


def test_invalid_run_status(db: Session, sample_job: Job) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        run = Run(
            name="TestRun",
            job_id=sample_job.id,
            run_status="InvalidStatus",
            inputs={},
            outputs={},
            executor_type=ExecutorType.LOCAL,
        )
        db.add(run)
        db.commit()


def test_invalid_executor_type(db: Session, sample_job: Job) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        run = Run(
            name="TestRun",
            job_id=sample_job.id,
            run_status=RunStatus.PENDING,
            executor_type="InvalidType",
            inputs={},
            outputs={},
        )
        db.add(run)
        db.commit()


def test_invalid_job(db: Session) -> None:
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        run = Run(
            name="TestRun",
            job_id=290348,
            run_status=RunStatus.PENDING,
            executor_type=ExecutorType.LOCAL,
            inputs={},
            outputs={},
        )
        db.add(run)
        db.commit()
